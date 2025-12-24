"""LangGraph workflow definition for SAGE."""

from typing import Callable, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph

from .state import SageState


def create_workflow(
    llm: BaseChatModel,
    tools: Optional[List[BaseTool]] = None,
    on_message: Optional[Callable] = None,
    on_phase: Optional[Callable] = None,
    on_tool_call: Optional[Callable] = None,
) -> StateGraph:
    """
    Create and compile the SAGE workflow graph.

    Args:
        llm: LangChain chat model for agent responses.
        tools: Optional tools available to agents.
        on_message: Callback for agent messages.
        on_phase: Callback for phase transitions.
        on_tool_call: Callback for tool invocations.

    Returns:
        Compiled StateGraph ready for execution.
    """
    from ..agents.nodes import discuss_node, research_node, synthesize_node

    graph = StateGraph(SageState)

    def research_fn(state: SageState) -> dict:
        return research_node(state, llm, tools, on_message, on_tool_call)

    def discuss_fn(state: SageState) -> dict:
        return discuss_node(state, llm, tools, on_message, on_tool_call)

    def synthesize_fn(state: SageState) -> dict:
        return synthesize_node(state, llm, on_message)

    def notify_phase(phase: str) -> Callable:
        def notify(state: SageState) -> dict:
            if on_phase:
                on_phase(phase)
            return {"current_phase": phase}

        return notify

    graph.add_node("start_research", notify_phase("research"))
    graph.add_node("research", research_fn)
    graph.add_node("start_discuss", notify_phase("discuss"))
    graph.add_node("discuss", discuss_fn)
    graph.add_node("start_synthesize", notify_phase("synthesize"))
    graph.add_node("synthesize", synthesize_fn)
    graph.add_node("complete", notify_phase("complete"))

    graph.set_entry_point("start_research")

    graph.add_edge("start_research", "research")
    graph.add_conditional_edges(
        "research",
        _route_research,
        {"research": "research", "discuss": "start_discuss"},
    )

    graph.add_edge("start_discuss", "discuss")
    graph.add_conditional_edges(
        "discuss",
        _route_discuss,
        {"discuss": "discuss", "synthesize": "start_synthesize"},
    )

    graph.add_edge("start_synthesize", "synthesize")
    graph.add_edge("synthesize", "complete")
    graph.add_edge("complete", END)

    return graph.compile()


def _route_research(state: SageState) -> str:
    """Route after research: continue with next agent or move to discuss."""
    if state["current_agent_index"] < len(state["agents"]):
        return "research"
    return "discuss"


def _route_discuss(state: SageState) -> str:
    """Route after discuss: continue with next agent or move to synthesize."""
    if state["current_agent_index"] < len(state["agents"]):
        return "discuss"
    return "synthesize"
