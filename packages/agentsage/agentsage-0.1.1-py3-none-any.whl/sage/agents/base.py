"""
Base agent class for SAGE.

Provides the foundation for agents with tool capabilities.
"""

from typing import List, Optional, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage


class SageAgent:
    """Base class for SAGE agents with tool capabilities.

    Agents can use tools to gather information and validate ideas
    during the problem-solving workflow.

    Attributes:
        name: Display name of the agent.
        role: The agent's expertise area.
        focus: Specific instructions for this agent.
        llm: The language model for this agent.
        tools: List of tools available to this agent.
    """

    def __init__(
        self,
        name: str,
        role: str,
        focus: str,
        llm: BaseChatModel,
        tools: Optional[List[BaseTool]] = None,
    ):
        """Initialize a SAGE agent.

        Args:
            name: Display name of the agent.
            role: The agent's expertise area.
            focus: Specific instructions for this agent.
            llm: The language model to use.
            tools: Optional list of tools for this agent.
        """
        self.name = name
        self.role = role
        self.focus = focus
        self.llm = llm
        self.tools = tools or []

    def invoke(
        self,
        task: str,
        system_prompt: str,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Invoke the agent with a task.

        Args:
            task: The task or question for the agent.
            system_prompt: System prompt defining the agent's behavior.
            context: Optional additional context.

        Returns:
            Dictionary with content, tool_calls, and tool_results.
        """
        messages: List[BaseMessage] = [SystemMessage(content=system_prompt)]

        if context:
            messages.append(HumanMessage(content=context))

        messages.append(HumanMessage(content=task))

        if self.tools:
            return self._invoke_with_tools(messages)
        else:
            return self._invoke_direct(messages)

    def _invoke_direct(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Invoke the LLM directly without tools.

        Args:
            messages: List of messages for the LLM.

        Returns:
            Dictionary with content and empty tool info.
        """
        response = self.llm.invoke(messages)
        return {
            "content": response.content,
            "tool_calls": [],
            "tool_results": [],
        }

    def _invoke_with_tools(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Invoke the LLM with tool support using ReAct pattern.

        This implements a simple ReAct loop where the agent can
        call tools and receive results.

        Args:
            messages: List of messages for the LLM.

        Returns:
            Dictionary with content, tool_calls, and tool_results.
        """
        # Bind tools to the LLM
        llm_with_tools = self.llm.bind_tools(self.tools)

        tool_calls = []
        tool_results = []
        max_iterations = 5  # Prevent infinite loops

        for _ in range(max_iterations):
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            # Check if the model wants to call tools
            if not hasattr(response, "tool_calls") or not response.tool_calls:
                # No tool calls, we're done
                return {
                    "content": response.content,
                    "tool_calls": tool_calls,
                    "tool_results": tool_results,
                }

            # Process tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Find and execute the tool
                tool_result = self._execute_tool(tool_name, tool_args)

                tool_calls.append({
                    "name": tool_name,
                    "args": tool_args,
                })
                tool_results.append({
                    "name": tool_name,
                    "result": tool_result,
                })

                # Add tool result to messages
                from langchain_core.messages import ToolMessage
                messages.append(ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call.get("id", tool_name),
                ))

        # Max iterations reached, return what we have
        final_response = llm_with_tools.invoke(messages)
        return {
            "content": final_response.content,
            "tool_calls": tool_calls,
            "tool_results": tool_results,
        }

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute.
            tool_args: Arguments for the tool.

        Returns:
            Tool execution result as string.
        """
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    return tool.invoke(tool_args)
                except Exception as e:
                    return f"Tool error: {type(e).__name__}: {str(e)}"

        return f"Tool not found: {tool_name}"
