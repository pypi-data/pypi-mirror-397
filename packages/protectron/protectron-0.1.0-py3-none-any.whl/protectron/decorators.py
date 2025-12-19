"""Decorators for automatic audit logging."""

import functools
import logging
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from protectron.client import ProtectronAgent
from protectron.events import EventStatus

logger = logging.getLogger("protectron.decorators")

F = TypeVar("F", bound=Callable[..., Any])


def trace(
    agent: ProtectronAgent,
    name: Optional[str] = None,
    *,
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator to trace a function execution.

    Creates a trace context around the function, automatically logging
    start and completion events.

    Example:
        ```python
        @trace(protectron, "process_order")
        def process_order(order_id: str):
            # All logging within this function shares the same trace_id
            return {"status": "processed"}
        ```

    Args:
        agent: ProtectronAgent instance
        name: Trace name (defaults to function name)
        metadata: Additional metadata to include

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        trace_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with agent.trace(trace_name, metadata=metadata):
                return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def log_action(
    agent: ProtectronAgent,
    action_name: Optional[str] = None,
    *,
    log_args: bool = False,
    log_result: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator to log function execution as an action.

    Example:
        ```python
        @log_action(protectron, "send_email", log_args=True)
        def send_email(to: str, subject: str):
            # Send email logic
            return {"sent": True}
        ```

    Args:
        agent: ProtectronAgent instance
        action_name: Action name (defaults to function name)
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        metadata: Additional metadata to include

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        name = action_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            details: Dict[str, Any] = {}

            if log_args:
                details["args"] = _safe_repr(args)
                details["kwargs"] = _safe_repr(kwargs)

            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                if log_result:
                    details["result"] = _safe_repr(result)

                agent.log_action(
                    action=name,
                    status="completed",
                    details=details if details else None,
                    duration_ms=duration_ms,
                    metadata=metadata,
                )

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                details["error"] = str(e)

                agent.log_action(
                    action=name,
                    status="failed",
                    details=details,
                    duration_ms=duration_ms,
                    metadata=metadata,
                )

                agent.log_error(
                    error_type=type(e).__name__,
                    message=str(e),
                    stack_trace=traceback.format_exc(),
                )

                raise

        return wrapper  # type: ignore

    return decorator


def log_tool(
    agent: ProtectronAgent,
    tool_name: Optional[str] = None,
    *,
    log_input: bool = True,
    log_output: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator to log function execution as a tool call.

    Example:
        ```python
        @log_tool(protectron, "search_database")
        def search_database(query: str) -> List[dict]:
            # Search logic
            return [{"id": 1, "name": "Result"}]
        ```

    Args:
        agent: ProtectronAgent instance
        tool_name: Tool name (defaults to function name)
        log_input: Whether to log input parameters
        log_output: Whether to log output
        metadata: Additional metadata to include

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        name = tool_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()

            input_data = None
            if log_input:
                input_data = {
                    "args": _safe_repr(args),
                    "kwargs": _safe_repr(kwargs),
                }

            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                output_data = None
                if log_output:
                    output_data = {"result": _safe_repr(result)}

                agent.log_tool_call(
                    tool_name=name,
                    input_data=input_data,
                    output_data=output_data,
                    duration_ms=duration_ms,
                    success=True,
                    metadata=metadata,
                )

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)

                agent.log_tool_call(
                    tool_name=name,
                    input_data=input_data,
                    duration_ms=duration_ms,
                    success=False,
                    error=str(e),
                    metadata=metadata,
                )

                raise

        return wrapper  # type: ignore

    return decorator


def log_decision(
    agent: ProtectronAgent,
    decision_name: Optional[str] = None,
    *,
    confidence_extractor: Optional[Callable[[Any], float]] = None,
    reasoning_extractor: Optional[Callable[[Any], str]] = None,
    alternatives: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator to log function result as a decision.

    The function should return the decision value. Optionally, extractors
    can be provided to get confidence and reasoning from the result.

    Example:
        ```python
        @log_decision(
            protectron,
            "approve_loan",
            confidence_extractor=lambda r: r["confidence"],
            reasoning_extractor=lambda r: r["reasoning"],
        )
        def evaluate_loan(application: dict) -> dict:
            # Evaluation logic
            return {
                "decision": "approve",
                "confidence": 0.95,
                "reasoning": "Good credit score"
            }
        ```

    Args:
        agent: ProtectronAgent instance
        decision_name: Decision name (defaults to function name)
        confidence_extractor: Function to extract confidence from result
        reasoning_extractor: Function to extract reasoning from result
        alternatives: List of alternative decisions considered
        metadata: Additional metadata to include

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        name = decision_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Extract decision details
            decision_value = str(result)
            confidence = 1.0
            reasoning = f"Decision made by {name}"

            if confidence_extractor:
                try:
                    confidence = confidence_extractor(result)
                except Exception:
                    pass

            if reasoning_extractor:
                try:
                    reasoning = reasoning_extractor(result)
                except Exception:
                    pass

            # Handle dict results
            if isinstance(result, dict):
                decision_value = result.get("decision", str(result))
                if not confidence_extractor and "confidence" in result:
                    confidence = result["confidence"]
                if not reasoning_extractor and "reasoning" in result:
                    reasoning = result["reasoning"]

            agent.log_decision(
                decision=decision_value,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=alternatives,
                metadata=metadata,
            )

            return result

        return wrapper  # type: ignore

    return decorator


def require_hitl(
    agent: ProtectronAgent,
    action_name: Optional[str] = None,
    *,
    timeout_seconds: int = 3600,
    on_reject: Optional[Callable[[Any], Any]] = None,
    context_builder: Optional[Callable[..., Dict[str, Any]]] = None,
) -> Callable[[F], F]:
    """
    Decorator that requires HITL approval before executing a function.

    Example:
        ```python
        @require_hitl(protectron, "delete_account", timeout_seconds=300)
        def delete_account(user_id: str):
            # This will only execute if approved
            return {"deleted": True}
        ```

    Args:
        agent: ProtectronAgent instance
        action_name: Action name for approval request
        timeout_seconds: How long to wait for approval
        on_reject: Function to call if rejected (receives original args)
        context_builder: Function to build context from args/kwargs

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        name = action_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build context for approval
            if context_builder:
                context = context_builder(*args, **kwargs)
            else:
                context = {
                    "function": func.__name__,
                    "args": _safe_repr(args),
                    "kwargs": _safe_repr(kwargs),
                }

            # Check if HITL is required
            if not agent.check_hitl(name, context):
                return func(*args, **kwargs)

            # Request approval
            approval = agent.request_approval(
                action=name,
                context=context,
                timeout_seconds=timeout_seconds,
            )

            if approval.approved:
                return func(*args, **kwargs)
            else:
                if on_reject:
                    return on_reject(*args, **kwargs)
                raise PermissionError(
                    f"HITL approval rejected for '{name}': {approval.reason}"
                )

        return wrapper  # type: ignore

    return decorator


def _safe_repr(obj: Any, max_length: int = 500) -> Any:
    """Safely convert object to a loggable representation."""
    try:
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            result = obj
        elif isinstance(obj, (list, tuple)):
            result = [_safe_repr(item, max_length // 2) for item in obj[:10]]
        elif isinstance(obj, dict):
            result = {
                str(k): _safe_repr(v, max_length // 2)
                for k, v in list(obj.items())[:10]
            }
        else:
            result = str(obj)

        # Truncate strings
        if isinstance(result, str) and len(result) > max_length:
            result = result[:max_length] + "..."

        return result
    except Exception:
        return "<unserializable>"
