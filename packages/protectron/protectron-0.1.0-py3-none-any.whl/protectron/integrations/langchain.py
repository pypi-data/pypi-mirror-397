"""LangChain integration for Protectron SDK."""

import logging
import time
import traceback
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

if TYPE_CHECKING:
    from protectron.client import ProtectronAgent

logger = logging.getLogger("protectron.integrations.langchain")

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.outputs import LLMResult

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object  # type: ignore


class ProtectronCallbackHandler(BaseCallbackHandler if LANGCHAIN_AVAILABLE else object):  # type: ignore
    """
    LangChain callback handler for Protectron audit logging.

    Automatically captures:
    - LLM calls (model, tokens, duration)
    - Tool/function calls
    - Agent actions and decisions
    - Chain execution
    - Errors

    Example:
        ```python
        from protectron import ProtectronAgent
        from protectron.integrations.langchain import ProtectronCallbackHandler
        from langchain.agents import create_react_agent

        protectron = ProtectronAgent(api_key="...", agent_id="...")
        handler = ProtectronCallbackHandler(protectron)

        agent = create_react_agent(llm, tools, callbacks=[handler])
        ```
    """

    def __init__(
        self,
        agent: "ProtectronAgent",
        *,
        log_prompts: bool = True,
        log_responses: bool = True,
        log_tool_inputs: bool = True,
        log_tool_outputs: bool = True,
    ):
        """
        Initialize the LangChain callback handler.

        Args:
            agent: ProtectronAgent instance for logging
            log_prompts: Whether to log LLM prompts
            log_responses: Whether to log LLM responses
            log_tool_inputs: Whether to log tool input parameters
            log_tool_outputs: Whether to log tool outputs
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. Install with: pip install langchain-core"
            )

        super().__init__()
        self.agent = agent
        self.log_prompts = log_prompts
        self.log_responses = log_responses
        self.log_tool_inputs = log_tool_inputs
        self.log_tool_outputs = log_tool_outputs

        self._run_starts: Dict[str, float] = {}
        self._llm_starts: Dict[str, Dict[str, Any]] = {}
        self._tool_starts: Dict[str, Dict[str, Any]] = {}
        self._chain_starts: Dict[str, Dict[str, Any]] = {}

    def _get_run_id(self, run_id: UUID) -> str:
        """Convert UUID to string."""
        return str(run_id)

    # =========================================================================
    # LLM Callbacks
    # =========================================================================

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts running."""
        rid = self._get_run_id(run_id)
        self._llm_starts[rid] = {
            "start_time": time.time(),
            "serialized": serialized,
            "prompts": prompts if self.log_prompts else None,
            "model": serialized.get("kwargs", {}).get("model_name")
            or serialized.get("id", ["unknown"])[-1],
        }

    def on_llm_end(
        self,
        response: "LLMResult",
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM ends running."""
        rid = self._get_run_id(run_id)
        start_info = self._llm_starts.pop(rid, {})
        start_time = start_info.get("start_time", time.time())
        duration_ms = int((time.time() - start_time) * 1000)

        model = start_info.get("model", "unknown")
        prompts = start_info.get("prompts")

        # Extract token usage
        tokens_input = None
        tokens_output = None
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            tokens_input = usage.get("prompt_tokens")
            tokens_output = usage.get("completion_tokens")

        # Get response text
        response_text = None
        if self.log_responses and response.generations:
            if response.generations[0]:
                response_text = response.generations[0][0].text

        try:
            self.agent.log_llm_call(
                model=model,
                provider="langchain",
                prompt=prompts[0] if prompts else None,
                response=response_text,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                duration_ms=duration_ms,
            )
        except Exception as e:
            logger.warning(f"Failed to log LLM call: {e}")

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM errors."""
        rid = self._get_run_id(run_id)
        self._llm_starts.pop(rid, None)

        try:
            self.agent.log_error(
                error_type=type(error).__name__,
                message=str(error),
                stack_trace=traceback.format_exc(),
            )
        except Exception as e:
            logger.warning(f"Failed to log LLM error: {e}")

    # =========================================================================
    # Tool Callbacks
    # =========================================================================

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when tool starts running."""
        rid = self._get_run_id(run_id)
        tool_name = serialized.get("name", "unknown_tool")

        self._tool_starts[rid] = {
            "start_time": time.time(),
            "tool_name": tool_name,
            "input_str": input_str if self.log_tool_inputs else None,
            "inputs": inputs if self.log_tool_inputs else None,
        }

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when tool ends running."""
        rid = self._get_run_id(run_id)
        start_info = self._tool_starts.pop(rid, {})
        start_time = start_info.get("start_time", time.time())
        duration_ms = int((time.time() - start_time) * 1000)

        tool_name = start_info.get("tool_name", "unknown_tool")
        input_data = None
        if self.log_tool_inputs:
            input_data = start_info.get("inputs") or {"input": start_info.get("input_str")}

        output_data = None
        if self.log_tool_outputs:
            output_data = {"output": str(output) if output else None}

        try:
            self.agent.log_tool_call(
                tool_name=tool_name,
                input_data=input_data,
                output_data=output_data,
                duration_ms=duration_ms,
                success=True,
            )
        except Exception as e:
            logger.warning(f"Failed to log tool call: {e}")

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when tool errors."""
        rid = self._get_run_id(run_id)
        start_info = self._tool_starts.pop(rid, {})
        start_time = start_info.get("start_time", time.time())
        duration_ms = int((time.time() - start_time) * 1000)

        tool_name = start_info.get("tool_name", "unknown_tool")

        try:
            self.agent.log_tool_call(
                tool_name=tool_name,
                duration_ms=duration_ms,
                success=False,
                error=str(error),
            )
        except Exception as e:
            logger.warning(f"Failed to log tool error: {e}")

    # =========================================================================
    # Chain Callbacks
    # =========================================================================

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when chain starts running."""
        rid = self._get_run_id(run_id)
        chain_name = serialized.get("id", ["unknown"])[-1]

        self._chain_starts[rid] = {
            "start_time": time.time(),
            "chain_name": chain_name,
            "inputs": inputs if self.log_prompts else None,
        }

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when chain ends running."""
        rid = self._get_run_id(run_id)
        start_info = self._chain_starts.pop(rid, {})
        start_time = start_info.get("start_time", time.time())
        duration_ms = int((time.time() - start_time) * 1000)

        chain_name = start_info.get("chain_name", "unknown_chain")

        try:
            self.agent.log_action(
                action=f"chain:{chain_name}",
                status="completed",
                details=outputs if self.log_responses else None,
                duration_ms=duration_ms,
            )
        except Exception as e:
            logger.warning(f"Failed to log chain end: {e}")

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when chain errors."""
        rid = self._get_run_id(run_id)
        self._chain_starts.pop(rid, None)

        try:
            self.agent.log_error(
                error_type=type(error).__name__,
                message=str(error),
                stack_trace=traceback.format_exc(),
            )
        except Exception as e:
            logger.warning(f"Failed to log chain error: {e}")

    # =========================================================================
    # Agent Callbacks
    # =========================================================================

    def on_agent_action(
        self,
        action: "AgentAction",
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when agent takes an action."""
        try:
            self.agent.log_decision(
                decision=f"use_tool:{action.tool}",
                confidence=1.0,
                reasoning=action.log if hasattr(action, "log") else "Agent decided to use tool",
                alternatives=[],
                context={"tool_input": action.tool_input} if self.log_tool_inputs else None,
            )
        except Exception as e:
            logger.warning(f"Failed to log agent action: {e}")

    def on_agent_finish(
        self,
        finish: "AgentFinish",
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when agent finishes."""
        try:
            self.agent.log_action(
                action="agent_finish",
                status="completed",
                details=finish.return_values if self.log_responses else None,
            )
        except Exception as e:
            logger.warning(f"Failed to log agent finish: {e}")

    # =========================================================================
    # Retriever Callbacks
    # =========================================================================

    def on_retriever_start(
        self,
        serialized: Dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when retriever starts."""
        rid = self._get_run_id(run_id)
        self._run_starts[rid] = time.time()

    def on_retriever_end(
        self,
        documents: List[Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when retriever ends."""
        rid = self._get_run_id(run_id)
        start_time = self._run_starts.pop(rid, time.time())
        duration_ms = int((time.time() - start_time) * 1000)

        try:
            self.agent.log_tool_call(
                tool_name="retriever",
                output_data={"document_count": len(documents)} if self.log_tool_outputs else None,
                duration_ms=duration_ms,
                success=True,
            )
        except Exception as e:
            logger.warning(f"Failed to log retriever: {e}")

    def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when retriever errors."""
        rid = self._get_run_id(run_id)
        self._run_starts.pop(rid, None)

        try:
            self.agent.log_error(
                error_type=type(error).__name__,
                message=str(error),
            )
        except Exception as e:
            logger.warning(f"Failed to log retriever error: {e}")
