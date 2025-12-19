"""Configuration management with validation."""

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ProtectronConfig:
    """SDK configuration with sensible defaults."""

    # Required
    api_key: str
    agent_id: str

    # API Settings
    base_url: str = "https://api.protectron.ai"
    environment: str = "production"

    # Buffering
    buffer_size: int = 1000
    flush_interval: float = 5.0
    batch_size: int = 100

    # Retry
    retry_attempts: int = 3
    retry_base_delay: float = 1.0
    timeout: float = 30.0

    # Privacy
    pii_redaction_enabled: bool = True
    pii_patterns: List[str] = field(
        default_factory=lambda: ["email", "phone", "ssn", "credit_card", "ip_address"]
    )

    # Compression
    compression_enabled: bool = True
    compression_threshold: int = 1024

    # Persistence
    persist_path: Optional[str] = None

    # Debug
    debug: bool = False
    sdk_version: str = "0.1.0"

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("api_key is required")

        if not re.match(r"^pk_(live|test)_[a-zA-Z0-9]{20,}$", self.api_key):
            raise ValueError("api_key must be 'pk_live_xxx' or 'pk_test_xxx' format")

        if not self.agent_id:
            raise ValueError("agent_id is required")

        if not re.match(r"^agt_[a-zA-Z0-9]{12,}$", self.agent_id):
            raise ValueError("agent_id must be 'agt_xxx' format")

        if self.environment not in ("production", "staging", "development"):
            raise ValueError("environment must be production/staging/development")

        if self.buffer_size < 0:
            raise ValueError("buffer_size must be non-negative")

        if self.flush_interval <= 0:
            raise ValueError("flush_interval must be positive")

        if self.batch_size <= 0 or self.batch_size > 500:
            raise ValueError("batch_size must be between 1 and 500")

        if self.retry_attempts < 0:
            raise ValueError("retry_attempts must be non-negative")

        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

    @classmethod
    def from_env(cls, **overrides: object) -> "ProtectronConfig":
        """Create config from environment variables."""
        config = {
            "api_key": os.environ.get("PROTECTRON_API_KEY", ""),
            "agent_id": os.environ.get("PROTECTRON_AGENT_ID", ""),
            "base_url": os.getenv(
                "PROTECTRON_BASE_URL", "https://api.protectron.ai"
            ),
            "environment": os.getenv("PROTECTRON_ENVIRONMENT", "production"),
            "debug": os.getenv("PROTECTRON_DEBUG", "").lower() == "true",
            "pii_redaction_enabled": os.getenv(
                "PROTECTRON_PII_REDACTION", "true"
            ).lower()
            == "true",
        }

        # Parse numeric values from env
        if buffer_size := os.getenv("PROTECTRON_BUFFER_SIZE"):
            config["buffer_size"] = int(buffer_size)
        if flush_interval := os.getenv("PROTECTRON_FLUSH_INTERVAL"):
            config["flush_interval"] = float(flush_interval)
        if batch_size := os.getenv("PROTECTRON_BATCH_SIZE"):
            config["batch_size"] = int(batch_size)

        config.update(overrides)
        return cls(**config)  # type: ignore[arg-type]

    @property
    def is_test_mode(self) -> bool:
        """Check if using test API key."""
        return self.api_key.startswith("pk_test_")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
