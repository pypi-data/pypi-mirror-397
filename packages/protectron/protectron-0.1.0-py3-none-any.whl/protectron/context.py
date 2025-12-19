"""Trace context management for distributed tracing."""

import threading
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, Optional

from protectron.utils.ids import generate_span_id

_current_context: ContextVar[Optional["TraceContext"]] = ContextVar(
    "protectron_context", default=None
)


@dataclass
class TraceContext:
    """
    Context for tracing a complete agent invocation.

    Holds trace ID, span information, and other context that should
    be shared across all events within a trace.
    """

    trace_id: str
    name: str
    agent_id: str
    session_id: Optional[str] = None
    current_span_id: str = field(default_factory=generate_span_id)
    parent_span_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    _span_stack: list[str] = field(default_factory=list, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def push_span(self) -> str:
        """
        Push a new span onto the stack.

        Returns:
            The new span ID
        """
        with self._lock:
            self._span_stack.append(self.current_span_id)
            self.parent_span_id = self.current_span_id
            self.current_span_id = generate_span_id()
            return self.current_span_id

    def pop_span(self) -> Optional[str]:
        """
        Pop a span from the stack.

        Returns:
            The popped span ID, or None if stack is empty
        """
        with self._lock:
            if self._span_stack:
                popped = self.current_span_id
                self.current_span_id = self._span_stack.pop()
                self.parent_span_id = (
                    self._span_stack[-1] if self._span_stack else None
                )
                return popped
            return None

    def add_metadata(self, **kwargs: Any) -> None:
        """Add metadata to the context."""
        with self._lock:
            self.metadata.update(kwargs)


def get_current_context() -> Optional[TraceContext]:
    """
    Get the current trace context.

    Returns:
        Current TraceContext or None if not in a trace
    """
    return _current_context.get()


def set_current_context(ctx: Optional[TraceContext]) -> Token[Optional[TraceContext]]:
    """
    Set the current trace context.

    Args:
        ctx: TraceContext to set, or None to clear

    Returns:
        Token that can be used to reset the context
    """
    return _current_context.set(ctx)


def reset_context(token: Token[Optional[TraceContext]]) -> None:
    """
    Reset the context to a previous state.

    Args:
        token: Token from a previous set_current_context call
    """
    _current_context.reset(token)


class SpanContext:
    """
    Context manager for creating a child span within a trace.

    Example:
        with SpanContext(trace_ctx, "process_data") as span:
            # Operations within this span
            pass
    """

    def __init__(self, trace_ctx: TraceContext, name: str):
        self.trace_ctx = trace_ctx
        self.name = name
        self.span_id: Optional[str] = None

    def __enter__(self) -> "SpanContext":
        self.span_id = self.trace_ctx.push_span()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        self.trace_ctx.pop_span()
