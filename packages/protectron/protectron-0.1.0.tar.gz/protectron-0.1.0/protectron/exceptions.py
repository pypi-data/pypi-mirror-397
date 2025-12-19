"""Custom exceptions for the Protectron SDK."""

from typing import Any, Dict, Optional


class ProtectronError(Exception):
    """Base exception for all Protectron errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ConfigurationError(ProtectronError):
    """Raised when SDK configuration is invalid."""

    pass


class TransportError(ProtectronError):
    """Raised when HTTP transport fails."""

    pass


class AuthenticationError(ProtectronError):
    """Raised when API authentication fails."""

    pass


class RateLimitError(ProtectronError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self, message: str, retry_after: Optional[int] = None, **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ServerError(ProtectronError):
    """Raised when server returns 5xx error."""

    pass


class AgentStoppedError(ProtectronError):
    """Raised when agent has been emergency stopped."""

    pass


class HITLTimeoutError(ProtectronError):
    """Raised when HITL approval request times out."""

    pass


class ValidationError(ProtectronError):
    """Raised when event validation fails."""

    pass


class BufferFullError(ProtectronError):
    """Raised when event buffer is full and overflow strategy is 'raise'."""

    pass
