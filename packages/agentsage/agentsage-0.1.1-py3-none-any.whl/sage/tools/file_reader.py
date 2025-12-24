"""
File reading tools for SAGE agents.

Provides file reading and directory listing capabilities for context gathering.
Uses official LangChain tools.
"""

from langchain_core.tools import BaseTool
from langchain_community.tools.file_management import ReadFileTool, ListDirectoryTool


def create_file_reader_tool() -> BaseTool:
    """Create a file reader tool.

    Returns:
        Configured file reader tool using LangChain's ReadFileTool.
    """
    return ReadFileTool()


def create_list_directory_tool() -> BaseTool:
    """Create a directory listing tool.

    Returns:
        Configured directory listing tool using LangChain's ListDirectoryTool.
    """
    return ListDirectoryTool()
