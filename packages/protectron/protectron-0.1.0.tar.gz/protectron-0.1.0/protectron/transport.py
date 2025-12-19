"""HTTP transport with retry logic and error handling."""

import gzip
import json
import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from protectron.config import ProtectronConfig
from protectron.events import Event
from protectron.exceptions import (
    AuthenticationError,
    RateLimitError,
    ServerError,
    TransportError,
)

logger = logging.getLogger("protectron.transport")

F = TypeVar("F", bound=Callable[..., Any])


def with_retry(max_attempts: int = 3, base_delay: float = 1.0) -> Callable[[F], F]:
    """Decorator for retry with exponential backoff."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (TransportError, ServerError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2**attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                        )
                        time.sleep(delay)
                except (AuthenticationError, RateLimitError):
                    raise
            if last_exception:
                raise last_exception
            raise TransportError("All retry attempts failed")

        return wrapper  # type: ignore[return-value]

    return decorator


class Transport:
    """HTTP transport with retry logic and compression."""

    def __init__(self, config: ProtectronConfig):
        self.config = config
        self._session = self._create_session()
        self._closed = False

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry configuration."""
        session = requests.Session()

        retry_strategy = Retry(
            total=0,  # We handle retries ourselves
            backoff_factor=self.config.retry_base_delay,
            status_forcelist=[502, 503, 504],
            allowed_methods=["POST", "GET"],
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        session.headers.update(
            {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"protectron-sdk-python/{self.config.sdk_version}",
                "X-Agent-ID": self.config.agent_id,
            }
        )

        return session

    def _compress(self, payload: str) -> tuple[bytes, Dict[str, str]]:
        """Compress payload if it exceeds threshold."""
        body = payload.encode("utf-8")
        headers: Dict[str, str] = {}

        if (
            self.config.compression_enabled
            and len(body) > self.config.compression_threshold
        ):
            body = gzip.compress(body)
            headers["Content-Encoding"] = "gzip"

        return body, headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code == 200:
            return response.json() if response.content else {}

        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", response.text)
        except (json.JSONDecodeError, ValueError):
            error_msg = response.text

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        if response.status_code == 403:
            raise AuthenticationError("Access forbidden")
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            retry_seconds = int(retry_after) if retry_after.isdigit() else 60
            raise RateLimitError(
                f"Rate limited, retry after {retry_seconds}s",
                retry_after=retry_seconds,
            )
        if 500 <= response.status_code < 600:
            raise ServerError(f"Server error ({response.status_code}): {error_msg}")

        raise TransportError(f"Request failed ({response.status_code}): {error_msg}")

    @with_retry(max_attempts=3)
    def send_event(self, event: Event) -> bool:
        """Send a single event."""
        return self.send_batch([event])

    @with_retry(max_attempts=3)
    def send_batch(self, events: List[Event]) -> bool:
        """
        Send a batch of events.

        Args:
            events: List of events to send

        Returns:
            True if successful

        Raises:
            TransportError: On transport failures
            AuthenticationError: On auth failures
            RateLimitError: When rate limited
        """
        if not events or self._closed:
            return True

        url = f"{self.config.base_url}/v1/agents/{self.config.agent_id}/events/batch"
        payload = json.dumps(
            {"events": [e.to_dict() for e in events]},
            default=str,
        )
        body, headers = self._compress(payload)

        try:
            response = self._session.post(
                url,
                data=body,
                headers=headers,
                timeout=self.config.timeout,
            )
            self._handle_response(response)
            logger.debug(f"Successfully sent {len(events)} events")
            return True
        except requests.RequestException as e:
            raise TransportError(f"Network error: {e}") from e

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status from the server."""
        if self._closed:
            raise TransportError("Transport is closed")

        url = f"{self.config.base_url}/v1/agents/{self.config.agent_id}/status"

        try:
            response = self._session.get(url, timeout=10)
            return self._handle_response(response)
        except requests.RequestException as e:
            raise TransportError(f"Failed to get agent status: {e}") from e

    def check_hitl_required(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if action requires HITL approval."""
        if self._closed:
            raise TransportError("Transport is closed")

        url = f"{self.config.base_url}/v1/agents/{self.config.agent_id}/hitl/check"

        try:
            response = self._session.post(
                url,
                json={"action": action, "context": context},
                timeout=10,
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            raise TransportError(f"HITL check failed: {e}") from e

    def request_hitl_approval(
        self,
        action: str,
        context: Dict[str, Any],
        timeout_seconds: int,
    ) -> Dict[str, Any]:
        """Request HITL approval."""
        if self._closed:
            raise TransportError("Transport is closed")

        url = f"{self.config.base_url}/v1/agents/{self.config.agent_id}/hitl/request"

        try:
            response = self._session.post(
                url,
                json={
                    "action": action,
                    "context": context,
                    "timeout_seconds": timeout_seconds,
                },
                timeout=10,
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            raise TransportError(f"HITL request failed: {e}") from e

    def poll_hitl_status(self, request_id: str) -> Dict[str, Any]:
        """Poll for HITL approval status."""
        if self._closed:
            raise TransportError("Transport is closed")

        url = (
            f"{self.config.base_url}/v1/agents/{self.config.agent_id}/hitl/{request_id}"
        )

        try:
            response = self._session.get(url, timeout=10)
            return self._handle_response(response)
        except requests.RequestException as e:
            raise TransportError(f"HITL poll failed: {e}") from e

    def close(self) -> None:
        """Close the transport session."""
        if not self._closed:
            self._session.close()
            self._closed = True
            logger.debug("Transport closed")

    @property
    def is_closed(self) -> bool:
        """Check if transport is closed."""
        return self._closed
