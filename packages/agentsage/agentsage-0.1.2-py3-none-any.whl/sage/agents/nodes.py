"""
LangGraph node functions for SAGE workflow phases.

These functions implement the research, discuss, and synthesize phases
of the multi-agent collaboration workflow.
"""

from typing import List, Optional, Callable, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import SystemMessage, HumanMessage

from ..graph.state import SageState, AgentOutput
from .base import SageAgent


# System prompt templates
RESEARCH_SYSTEM_PROMPT = """You are {agent_name}, an expert {role}.

Your focus: {focus}

You are in the RESEARCH phase of a collaborative problem-solving session.
Your job is to analyze the task from your unique perspective and expertise.

You have access to tools to help with your research:
- duckduckgo_search: Search the internet for current information
- read_file: Read local files for context
- list_directory: Explore file structures

IMPORTANT: For questions about current events, prices, news, or real-time data, USE the duckduckgo_search tool first.

Guidelines:
- Use tools when you need external information or to verify facts
- Stay focused on your assigned role and expertise
- Be thorough but concise in your analysis
- Support your points with evidence from your research
- Acknowledge when something is outside your expertise
"""

DISCUSS_SYSTEM_PROMPT = """You are {agent_name}, an expert {role}.

Your focus: {focus}

You are in the DISCUSSION phase of a collaborative problem-solving session.
Review the research findings from all agents and provide your perspective.

Research findings from the team:
{research_findings}

You have access to tools to validate ideas:
- Python_REPL: Run Python code to test or calculate things

Your task:
1. Identify points you agree with and explain why
2. Challenge any assumptions or findings you disagree with
3. Add new insights based on the combined information
4. Highlight any gaps or areas needing more investigation

Guidelines:
- Build on insights from other agents
- Be constructive in your criticism
- Use code execution to validate technical claims if needed
"""

SYNTHESIZE_SYSTEM_PROMPT = """You are a helpful assistant synthesizing insights from a team discussion.

Team discussion:
{discussion_summary}

Your task: Give a clear, natural response to the user's question.

Guidelines:
- Be conversational and direct, like ChatGPT or Claude
- For simple questions, give simple answers (don't over-explain "2+2=4")
- For complex questions, provide thorough but readable explanations
- Use markdown formatting only when it helps readability (lists, code blocks)
- Don't use rigid headers like "SUMMARY" or "KEY INSIGHTS"
- Match the response length to the question complexity
"""


def research_node(
    state: SageState,
    llm: BaseChatModel,
    tools: Optional[List[BaseTool]] = None,
    on_message: Optional[Callable] = None,
    on_tool_call: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Execute research phase for the current agent.

    Args:
        state: Current workflow state.
        llm: Language model for the agent.
        tools: Available tools for research.
        on_message: Callback for agent messages.
        on_tool_call: Callback for tool invocations.

    Returns:
        State updates with research output.
    """
    agent_index = state["current_agent_index"]

    # Check if we've processed all agents
    if agent_index >= len(state["agents"]):
        return {"current_agent_index": 0}  # Reset for next phase

    agent_def = state["agents"][agent_index]
    agent_name = agent_def["name"]
    agent_role = agent_def["role"]
    agent_focus = agent_def["focus"]

    # Create the agent
    # Tool names: duckduckgo_search, read_file, list_directory
    research_tools = [t for t in (tools or []) if t.name in ["duckduckgo_search", "read_file", "list_directory"]]
    agent = SageAgent(
        name=agent_name,
        role=agent_role,
        focus=agent_focus,
        llm=llm,
        tools=research_tools if state.get("tools_enabled", True) else None,
    )

    # Build system prompt
    system_prompt = RESEARCH_SYSTEM_PROMPT.format(
        agent_name=agent_name,
        role=agent_role,
        focus=agent_focus,
    )

    # Invoke the agent
    result = agent.invoke(
        task=state["task"],
        system_prompt=system_prompt,
    )

    # Notify callbacks
    if on_message:
        on_message(agent_name, agent_role, result["content"])

    if on_tool_call and result["tool_calls"]:
        for tc in result["tool_calls"]:
            on_tool_call(agent_name, tc["name"], tc["args"])

    # Build output
    output = AgentOutput(
        agent_name=agent_name,
        role=agent_role,
        content=result["content"],
        tool_calls=result["tool_calls"],
        tool_results=result["tool_results"],
    )

    return {
        "research_outputs": [output],
        "current_agent_index": agent_index + 1,
    }


def discuss_node(
    state: SageState,
    llm: BaseChatModel,
    tools: Optional[List[BaseTool]] = None,
    on_message: Optional[Callable] = None,
    on_tool_call: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Execute discussion phase for the current agent.

    Args:
        state: Current workflow state.
        llm: Language model for the agent.
        tools: Available tools for discussion.
        on_message: Callback for agent messages.
        on_tool_call: Callback for tool invocations.

    Returns:
        State updates with discussion output.
    """
    agent_index = state["current_agent_index"]

    # Check if we've processed all agents
    if agent_index >= len(state["agents"]):
        return {"current_agent_index": 0}  # Reset for next phase

    agent_def = state["agents"][agent_index]
    agent_name = agent_def["name"]
    agent_role = agent_def["role"]
    agent_focus = agent_def["focus"]

    # Format research findings
    research_findings = _format_research_findings(state["research_outputs"])

    # Create the agent
    # Tool name: Python_REPL
    discuss_tools = [t for t in (tools or []) if t.name == "Python_REPL"]
    agent = SageAgent(
        name=agent_name,
        role=agent_role,
        focus=agent_focus,
        llm=llm,
        tools=discuss_tools if state.get("tools_enabled", True) else None,
    )

    # Build system prompt
    system_prompt = DISCUSS_SYSTEM_PROMPT.format(
        agent_name=agent_name,
        role=agent_role,
        focus=agent_focus,
        research_findings=research_findings,
    )

    # Invoke the agent
    result = agent.invoke(
        task=f"Based on the research findings above, provide your analysis and perspective on: {state['task']}",
        system_prompt=system_prompt,
    )

    # Notify callbacks
    if on_message:
        on_message(agent_name, agent_role, result["content"])

    if on_tool_call and result["tool_calls"]:
        for tc in result["tool_calls"]:
            on_tool_call(agent_name, tc["name"], tc["args"])

    # Build output
    output = AgentOutput(
        agent_name=agent_name,
        role=agent_role,
        content=result["content"],
        tool_calls=result["tool_calls"],
        tool_results=result["tool_results"],
    )

    return {
        "discussion_outputs": [output],
        "current_agent_index": agent_index + 1,
    }


def synthesize_node(
    state: SageState,
    llm: BaseChatModel,
    on_message: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Execute synthesis phase to combine all insights.

    Args:
        state: Current workflow state.
        llm: Language model for synthesis.
        on_message: Callback for the synthesis message.

    Returns:
        State updates with synthesis result.
    """
    # Format discussion summary
    discussion_summary = _format_discussion_summary(
        state["research_outputs"],
        state["discussion_outputs"],
    )

    # Build system prompt
    system_prompt = SYNTHESIZE_SYSTEM_PROMPT.format(
        discussion_summary=discussion_summary,
    )

    # Invoke the LLM directly (no tools for synthesis)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Synthesize the team's analysis into a comprehensive solution for: {state['task']}"),
    ]

    response = llm.invoke(messages)
    synthesis = response.content

    # Notify callback
    if on_message:
        on_message("Synthesizer", "synthesizer", synthesis)

    return {
        "synthesis": synthesis,
        "current_phase": "complete",
    }


def _format_research_findings(outputs: List[AgentOutput]) -> str:
    """Format research outputs for the discussion prompt.

    Args:
        outputs: List of research phase outputs.

    Returns:
        Formatted string of research findings.
    """
    findings = []
    for output in outputs:
        findings.append(f"### {output['agent_name']} ({output['role']})\n{output['content']}")

        # Include tool usage if any
        if output["tool_calls"]:
            tool_summary = ", ".join(tc["name"] for tc in output["tool_calls"])
            findings.append(f"_Tools used: {tool_summary}_")

    return "\n\n".join(findings)


def _format_discussion_summary(
    research_outputs: List[AgentOutput],
    discussion_outputs: List[AgentOutput],
) -> str:
    """Format all outputs for the synthesis prompt.

    Args:
        research_outputs: Outputs from the research phase.
        discussion_outputs: Outputs from the discussion phase.

    Returns:
        Formatted string of the full discussion.
    """
    sections = []

    # Research section
    sections.append("## Research Phase\n")
    for output in research_outputs:
        sections.append(f"### {output['agent_name']} ({output['role']})\n{output['content']}\n")

    # Discussion section
    sections.append("\n## Discussion Phase\n")
    for output in discussion_outputs:
        sections.append(f"### {output['agent_name']} ({output['role']})\n{output['content']}\n")

    return "\n".join(sections)
