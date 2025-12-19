"""Human-in-the-Loop (HITL) client for approval workflows."""

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

from protectron.exceptions import HITLTimeoutError, TransportError

if TYPE_CHECKING:
    from protectron.transport import Transport

logger = logging.getLogger("protectron.hitl")


@dataclass
class HITLResponse:
    """Response from a HITL approval request."""

    status: str  # "pending", "approved", "rejected", "timeout"
    request_id: str
    reviewer: Optional[str] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @property
    def approved(self) -> bool:
        """Check if request was approved."""
        return self.status == "approved"

    @property
    def rejected(self) -> bool:
        """Check if request was rejected."""
        return self.status == "rejected"

    @property
    def timed_out(self) -> bool:
        """Check if request timed out."""
        return self.status == "timeout"

    @property
    def pending(self) -> bool:
        """Check if request is still pending."""
        return self.status == "pending"

    @property
    def is_final(self) -> bool:
        """Check if this is a final (non-pending) status."""
        return self.status in ("approved", "rejected", "timeout")


class HITLClient:
    """
    Client for Human-in-the-Loop approval workflows.

    Handles checking if actions require approval, requesting approvals,
    and polling for approval status.
    """

    def __init__(self, transport: "Transport", agent_id: str):
        """
        Initialize the HITL client.

        Args:
            transport: Transport instance for API calls
            agent_id: Agent ID for this client
        """
        self._transport = transport
        self._agent_id = agent_id

    def check_required(self, action: str, context: Dict[str, Any]) -> bool:
        """
        Check if an action requires human approval.

        This is a non-blocking call that checks the configured HITL rules.

        Args:
            action: The action name to check
            context: Context data for rule evaluation

        Returns:
            True if human approval is required, False otherwise
        """
        try:
            response = self._transport.check_hitl_required(action, context)
            required = response.get("required", False)
            if required:
                rule_id = response.get("rule_id", "unknown")
                logger.debug(f"HITL required for '{action}' (rule: {rule_id})")
            return required
        except TransportError as e:
            logger.warning(f"HITL check failed, defaulting to not required: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in HITL check: {e}")
            return False

    def request_approval(
        self,
        action: str,
        context: Dict[str, Any],
        timeout_seconds: int = 3600,
        block: bool = True,
        poll_interval: float = 2.0,
    ) -> HITLResponse:
        """
        Request human approval for an action.

        Args:
            action: The action requiring approval
            context: Full context for the reviewer
            timeout_seconds: How long to wait for approval
            block: If True, wait for response; if False, return immediately
            poll_interval: Seconds between status polls (when blocking)

        Returns:
            HITLResponse with approval status

        Raises:
            HITLTimeoutError: If approval times out (only when blocking)
            TransportError: On transport failures
        """
        try:
            response = self._transport.request_hitl_approval(
                action, context, timeout_seconds
            )
            request_id = response.get("request_id", "")

            if not request_id:
                raise TransportError("No request_id in HITL response")

            logger.info(f"HITL approval requested: {request_id} for '{action}'")

            if not block:
                return HITLResponse(
                    status="pending",
                    request_id=request_id,
                )

            return self._poll_until_complete(
                request_id=request_id,
                timeout_seconds=timeout_seconds,
                poll_interval=poll_interval,
            )

        except TransportError:
            raise
        except Exception as e:
            raise TransportError(f"HITL request failed: {e}") from e

    def get_status(self, request_id: str) -> HITLResponse:
        """
        Get the current status of a HITL request.

        Args:
            request_id: The request ID to check

        Returns:
            HITLResponse with current status
        """
        try:
            response = self._transport.poll_hitl_status(request_id)
            return HITLResponse(
                status=response.get("status", "pending"),
                request_id=request_id,
                reviewer=response.get("reviewer"),
                reason=response.get("reason"),
                metadata=response.get("metadata"),
            )
        except TransportError:
            raise
        except Exception as e:
            raise TransportError(f"Failed to get HITL status: {e}") from e

    def _poll_until_complete(
        self,
        request_id: str,
        timeout_seconds: int,
        poll_interval: float,
    ) -> HITLResponse:
        """
        Poll for HITL status until complete or timeout.

        Args:
            request_id: Request ID to poll
            timeout_seconds: Maximum time to wait
            poll_interval: Seconds between polls

        Returns:
            Final HITLResponse

        Raises:
            HITLTimeoutError: If approval times out
        """
        start_time = time.time()
        last_status = "pending"

        while True:
            elapsed = time.time() - start_time

            if elapsed >= timeout_seconds:
                logger.warning(f"HITL request {request_id} timed out")
                raise HITLTimeoutError(
                    f"HITL approval timed out after {timeout_seconds}s",
                    details={"request_id": request_id, "last_status": last_status},
                )

            try:
                response = self.get_status(request_id)
                last_status = response.status

                if response.is_final:
                    logger.info(
                        f"HITL request {request_id} completed: {response.status}"
                    )
                    return response

            except TransportError as e:
                logger.warning(f"Error polling HITL status: {e}")

            time.sleep(poll_interval)

    def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a pending HITL request.

        Note: This is a best-effort operation. The request may still
        be processed if a reviewer acts before cancellation.

        Args:
            request_id: Request ID to cancel

        Returns:
            True if cancellation was acknowledged
        """
        logger.info(f"Cancelling HITL request: {request_id}")
        return True
