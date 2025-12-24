"""
Code execution tool for SAGE agents.

Provides Python code execution capabilities for testing and validating ideas.
Uses official LangChain experimental tools.
"""

import warnings
from langchain_core.tools import BaseTool
from langchain_experimental.tools import PythonREPLTool


def create_code_exec_tool() -> BaseTool:
    """Create a code execution tool.

    Returns:
        Configured code execution tool using LangChain's PythonREPLTool.
    """
    # Suppress the "can execute arbitrary code" warning for cleaner output
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return PythonREPLTool()
