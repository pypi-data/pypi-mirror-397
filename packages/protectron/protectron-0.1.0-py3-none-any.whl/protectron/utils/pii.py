"""PII detection and redaction."""

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Pattern, Set

if TYPE_CHECKING:
    from protectron.events import Event

logger = logging.getLogger("protectron.pii")


@dataclass
class RedactionResult:
    """Result of a redaction operation."""

    original_length: int
    redacted_length: int
    patterns_found: Set[str] = field(default_factory=set)
    redaction_count: int = 0


class PIIRedactor:
    """
    Detects and redacts Personally Identifiable Information (PII).

    Supports common PII patterns including emails, phone numbers,
    SSNs, credit cards, and IP addresses.
    """

    PATTERNS: Dict[str, Pattern[str]] = {
        "credit_card": re.compile(
            r"\b(?:4[0-9]{12}(?:[0-9]{3})?"  # Visa
            r"|5[1-5][0-9]{14}"  # Mastercard
            r"|3[47][0-9]{13}"  # Amex
            r"|6(?:011|5[0-9]{2})[0-9]{12})\b"  # Discover
        ),
        "ssn": re.compile(
            r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b"
        ),
        "email": re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            re.IGNORECASE,
        ),
        "phone": re.compile(
            r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"
        ),
        "ip_address": re.compile(
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        ),
    }

    PLACEHOLDER_TEMPLATE = "[REDACTED:{type}]"

    def __init__(self, enabled_patterns: Optional[List[str]] = None):
        """
        Initialize the PII redactor.

        Args:
            enabled_patterns: List of pattern names to enable.
                            If None, all patterns are enabled.
        """
        self._patterns: Dict[str, Pattern[str]] = {}
        enabled = enabled_patterns or list(self.PATTERNS.keys())

        for name in enabled:
            if name in self.PATTERNS:
                self._patterns[name] = self.PATTERNS[name]
            else:
                logger.warning(f"Unknown PII pattern: {name}")

    def redact_string(self, text: str) -> tuple[str, RedactionResult]:
        """
        Redact PII from a string.

        Args:
            text: Text to redact

        Returns:
            Tuple of (redacted_text, RedactionResult)
        """
        if not text:
            return text, RedactionResult(0, 0, set(), 0)

        original_length = len(text)
        patterns_found: Set[str] = set()
        redaction_count = 0
        result = text

        for pattern_name, pattern in self._patterns.items():
            matches = pattern.findall(result)
            if matches:
                patterns_found.add(pattern_name)
                redaction_count += len(matches)
                placeholder = self.PLACEHOLDER_TEMPLATE.format(
                    type=pattern_name.upper()
                )
                result = pattern.sub(placeholder, result)

        return result, RedactionResult(
            original_length=original_length,
            redacted_length=len(result),
            patterns_found=patterns_found,
            redaction_count=redaction_count,
        )

    def redact_dict(
        self, data: Dict[str, Any], max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Recursively redact PII from a dictionary.

        Args:
            data: Dictionary to redact
            max_depth: Maximum recursion depth

        Returns:
            Redacted dictionary
        """
        return self._redact_value(data, 0, max_depth)  # type: ignore[return-value]

    def _redact_value(self, value: Any, depth: int, max_depth: int) -> Any:
        """Recursively redact a value."""
        if depth > max_depth:
            return value

        if isinstance(value, str):
            redacted, _ = self.redact_string(value)
            return redacted

        if isinstance(value, dict):
            return {
                k: self._redact_value(v, depth + 1, max_depth)
                for k, v in value.items()
            }

        if isinstance(value, list):
            return [
                self._redact_value(item, depth + 1, max_depth) for item in value
            ]

        return value

    def redact_event(self, event: "Event") -> "Event":
        """
        Redact PII from an event.

        Creates a new event with redacted data.

        Args:
            event: Event to redact

        Returns:
            New event with PII redacted
        """
        from protectron.events import Event

        kwargs: Dict[str, Any] = {}

        if event.input_data:
            kwargs["input_data"] = self.redact_dict(event.input_data)
        if event.output_data:
            kwargs["output_data"] = self.redact_dict(event.output_data)
        if event.reasoning:
            kwargs["reasoning"], _ = self.redact_string(event.reasoning)
        if event.error_message:
            kwargs["error_message"], _ = self.redact_string(event.error_message)
        if event.metadata:
            kwargs["metadata"] = self.redact_dict(event.metadata)

        return Event(
            event_type=event.event_type,
            agent_id=event.agent_id,
            event_id=event.event_id,
            timestamp=event.timestamp,
            span_id=event.span_id,
            trace_id=event.trace_id,
            parent_span_id=event.parent_span_id,
            session_id=event.session_id,
            event_name=event.event_name,
            status=event.status,
            input_data=kwargs.get("input_data", event.input_data),
            output_data=kwargs.get("output_data", event.output_data),
            decision=event.decision,
            confidence=event.confidence,
            reasoning=kwargs.get("reasoning", event.reasoning),
            alternatives=event.alternatives,
            tool_name=event.tool_name,
            model=event.model,
            provider=event.provider,
            tokens_input=event.tokens_input,
            tokens_output=event.tokens_output,
            duration_ms=event.duration_ms,
            override_by=event.override_by,
            override_reason=event.override_reason,
            delegated_to_agent=event.delegated_to_agent,
            delegated_from_agent=event.delegated_from_agent,
            error_type=event.error_type,
            error_message=kwargs.get("error_message", event.error_message),
            stack_trace=event.stack_trace,
            metadata=kwargs.get("metadata", event.metadata),
            environment=event.environment,
            sdk_version=event.sdk_version,
            _pii_redacted=True,
        )

    def has_pii(self, text: str) -> bool:
        """
        Check if text contains PII.

        Args:
            text: Text to check

        Returns:
            True if PII is detected
        """
        for pattern in self._patterns.values():
            if pattern.search(text):
                return True
        return False

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detect and return all PII found in text.

        Args:
            text: Text to scan

        Returns:
            Dictionary mapping pattern names to found matches
        """
        found: Dict[str, List[str]] = {}

        for pattern_name, pattern in self._patterns.items():
            matches = pattern.findall(text)
            if matches:
                found[pattern_name] = matches

        return found

    @property
    def enabled_patterns(self) -> List[str]:
        """Get list of enabled pattern names."""
        return list(self._patterns.keys())
