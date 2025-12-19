"""CrewAI integration for Protectron SDK."""

import logging
import time
import traceback
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, TypeVar

if TYPE_CHECKING:
    from protectron.client import ProtectronAgent

logger = logging.getLogger("protectron.integrations.crewai")

try:
    from crewai import Agent, Crew, Task
    from crewai.tools import BaseTool

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    Agent = object  # type: ignore
    Crew = object  # type: ignore
    Task = object  # type: ignore
    BaseTool = object  # type: ignore

F = TypeVar("F", bound=Callable[..., Any])


class ProtectronCrewAI:
    """
    CrewAI integration for Protectron audit logging.

    Automatically captures:
    - Crew execution (start, end, duration)
    - Task execution and results
    - Agent actions and decisions
    - Tool usage
    - Errors

    Example:
        ```python
        from protectron import ProtectronAgent
        from protectron.integrations.crewai import ProtectronCrewAI
        from crewai import Crew, Agent, Task

        protectron = ProtectronAgent(api_key="...", agent_id="...")
        integration = ProtectronCrewAI(protectron)

        crew = Crew(agents=[...], tasks=[...])
        wrapped_crew = integration.wrap_crew(crew)
        result = wrapped_crew.kickoff()
        ```
    """

    def __init__(
        self,
        agent: "ProtectronAgent",
        *,
        log_task_inputs: bool = True,
        log_task_outputs: bool = True,
        log_tool_inputs: bool = True,
        log_tool_outputs: bool = True,
    ):
        """
        Initialize the CrewAI integration.

        Args:
            agent: ProtectronAgent instance for logging
            log_task_inputs: Whether to log task input data
            log_task_outputs: Whether to log task output data
            log_tool_inputs: Whether to log tool input parameters
            log_tool_outputs: Whether to log tool outputs
        """
        if not CREWAI_AVAILABLE:
            raise ImportError(
                "CrewAI is not installed. Install with: pip install crewai"
            )

        self.agent = agent
        self.log_task_inputs = log_task_inputs
        self.log_task_outputs = log_task_outputs
        self.log_tool_inputs = log_tool_inputs
        self.log_tool_outputs = log_tool_outputs

    def wrap_crew(self, crew: "Crew") -> "Crew":
        """
        Wrap a Crew instance to add Protectron logging.

        Args:
            crew: CrewAI Crew instance

        Returns:
            The same Crew instance with wrapped methods
        """
        original_kickoff = crew.kickoff

        @wraps(original_kickoff)
        def wrapped_kickoff(*args: Any, **kwargs: Any) -> Any:
            crew_name = getattr(crew, "name", None) or "unnamed_crew"
            start_time = time.time()

            try:
                self.agent.log_action(
                    action=f"crew_start:{crew_name}",
                    status="started",
                    details={
                        "agent_count": len(crew.agents) if hasattr(crew, "agents") else 0,
                        "task_count": len(crew.tasks) if hasattr(crew, "tasks") else 0,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to log crew start: {e}")

            try:
                result = original_kickoff(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                try:
                    self.agent.log_action(
                        action=f"crew_complete:{crew_name}",
                        status="completed",
                        details={"result": str(result)[:500]} if self.log_task_outputs else None,
                        duration_ms=duration_ms,
                    )
                except Exception as e:
                    logger.warning(f"Failed to log crew completion: {e}")

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)

                try:
                    self.agent.log_error(
                        error_type=type(e).__name__,
                        message=str(e),
                        stack_trace=traceback.format_exc(),
                        context={"crew": crew_name},
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log crew error: {log_error}")

                raise

        crew.kickoff = wrapped_kickoff  # type: ignore

        # Wrap agents
        if hasattr(crew, "agents"):
            for agent in crew.agents:
                self.wrap_agent(agent)

        # Wrap tasks
        if hasattr(crew, "tasks"):
            for task in crew.tasks:
                self.wrap_task(task)

        return crew

    def wrap_agent(self, crewai_agent: "Agent") -> "Agent":
        """
        Wrap a CrewAI Agent to add logging.

        Args:
            crewai_agent: CrewAI Agent instance

        Returns:
            The same Agent instance with wrapped methods
        """
        agent_name = getattr(crewai_agent, "role", None) or "unnamed_agent"

        # Wrap tools if present
        if hasattr(crewai_agent, "tools") and crewai_agent.tools:
            wrapped_tools = []
            for tool in crewai_agent.tools:
                wrapped_tools.append(self.wrap_tool(tool, agent_name))
            crewai_agent.tools = wrapped_tools

        return crewai_agent

    def wrap_task(self, task: "Task") -> "Task":
        """
        Wrap a CrewAI Task to add logging.

        Args:
            task: CrewAI Task instance

        Returns:
            The same Task instance with wrapped execution
        """
        task_description = getattr(task, "description", "unnamed_task")[:100]

        if hasattr(task, "execute") and callable(task.execute):
            original_execute = task.execute

            @wraps(original_execute)
            def wrapped_execute(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()

                try:
                    self.agent.log_action(
                        action=f"task_start",
                        status="started",
                        details={"description": task_description} if self.log_task_inputs else None,
                    )
                except Exception as e:
                    logger.warning(f"Failed to log task start: {e}")

                try:
                    result = original_execute(*args, **kwargs)
                    duration_ms = int((time.time() - start_time) * 1000)

                    try:
                        self.agent.log_action(
                            action=f"task_complete",
                            status="completed",
                            details={"result": str(result)[:500]} if self.log_task_outputs else None,
                            duration_ms=duration_ms,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to log task completion: {e}")

                    return result

                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)

                    try:
                        self.agent.log_error(
                            error_type=type(e).__name__,
                            message=str(e),
                            stack_trace=traceback.format_exc(),
                        )
                    except Exception as log_error:
                        logger.warning(f"Failed to log task error: {log_error}")

                    raise

            task.execute = wrapped_execute  # type: ignore

        return task

    def wrap_tool(self, tool: Any, agent_name: str = "unknown") -> Any:
        """
        Wrap a CrewAI tool to add logging.

        Args:
            tool: Tool instance (can be BaseTool or callable)
            agent_name: Name of the agent using this tool

        Returns:
            Wrapped tool with logging
        """
        if hasattr(tool, "_run"):
            original_run = tool._run
            tool_name = getattr(tool, "name", None) or type(tool).__name__

            @wraps(original_run)
            def wrapped_run(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()

                input_data = None
                if self.log_tool_inputs:
                    input_data = {"args": str(args)[:200], "kwargs": str(kwargs)[:200]}

                try:
                    result = original_run(*args, **kwargs)
                    duration_ms = int((time.time() - start_time) * 1000)

                    try:
                        self.agent.log_tool_call(
                            tool_name=tool_name,
                            input_data=input_data,
                            output_data={"result": str(result)[:500]} if self.log_tool_outputs else None,
                            duration_ms=duration_ms,
                            success=True,
                            metadata={"agent": agent_name},
                        )
                    except Exception as e:
                        logger.warning(f"Failed to log tool call: {e}")

                    return result

                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)

                    try:
                        self.agent.log_tool_call(
                            tool_name=tool_name,
                            input_data=input_data,
                            duration_ms=duration_ms,
                            success=False,
                            error=str(e),
                            metadata={"agent": agent_name},
                        )
                    except Exception as log_error:
                        logger.warning(f"Failed to log tool error: {log_error}")

                    raise

            tool._run = wrapped_run

        return tool

    def log_delegation(
        self,
        from_agent: str,
        to_agent: str,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Log a task delegation between agents.

        Args:
            from_agent: Name/role of delegating agent
            to_agent: Name/role of receiving agent
            task_description: Description of delegated task
            context: Additional context

        Returns:
            Event ID if successful
        """
        try:
            return self.agent.log_delegation(
                to_agent_id=to_agent,
                task=task_description,
                context=context,
                metadata={"from_agent": from_agent},
            )
        except Exception as e:
            logger.warning(f"Failed to log delegation: {e}")
            return None


def with_protectron(
    protectron_agent: "ProtectronAgent",
    **integration_kwargs: Any,
) -> Callable[[F], F]:
    """
    Decorator to wrap a function that creates/runs a CrewAI crew.

    Example:
        ```python
        @with_protectron(protectron_agent)
        def run_my_crew():
            crew = Crew(agents=[...], tasks=[...])
            return crew.kickoff()
        ```
    """
    integration = ProtectronCrewAI(protectron_agent, **integration_kwargs)

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            func_name = func.__name__

            try:
                protectron_agent.log_action(
                    action=f"crewai_function:{func_name}",
                    status="started",
                )
            except Exception as e:
                logger.warning(f"Failed to log function start: {e}")

            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                try:
                    protectron_agent.log_action(
                        action=f"crewai_function:{func_name}",
                        status="completed",
                        duration_ms=duration_ms,
                    )
                except Exception as e:
                    logger.warning(f"Failed to log function completion: {e}")

                return result

            except Exception as e:
                try:
                    protectron_agent.log_error(
                        error_type=type(e).__name__,
                        message=str(e),
                        stack_trace=traceback.format_exc(),
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log function error: {log_error}")

                raise

        return wrapper  # type: ignore

    return decorator
