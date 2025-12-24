"""
SAGE: Synchronized Agents for Generalized Expertise

A LangGraph-powered multi-agent framework for collaborative problem solving.
Multiple AI agents with distinct perspectives analyze problems through
structured research, discussion, and synthesis phases.

Example:
    >>> from sage import Sage, Agent
    >>> sage = Sage(model="gpt-4o")
    >>> agents = [
    ...     Agent(role="researcher", focus="Gather relevant facts"),
    ...     Agent(role="critic", focus="Identify flaws and risks"),
    ...     Agent(role="strategist", focus="Propose solutions"),
    ... ]
    >>> result = sage.solve("How should we scale our database?", agents)
    >>> print(result.summary)

Supported Providers:
    - OpenAI (gpt-4o, gpt-4o-mini, etc.)
    - Anthropic (claude-3-opus, claude-3-sonnet, etc.)
    - Google (gemini-pro, etc.)
    - Ollama (llama2, mistral, etc.)
    - Azure OpenAI
    - AWS Bedrock
"""

__version__ = "0.1.0"

from .types import Agent, Config, Message, Result, AgentContribution, Phase
from .core import Sage
from .providers import ModelFactory, create_model

__all__ = [
    "Sage",
    "Agent",
    "Config",
    "Message",
    "Result",
    "AgentContribution",
    "Phase",
    "ModelFactory",
    "create_model",
]
