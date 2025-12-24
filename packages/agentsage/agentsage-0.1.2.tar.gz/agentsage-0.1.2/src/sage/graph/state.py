"""LangGraph state schema for SAGE workflow."""

from operator import add
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class AgentOutput(TypedDict):
    """Output from a single agent during a workflow phase."""

    agent_name: str
    role: str
    content: str
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]


class SageState(TypedDict):
    """
    State schema for the SAGE workflow graph.

    This state flows through all nodes, accumulating outputs
    from each agent across the research, discuss, and synthesize phases.
    """

    task: str
    agents: List[Dict[str, str]]
    current_phase: str
    current_agent_index: int
    research_outputs: Annotated[List[AgentOutput], add]
    discussion_outputs: Annotated[List[AgentOutput], add]
    synthesis: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    tools_enabled: bool
    error: Optional[str]
