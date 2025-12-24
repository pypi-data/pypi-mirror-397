"""
Web search tool for SAGE agents.

Provides web search capabilities using DuckDuckGo (free) or Tavily (premium).
Uses official LangChain tools.
"""

from typing import Optional
from langchain_core.tools import BaseTool


def create_web_search_tool(
    provider: str = "duckduckgo",
    api_key: Optional[str] = None,
) -> BaseTool:
    """Create a web search tool with the specified provider.

    Args:
        provider: Search provider ("duckduckgo" or "tavily").
        api_key: API key for Tavily (not needed for DuckDuckGo).

    Returns:
        Configured web search tool.
    """
    if provider == "tavily" and api_key:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            return TavilySearchResults(api_key=api_key, max_results=5)
        except ImportError:
            pass

    # Use official LangChain DuckDuckGo tool
    from langchain_community.tools import DuckDuckGoSearchRun
    return DuckDuckGoSearchRun()
