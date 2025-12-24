"""
Core orchestration engine for SAGE multi-agent framework.

This module provides the main Sage class that coordinates multiple AI agents
through a structured workflow using LangGraph for state management.
"""

from typing import Callable, List, Optional

from .graph.state import SageState
from .graph.workflow import create_workflow
from .providers import create_model
from .tools import create_tools
from .types import Agent, AgentContribution, Config, Message, Phase, Result


class Sage:
    """
    Multi-agent orchestration engine for collaborative problem solving.

    Sage coordinates multiple AI agents through three phases:
    1. Research: Agents independently analyze the problem
    2. Discuss: Agents review and challenge each other's findings
    3. Synthesize: Insights are combined into a comprehensive solution

    Example:
        >>> sage = Sage(model="gpt-4o")
        >>> agents = [
        ...     Agent(role="researcher", focus="Gather facts"),
        ...     Agent(role="critic", focus="Identify risks"),
        ... ]
        >>> result = sage.solve("How should we scale?", agents)
        >>> print(result.summary)

    Attributes:
        config: Session configuration including model and parameters.
        provider: LLM provider name (auto-detected if not specified).
        tools_enabled: Whether agent tools are active.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        provider: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        tools_enabled: bool = True,
        web_search: bool = True,
        code_execution: bool = True,
        file_reading: bool = True,
    ) -> None:
        """
        Initialize a SAGE instance.

        Args:
            model: LLM model identifier (e.g., "gpt-4o", "claude-3-opus").
            provider: LLM provider. Auto-detected from model if not specified.
            max_tokens: Maximum tokens per completion.
            temperature: Sampling temperature between 0.0 and 2.0.
            tools_enabled: Enable agent tools (web search, code exec, etc.).
            web_search: Enable web search capability.
            code_execution: Enable Python code execution.
            file_reading: Enable local file reading.
        """
        self.config = Config(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        self.provider = provider
        self.tools_enabled = tools_enabled

        self._web_search = web_search
        self._code_execution = code_execution
        self._file_reading = file_reading

        self._on_message: Optional[Callable[[str, str, str], None]] = None
        self._on_phase: Optional[Callable[[str], None]] = None
        self._on_tool_call: Optional[Callable[[str, str, dict], None]] = None

        self._llm = create_model(
            model=model,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        self._tools = []
        if tools_enabled:
            self._tools = create_tools(
                web_search=web_search,
                code_exec=code_execution,
                file_read=file_reading,
            )

    def on_message(self, callback: Callable[[str, str, str], None]) -> "Sage":
        """
        Register a callback for agent messages.

        Args:
            callback: Function called with (agent_name, role, content).

        Returns:
            Self for method chaining.
        """
        self._on_message = callback
        return self

    def on_phase(self, callback: Callable[[str], None]) -> "Sage":
        """
        Register a callback for phase transitions.

        Args:
            callback: Function called with phase name.

        Returns:
            Self for method chaining.
        """
        self._on_phase = callback
        return self

    def on_tool_call(self, callback: Callable[[str, str, dict], None]) -> "Sage":
        """
        Register a callback for tool invocations.

        Args:
            callback: Function called with (agent_name, tool_name, args).

        Returns:
            Self for method chaining.
        """
        self._on_tool_call = callback
        return self

    def solve(self, task: str, agents: List[Agent]) -> Result:
        """
        Solve a task using multiple agents.

        Args:
            task: The problem or question to solve.
            agents: List of agents with different roles and perspectives.

        Returns:
            Result containing the synthesized solution and all contributions.

        Raises:
            ValueError: If task is empty or no agents provided.
        """
        if not task:
            raise ValueError("Task cannot be empty")
        if not agents:
            raise ValueError("At least one agent is required")

        workflow = create_workflow(
            llm=self._llm,
            tools=self._tools if self.tools_enabled else None,
            on_message=self._on_message,
            on_phase=self._on_phase,
            on_tool_call=self._on_tool_call,
        )

        initial_state: SageState = {
            "task": task,
            "agents": [
                {"name": a.display_name, "role": a.role, "focus": a.focus}
                for a in agents
            ],
            "current_phase": "research",
            "current_agent_index": 0,
            "research_outputs": [],
            "discussion_outputs": [],
            "synthesis": None,
            "model_name": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "tools_enabled": self.tools_enabled,
            "error": None,
        }

        final_state = workflow.invoke(initial_state)
        return self._build_result(task, agents, final_state)

    def _build_result(
        self,
        task: str,
        agents: List[Agent],
        state: SageState,
    ) -> Result:
        """Build Result object from final workflow state."""
        contributions = []
        all_messages = []

        for i, output in enumerate(state.get("research_outputs", [])):
            agent_name = output.get("agent_name", f"Agent-{i}")
            agent_role = output.get("role", "unknown")

            msg = Message(
                agent_name=agent_name,
                role=agent_role,
                phase=Phase.RESEARCH.value,
                content=output.get("content", ""),
            )
            all_messages.append(msg)

            contributions.append(
                AgentContribution(
                    agent_name=agent_name,
                    role=agent_role,
                    key_points=output.get("content", ""),
                    messages=(msg,),
                )
            )

        for i, output in enumerate(state.get("discussion_outputs", [])):
            msg = Message(
                agent_name=output.get("agent_name", f"Agent-{i}"),
                role=output.get("role", "unknown"),
                phase=Phase.DISCUSS.value,
                content=output.get("content", ""),
            )
            all_messages.append(msg)

        return Result(
            task=task,
            summary=state.get("synthesis", ""),
            contributions=tuple(contributions),
            messages=tuple(all_messages),
            model=self.config.model,
            total_agents=len(agents),
            phases_completed=3,
        )
