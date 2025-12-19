"""Main Protectron SDK client."""

import atexit
import logging
import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from protectron.buffer import EventBuffer
from protectron.config import ProtectronConfig
from protectron.context import TraceContext, get_current_context, set_current_context
from protectron.events import Event, EventStatus, EventType
from protectron.exceptions import AgentStoppedError, TransportError
from protectron.hitl import HITLClient, HITLResponse
from protectron.transport import Transport
from protectron.utils.ids import generate_session_id, generate_trace_id
from protectron.utils.pii import PIIRedactor

logger = logging.getLogger("protectron")


class ProtectronAgent:
    """
    Main SDK client for EU AI Act compliant audit logging.

    Example:
        ```python
        from protectron import ProtectronAgent

        agent = ProtectronAgent(
            api_key="pk_live_xxxx",
            agent_id="agt_xxxx"
        )

        # Log events
        agent.log_action("process_refund", status="completed", details={"amount": 100})

        # With HITL
        if agent.check_hitl("process_refund", {"amount": 500}):
            approval = agent.request_approval("process_refund", {"amount": 500})
            if approval.approved:
                # proceed
                pass

        # Always flush on shutdown
        agent.close()
        ```
    """

    VERSION = "0.1.0"

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        *,
        base_url: str = "https://api.protectron.ai",
        environment: str = "production",
        buffer_size: int = 1000,
        flush_interval: float = 5.0,
        batch_size: int = 100,
        retry_attempts: int = 3,
        pii_redaction: bool = True,
        debug: bool = False,
        persist_path: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Initialize the Protectron SDK client.

        Args:
            api_key: Your Protectron API key (pk_live_xxx or pk_test_xxx)
            agent_id: Your agent ID (agt_xxx)
            base_url: API base URL (default: https://api.protectron.ai)
            environment: Environment name (production/staging/development)
            buffer_size: Max events to buffer when offline
            flush_interval: Seconds between automatic flushes
            batch_size: Events per batch request
            retry_attempts: Retries before buffering
            pii_redaction: Enable automatic PII redaction
            debug: Enable debug logging
            persist_path: Path for buffer persistence (optional)
        """
        self.config = ProtectronConfig(
            api_key=api_key,
            agent_id=agent_id,
            base_url=base_url,
            environment=environment,
            buffer_size=buffer_size,
            flush_interval=flush_interval,
            batch_size=batch_size,
            retry_attempts=retry_attempts,
            pii_redaction_enabled=pii_redaction,
            persist_path=persist_path,
            debug=debug,
            **kwargs,
        )

        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

        self._transport = Transport(self.config)
        self._buffer = EventBuffer(
            max_size=buffer_size,
            persist_path=persist_path,
        )
        self._hitl = HITLClient(self._transport, agent_id)
        self._pii_redactor = PIIRedactor() if pii_redaction else None

        self._agent_id = agent_id
        self._environment = environment
        self._session_id: Optional[str] = None
        self._stopped = False
        self._closed = False

        self._flush_thread: Optional[threading.Thread] = None
        self._flush_stop_event = threading.Event()
        self._start_flush_thread()

        atexit.register(self.close)

        logger.info(f"Protectron SDK initialized for agent {agent_id}")

    # =========================================================================
    # Session Management
    # =========================================================================

    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new session and return the session ID.

        Args:
            session_id: Optional custom session ID

        Returns:
            The session ID
        """
        self._session_id = session_id or generate_session_id()
        logger.debug(f"Started session: {self._session_id}")
        return self._session_id

    def end_session(self) -> None:
        """End the current session and flush events."""
        if self._session_id:
            self.flush()
            logger.debug(f"Ended session: {self._session_id}")
            self._session_id = None

    @property
    def session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self._session_id

    # =========================================================================
    # Tracing Context
    # =========================================================================

    @contextmanager
    def trace(
        self,
        name: str,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator[TraceContext, None, None]:
        """
        Context manager for tracing a complete agent invocation.

        All events logged within this context will share the same trace_id.

        Example:
            ```python
            with agent.trace("handle_customer_request") as ctx:
                agent.log_tool_call("search_database", ...)
                agent.log_decision("approve_refund", ...)
            ```

        Args:
            name: Name of the trace
            trace_id: Optional custom trace ID
            metadata: Optional metadata for the trace

        Yields:
            TraceContext for this trace
        """
        ctx = TraceContext(
            trace_id=trace_id or generate_trace_id(),
            name=name,
            agent_id=self._agent_id,
            session_id=self._session_id,
        )

        self._log_event(
            EventType.AGENT_INVOKED,
            event_name=name,
            trace_id=ctx.trace_id,
            metadata=metadata or {},
        )

        start_time = time.time()
        token = set_current_context(ctx)
        error: Optional[Exception] = None

        try:
            yield ctx
            status = EventStatus.SUCCESS
        except Exception as e:
            status = EventStatus.FAILURE
            error = e
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)

            self._log_event(
                EventType.AGENT_COMPLETED,
                event_name=name,
                trace_id=ctx.trace_id,
                status=status,
                duration_ms=duration_ms,
                error_type=type(error).__name__ if error else None,
                error_message=str(error) if error else None,
            )

            set_current_context(token)  # type: ignore[arg-type]

    # =========================================================================
    # Logging Methods
    # =========================================================================

    def log_action(
        self,
        action: str,
        *,
        status: str = "completed",
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log an action taken by the agent.

        Args:
            action: Name of the action (e.g., "process_refund")
            status: Outcome status ("completed", "failed", "pending")
            details: Action-specific details
            duration_ms: How long the action took
            tokens_used: Tokens consumed (if applicable)
            metadata: Additional metadata

        Returns:
            The event ID
        """
        self._check_not_stopped()

        event_status = {
            "completed": EventStatus.SUCCESS,
            "failed": EventStatus.FAILURE,
            "pending": EventStatus.PENDING,
            "started": EventStatus.PENDING,
        }.get(status, EventStatus.SUCCESS)

        return self._log_event(
            EventType.ACTION_COMPLETED,
            event_name=action,
            status=event_status,
            output_data=details,
            duration_ms=duration_ms,
            tokens_output=tokens_used,
            metadata=metadata or {},
        )

    def log_decision(
        self,
        decision: str,
        *,
        confidence: float,
        reasoning: str,
        alternatives: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log a decision made by the agent.

        This is critical for Article 12 compliance - decisions must be
        traceable with their reasoning.

        Args:
            decision: The decision made (e.g., "escalate_to_human")
            confidence: Confidence score (0.0 to 1.0)
            reasoning: Explanation of why this decision was made
            alternatives: Other options that were considered
            context: Input context that led to this decision
            metadata: Additional metadata

        Returns:
            The event ID
        """
        self._check_not_stopped()

        return self._log_event(
            EventType.DECISION_MADE,
            event_name=decision,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            input_data=context,
            metadata=metadata or {},
        )

    def log_tool_call(
        self,
        tool_name: str,
        *,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log a tool/API call made by the agent.

        Args:
            tool_name: Name of the tool (e.g., "search_database")
            input_data: Input parameters
            output_data: Output/response data
            duration_ms: Call duration
            success: Whether the call succeeded
            error: Error message if failed
            metadata: Additional metadata

        Returns:
            The event ID
        """
        self._check_not_stopped()

        return self._log_event(
            EventType.TOOL_CALL,
            event_name=tool_name,
            tool_name=tool_name,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            status=EventStatus.SUCCESS if success else EventStatus.FAILURE,
            error_message=error,
            metadata=metadata or {},
        )

    def log_llm_call(
        self,
        model: str,
        provider: str,
        *,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log an LLM API call.

        Args:
            model: Model name (e.g., "gpt-4")
            provider: Provider name (e.g., "openai")
            prompt: Input prompt (will be redacted if PII detected)
            response: Model response
            tokens_input: Input tokens
            tokens_output: Output tokens
            duration_ms: Call duration
            metadata: Additional metadata

        Returns:
            The event ID
        """
        self._check_not_stopped()

        return self._log_event(
            EventType.LLM_CALL,
            event_name=f"{provider}/{model}",
            model=model,
            provider=provider,
            input_data={"prompt": prompt} if prompt else None,
            output_data={"response": response} if response else None,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

    def log_error(
        self,
        error_type: str,
        message: str,
        *,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log an error that occurred.

        Args:
            error_type: Exception type name
            message: Error message
            stack_trace: Full stack trace
            context: Context when error occurred
            metadata: Additional metadata

        Returns:
            The event ID
        """
        return self._log_event(
            EventType.ERROR,
            event_name=error_type,
            status=EventStatus.FAILURE,
            error_type=error_type,
            error_message=message,
            stack_trace=stack_trace,
            input_data=context,
            metadata=metadata or {},
        )

    def log_delegation(
        self,
        to_agent_id: str,
        task: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log delegation to another agent (for multi-agent systems).

        Args:
            to_agent_id: ID of the agent being delegated to
            task: Description of the delegated task
            context: Context being passed
            metadata: Additional metadata

        Returns:
            The event ID
        """
        self._check_not_stopped()

        return self._log_event(
            EventType.AGENT_DELEGATION,
            event_name=task,
            delegated_to_agent=to_agent_id,
            delegated_from_agent=self._agent_id,
            input_data=context,
            metadata=metadata or {},
        )

    def log_human_override(
        self,
        action: str,
        original_decision: str,
        override_decision: str,
        *,
        reviewer: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log when a human overrides an agent decision.

        Args:
            action: The action that was overridden
            original_decision: What the agent decided
            override_decision: What the human decided
            reviewer: Email/ID of the reviewer
            reason: Explanation for the override
            metadata: Additional metadata

        Returns:
            The event ID
        """
        return self._log_event(
            EventType.HUMAN_OVERRIDE,
            event_name=action,
            decision=override_decision,
            reasoning=reason,
            override_by=reviewer,
            override_reason=reason,
            input_data={"original_decision": original_decision},
            metadata=metadata or {},
        )

    # =========================================================================
    # Human-in-the-Loop (HITL)
    # =========================================================================

    def check_hitl(self, action: str, context: Dict[str, Any]) -> bool:
        """
        Check if an action requires human approval.

        Args:
            action: The action name
            context: Action context (used to evaluate rules)

        Returns:
            True if human approval is required
        """
        self._check_not_stopped()
        return self._hitl.check_required(action, context)

    def request_approval(
        self,
        action: str,
        context: Dict[str, Any],
        *,
        timeout_seconds: int = 3600,
        block: bool = True,
    ) -> HITLResponse:
        """
        Request human approval for an action.

        Args:
            action: The action requiring approval
            context: Full context for the reviewer
            timeout_seconds: How long to wait for approval
            block: If True, wait for response; if False, return immediately

        Returns:
            HITLResponse with approval status

        Raises:
            HITLTimeoutError: If approval times out
        """
        self._check_not_stopped()

        self._log_event(
            EventType.HITL_REQUESTED,
            event_name=action,
            input_data=context,
        )

        response = self._hitl.request_approval(
            action=action,
            context=context,
            timeout_seconds=timeout_seconds,
            block=block,
        )

        if response.status == "approved":
            self._log_event(
                EventType.HITL_APPROVED,
                event_name=action,
                override_by=response.reviewer,
                override_reason=response.reason,
            )
        elif response.status == "rejected":
            self._log_event(
                EventType.HITL_REJECTED,
                event_name=action,
                override_by=response.reviewer,
                override_reason=response.reason,
            )
        elif response.status == "timeout":
            self._log_event(
                EventType.HITL_TIMEOUT,
                event_name=action,
            )

        return response

    # =========================================================================
    # Agent Status
    # =========================================================================

    def is_stopped(self) -> bool:
        """
        Check if the agent has been emergency stopped.

        Call this periodically to respect emergency stop commands.

        Returns:
            True if agent should stop operations
        """
        if self._stopped:
            return True

        try:
            status = self._transport.get_agent_status()
            if status.get("lifecycle_status") in ("paused", "archived", "stopped"):
                self._stopped = True
                logger.warning("Agent has been stopped by platform")
                return True
            return False
        except TransportError as e:
            logger.warning(f"Failed to check agent status: {e}")
            return False

    def _check_not_stopped(self) -> None:
        """Raise if agent is stopped."""
        if self._stopped:
            raise AgentStoppedError(
                "Agent has been stopped. No further actions allowed."
            )

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def flush(self) -> int:
        """
        Flush all buffered events to the server.

        Returns:
            Number of events flushed
        """
        if self._closed:
            return 0

        total_flushed = 0
        events = self._buffer.get_batch(self.config.batch_size)

        while events:
            try:
                self._transport.send_batch(events)
                total_flushed += len(events)
                events = self._buffer.get_batch(self.config.batch_size)
            except TransportError as e:
                logger.error(f"Failed to flush events: {e}")
                self._buffer.return_batch(events)
                break

        if total_flushed > 0:
            logger.debug(f"Flushed {total_flushed} events")

        return total_flushed

    def close(self) -> None:
        """
        Gracefully shutdown the SDK.

        - Stops the background flush thread
        - Flushes remaining events
        - Persists buffer to disk if configured
        - Closes connections
        """
        if self._closed:
            return

        logger.info("Shutting down Protectron SDK...")

        self._flush_stop_event.set()
        if self._flush_thread and self._flush_thread.is_alive():
            self._flush_thread.join(timeout=5.0)

        self.flush()

        if self.config.persist_path:
            self._buffer.persist_to_disk()

        self._transport.close()

        self._closed = True
        logger.info("Protectron SDK shutdown complete")

    def buffer_stats(self) -> Dict[str, object]:
        """Get buffer statistics."""
        return self._buffer.stats()

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _log_event(self, event_type: EventType, **kwargs: Any) -> str:
        """Internal method to create and queue an event."""
        ctx = get_current_context()

        # Handle trace_id - ctx could be None or a TraceContext
        trace_id = kwargs.pop("trace_id", None)
        if trace_id is None and ctx is not None and hasattr(ctx, "trace_id"):
            trace_id = ctx.trace_id

        parent_span_id = None
        if ctx is not None and hasattr(ctx, "current_span_id"):
            parent_span_id = ctx.current_span_id

        event = Event(
            event_type=event_type,
            agent_id=self._agent_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            session_id=self._session_id,
            environment=self._environment,
            sdk_version=self.VERSION,
            **kwargs,
        )

        if self._pii_redactor:
            event = self._pii_redactor.redact_event(event)

        self._buffer.add(event)

        logger.debug(f"Logged event: {event.event_id} ({event_type.value})")
        return event.event_id

    def _start_flush_thread(self) -> None:
        """Start background thread for periodic flushing."""

        def flush_loop() -> None:
            while not self._flush_stop_event.wait(self.config.flush_interval):
                try:
                    self.flush()
                except Exception as e:
                    logger.error(f"Background flush error: {e}")

        self._flush_thread = threading.Thread(
            target=flush_loop,
            name="protectron-flush",
            daemon=True,
        )
        self._flush_thread.start()

    # =========================================================================
    # Context Manager Support
    # =========================================================================

    def __enter__(self) -> "ProtectronAgent":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return (
            f"ProtectronAgent(agent_id={self._agent_id!r}, "
            f"environment={self._environment!r})"
        )
