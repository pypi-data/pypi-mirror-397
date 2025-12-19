"""
Protectron SDK - EU AI Act compliance for AI agents.

Automatic audit logging, human-in-the-loop approvals, and evidence generation.
"""

from protectron.client import ProtectronAgent
from protectron.config import ProtectronConfig
from protectron.decorators import log_action, log_decision, log_tool, require_hitl, trace
from protectron.events import Event, EventBuilder, EventStatus, EventType
from protectron.exceptions import (
    AgentStoppedError,
    AuthenticationError,
    BufferFullError,
    ConfigurationError,
    HITLTimeoutError,
    ProtectronError,
    RateLimitError,
    ServerError,
    TransportError,
    ValidationError,
)

__version__ = "0.1.0"
__all__ = [
    # Main client
    "ProtectronAgent",
    "ProtectronConfig",
    # Events
    "Event",
    "EventBuilder",
    "EventType",
    "EventStatus",
    # Decorators
    "trace",
    "log_action",
    "log_tool",
    "log_decision",
    "require_hitl",
    # Exceptions
    "ProtectronError",
    "ConfigurationError",
    "TransportError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
    "AgentStoppedError",
    "HITLTimeoutError",
    "ValidationError",
    "BufferFullError",
]
