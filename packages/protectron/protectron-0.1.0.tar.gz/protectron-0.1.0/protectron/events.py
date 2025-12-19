"""Event types and builders for audit logging."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from protectron.utils.ids import generate_event_id, generate_span_id


class EventType(str, Enum):
    """Supported event types for EU AI Act compliance."""

    AGENT_INVOKED = "agent_invoked"
    AGENT_COMPLETED = "agent_completed"
    AGENT_STOPPED = "agent_stopped"
    ACTION_STARTED = "action_started"
    ACTION_COMPLETED = "action_completed"
    DECISION_MADE = "decision"
    TOOL_CALL = "tool_call"
    LLM_CALL = "llm_call"
    HUMAN_OVERRIDE = "human_override"
    ESCALATION = "escalation"
    HITL_REQUESTED = "hitl_requested"
    HITL_APPROVED = "hitl_approved"
    HITL_REJECTED = "hitl_rejected"
    HITL_TIMEOUT = "hitl_timeout"
    AGENT_DELEGATION = "agent_delegation"
    ERROR = "error"


class EventStatus(str, Enum):
    """Event outcome status."""

    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    CANCELLED = "cancelled"


@dataclass
class Event:
    """
    Audit event following OpenTelemetry semantic conventions.

    Attributes align with the EU AI Act Article 12 requirements for
    automatic recording of events.
    """

    # Required
    event_type: EventType
    agent_id: str

    # Auto-generated
    event_id: str = field(default_factory=generate_event_id)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    span_id: str = field(default_factory=generate_span_id)

    # Tracing
    trace_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    session_id: Optional[str] = None

    # Event details
    event_name: Optional[str] = None
    status: EventStatus = EventStatus.SUCCESS

    # Content
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None

    # Decision-specific
    decision: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    alternatives: Optional[List[str]] = None

    # Tool-specific
    tool_name: Optional[str] = None

    # LLM-specific
    model: Optional[str] = None
    provider: Optional[str] = None
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None

    # Performance
    duration_ms: Optional[int] = None

    # Human oversight
    override_by: Optional[str] = None
    override_reason: Optional[str] = None

    # Multi-agent
    delegated_to_agent: Optional[str] = None
    delegated_from_agent: Optional[str] = None

    # Error
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    environment: str = "production"
    sdk_version: str = "0.1.0"
    _pii_redacted: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        """Validate event after initialization."""
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.duration_ms is not None and self.duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        if self.tokens_input is not None and self.tokens_input < 0:
            raise ValueError("tokens_input must be non-negative")
        if self.tokens_output is not None and self.tokens_output < 0:
            raise ValueError("tokens_output must be non-negative")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API payload format."""
        data: Dict[str, Any] = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "span_id": self.span_id,
            "status": self.status.value,
        }

        # Optional tracing fields
        if self.trace_id:
            data["trace_id"] = self.trace_id
        if self.parent_span_id:
            data["parent_span_id"] = self.parent_span_id
        if self.session_id:
            data["session_id"] = self.session_id
        if self.event_name:
            data["event_name"] = self.event_name

        # Attributes (OpenTelemetry style)
        attributes: Dict[str, Any] = {"gen_ai.agent.id": self.agent_id}
        if self.event_name:
            attributes["gen_ai.operation.name"] = self.event_name
        if self.tool_name:
            attributes["gen_ai.tool.name"] = self.tool_name
        if self.model:
            attributes["gen_ai.request.model"] = self.model
        if self.provider:
            attributes["gen_ai.provider.name"] = self.provider
        if self.tokens_input is not None:
            attributes["gen_ai.usage.input_tokens"] = self.tokens_input
        if self.tokens_output is not None:
            attributes["gen_ai.usage.output_tokens"] = self.tokens_output
        data["attributes"] = attributes

        # Context
        context: Dict[str, Any] = {}
        if self.input_data:
            context["input"] = self.input_data
        if self.output_data:
            context["output"] = self.output_data
        if self.decision:
            context["decision"] = self.decision
        if self.confidence is not None:
            context["confidence"] = self.confidence
        if self.reasoning:
            context["reasoning"] = self.reasoning
        if self.alternatives:
            context["alternatives_considered"] = self.alternatives
        if context:
            data["context"] = context

        # Duration
        if self.duration_ms is not None:
            data["duration_ms"] = self.duration_ms

        # Error
        if self.error_type:
            data["error"] = {
                "type": self.error_type,
                "message": self.error_message,
            }
            if self.stack_trace:
                data["error"]["stack_trace"] = self.stack_trace

        # Override
        if self.override_by:
            data["override"] = {
                "by": self.override_by,
                "reason": self.override_reason,
            }

        # Delegation
        if self.delegated_to_agent:
            data["delegation"] = {
                "to_agent": self.delegated_to_agent,
                "from_agent": self.delegated_from_agent,
            }

        # Metadata
        data["metadata"] = {
            **self.metadata,
            "environment": self.environment,
            "sdk_version": self.sdk_version,
            "pii_redacted": self._pii_redacted,
        }

        return data

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create Event from dictionary."""
        event_type = data.get("event_type")
        if isinstance(event_type, str):
            event_type = EventType(event_type)

        status = data.get("status", "success")
        if isinstance(status, str):
            status = EventStatus(status)

        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        context = data.get("context", {})
        attributes = data.get("attributes", {})
        error = data.get("error", {})
        metadata = data.get("metadata", {})
        override = data.get("override", {})
        delegation = data.get("delegation", {})

        return cls(
            event_type=event_type,
            agent_id=data["agent_id"],
            event_id=data.get("event_id", generate_event_id()),
            timestamp=timestamp or datetime.now(timezone.utc),
            span_id=data.get("span_id", generate_span_id()),
            trace_id=data.get("trace_id"),
            parent_span_id=data.get("parent_span_id"),
            session_id=data.get("session_id"),
            event_name=data.get("event_name"),
            status=status,
            input_data=context.get("input"),
            output_data=context.get("output"),
            decision=context.get("decision"),
            confidence=context.get("confidence"),
            reasoning=context.get("reasoning"),
            alternatives=context.get("alternatives_considered"),
            tool_name=attributes.get("gen_ai.tool.name"),
            model=attributes.get("gen_ai.request.model"),
            provider=attributes.get("gen_ai.provider.name"),
            tokens_input=attributes.get("gen_ai.usage.input_tokens"),
            tokens_output=attributes.get("gen_ai.usage.output_tokens"),
            duration_ms=data.get("duration_ms"),
            override_by=override.get("by"),
            override_reason=override.get("reason"),
            delegated_to_agent=delegation.get("to_agent"),
            delegated_from_agent=delegation.get("from_agent"),
            error_type=error.get("type"),
            error_message=error.get("message"),
            stack_trace=error.get("stack_trace"),
            metadata={
                k: v
                for k, v in metadata.items()
                if k not in ("environment", "sdk_version", "pii_redacted")
            },
            environment=metadata.get("environment", "production"),
            sdk_version=metadata.get("sdk_version", "0.1.0"),
            _pii_redacted=metadata.get("pii_redacted", False),
        )


class EventBuilder:
    """Fluent builder for creating events."""

    def __init__(self, event_type: EventType, agent_id: str):
        self._event_type = event_type
        self._agent_id = agent_id
        self._kwargs: Dict[str, Any] = {}

    def with_name(self, name: str) -> "EventBuilder":
        """Set event name."""
        self._kwargs["event_name"] = name
        return self

    def with_trace(
        self, trace_id: str, parent_span_id: Optional[str] = None
    ) -> "EventBuilder":
        """Set trace context."""
        self._kwargs["trace_id"] = trace_id
        if parent_span_id:
            self._kwargs["parent_span_id"] = parent_span_id
        return self

    def with_session(self, session_id: str) -> "EventBuilder":
        """Set session ID."""
        self._kwargs["session_id"] = session_id
        return self

    def with_input(self, data: Dict[str, Any]) -> "EventBuilder":
        """Set input data."""
        self._kwargs["input_data"] = data
        return self

    def with_output(self, data: Dict[str, Any]) -> "EventBuilder":
        """Set output data."""
        self._kwargs["output_data"] = data
        return self

    def with_decision(
        self,
        decision: str,
        confidence: float,
        reasoning: str,
        alternatives: Optional[List[str]] = None,
    ) -> "EventBuilder":
        """Set decision details."""
        self._kwargs["decision"] = decision
        self._kwargs["confidence"] = confidence
        self._kwargs["reasoning"] = reasoning
        if alternatives:
            self._kwargs["alternatives"] = alternatives
        return self

    def with_tool(self, name: str) -> "EventBuilder":
        """Set tool name."""
        self._kwargs["tool_name"] = name
        return self

    def with_llm(
        self,
        model: str,
        provider: str,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
    ) -> "EventBuilder":
        """Set LLM details."""
        self._kwargs["model"] = model
        self._kwargs["provider"] = provider
        if tokens_in is not None:
            self._kwargs["tokens_input"] = tokens_in
        if tokens_out is not None:
            self._kwargs["tokens_output"] = tokens_out
        return self

    def with_duration(self, ms: int) -> "EventBuilder":
        """Set duration in milliseconds."""
        self._kwargs["duration_ms"] = ms
        return self

    def with_status(self, status: EventStatus) -> "EventBuilder":
        """Set event status."""
        self._kwargs["status"] = status
        return self

    def with_error(
        self,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
    ) -> "EventBuilder":
        """Set error details."""
        self._kwargs["status"] = EventStatus.FAILURE
        self._kwargs["error_type"] = error_type
        self._kwargs["error_message"] = message
        if stack_trace:
            self._kwargs["stack_trace"] = stack_trace
        return self

    def with_override(self, by: str, reason: str) -> "EventBuilder":
        """Set human override details."""
        self._kwargs["override_by"] = by
        self._kwargs["override_reason"] = reason
        return self

    def with_delegation(
        self, to_agent: str, from_agent: Optional[str] = None
    ) -> "EventBuilder":
        """Set delegation details."""
        self._kwargs["delegated_to_agent"] = to_agent
        if from_agent:
            self._kwargs["delegated_from_agent"] = from_agent
        return self

    def with_metadata(self, **kwargs: Any) -> "EventBuilder":
        """Add metadata."""
        self._kwargs.setdefault("metadata", {}).update(kwargs)
        return self

    def with_environment(self, environment: str) -> "EventBuilder":
        """Set environment."""
        self._kwargs["environment"] = environment
        return self

    def build(self) -> Event:
        """Build the event."""
        return Event(
            event_type=self._event_type,
            agent_id=self._agent_id,
            **self._kwargs,
        )
