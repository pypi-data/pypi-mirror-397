"""Base integration class for framework integrations."""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from protectron.client import ProtectronAgent

logger = logging.getLogger("protectron.integrations")


class BaseIntegration(ABC):
    """
    Abstract base class for framework integrations.

    All framework integrations (LangChain, CrewAI, etc.) should inherit
    from this class and implement the required methods.
    """

    def __init__(
        self,
        agent: "ProtectronAgent",
        *,
        log_inputs: bool = True,
        log_outputs: bool = True,
    ):
        """
        Initialize the integration.

        Args:
            agent: ProtectronAgent instance for logging
            log_inputs: Whether to log input data
            log_outputs: Whether to log output data
        """
        self.agent = agent
        self.log_inputs = log_inputs
        self.log_outputs = log_outputs
        self._trace_id: Optional[str] = None

    @property
    def agent_id(self) -> str:
        """Get the agent ID."""
        return self.agent._agent_id

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this integration."""
        pass

    def _safe_log_action(
        self,
        action: str,
        status: str = "completed",
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Safely log an action, catching any exceptions.

        Returns:
            Event ID if successful, None otherwise
        """
        try:
            return self.agent.log_action(
                action=action,
                status=status,
                details=details,
                duration_ms=duration_ms,
                **kwargs,
            )
        except Exception as e:
            logger.warning(f"Failed to log action '{action}': {e}")
            return None

    def _safe_log_tool_call(
        self,
        tool_name: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Safely log a tool call, catching any exceptions.

        Returns:
            Event ID if successful, None otherwise
        """
        try:
            return self.agent.log_tool_call(
                tool_name=tool_name,
                input_data=input_data if self.log_inputs else None,
                output_data=output_data if self.log_outputs else None,
                duration_ms=duration_ms,
                success=success,
                error=error,
                **kwargs,
            )
        except Exception as e:
            logger.warning(f"Failed to log tool call '{tool_name}': {e}")
            return None

    def _safe_log_llm_call(
        self,
        model: str,
        provider: str,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        duration_ms: Optional[int] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Safely log an LLM call, catching any exceptions.

        Returns:
            Event ID if successful, None otherwise
        """
        try:
            return self.agent.log_llm_call(
                model=model,
                provider=provider,
                prompt=prompt if self.log_inputs else None,
                response=response if self.log_outputs else None,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                duration_ms=duration_ms,
                **kwargs,
            )
        except Exception as e:
            logger.warning(f"Failed to log LLM call '{model}': {e}")
            return None

    def _safe_log_error(
        self,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Safely log an error, catching any exceptions.

        Returns:
            Event ID if successful, None otherwise
        """
        try:
            return self.agent.log_error(
                error_type=error_type,
                message=message,
                stack_trace=stack_trace,
                **kwargs,
            )
        except Exception as e:
            logger.warning(f"Failed to log error '{error_type}': {e}")
            return None
