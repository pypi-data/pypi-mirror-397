"""Agent tools for SAGE multi-agent framework."""

from typing import List, Optional

from langchain_core.tools import BaseTool

from .code_exec import create_code_exec_tool
from .file_reader import create_file_reader_tool, create_list_directory_tool
from .web_search import create_web_search_tool


def create_tools(
    web_search: bool = True,
    code_exec: bool = True,
    file_read: bool = True,
) -> List[BaseTool]:
    """
    Create the default tool set for SAGE agents.

    Args:
        web_search: Include web search capability.
        code_exec: Include Python code execution.
        file_read: Include file reading capabilities.

    Returns:
        List of configured LangChain tools.
    """
    tools = []

    if web_search:
        tools.append(create_web_search_tool())

    if code_exec:
        tools.append(create_code_exec_tool())

    if file_read:
        tools.append(create_file_reader_tool())
        tools.append(create_list_directory_tool())

    return tools


__all__ = [
    "create_tools",
    "create_web_search_tool",
    "create_code_exec_tool",
    "create_file_reader_tool",
    "create_list_directory_tool",
]
