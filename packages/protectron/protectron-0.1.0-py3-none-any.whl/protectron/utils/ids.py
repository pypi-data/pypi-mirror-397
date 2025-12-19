"""ID generation utilities."""

import secrets

CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _generate_id(prefix: str, length: int = 16) -> str:
    """Generate random ID with prefix."""
    random_part = "".join(secrets.choice(CHARSET) for _ in range(length))
    return f"{prefix}{random_part}"


def generate_event_id() -> str:
    """Generate event ID (evt_xxx)."""
    return _generate_id("evt_", 16)


def generate_trace_id() -> str:
    """Generate trace ID (trace_xxx)."""
    return _generate_id("trace_", 24)


def generate_span_id() -> str:
    """Generate span ID (span_xxx)."""
    return _generate_id("span_", 16)


def generate_session_id() -> str:
    """Generate session ID (sess_xxx)."""
    return _generate_id("sess_", 12)


def generate_request_id() -> str:
    """Generate HITL request ID (req_xxx)."""
    return _generate_id("req_", 16)


def validate_id(id_value: str, prefix: str) -> bool:
    """Validate ID format."""
    if not id_value or not isinstance(id_value, str):
        return False
    if not id_value.startswith(prefix):
        return False
    suffix = id_value[len(prefix) :]
    return len(suffix) >= 8 and all(c in CHARSET for c in suffix)


def validate_event_id(event_id: str) -> bool:
    """Validate event ID format."""
    return validate_id(event_id, "evt_")


def validate_trace_id(trace_id: str) -> bool:
    """Validate trace ID format."""
    return validate_id(trace_id, "trace_")


def validate_span_id(span_id: str) -> bool:
    """Validate span ID format."""
    return validate_id(span_id, "span_")


def validate_session_id(session_id: str) -> bool:
    """Validate session ID format."""
    return validate_id(session_id, "sess_")


def validate_agent_id(agent_id: str) -> bool:
    """Validate agent ID format."""
    return validate_id(agent_id, "agt_")
