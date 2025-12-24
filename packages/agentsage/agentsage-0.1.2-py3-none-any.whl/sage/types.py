"""
Data types for SAGE multi-agent framework.

This module defines immutable data structures used throughout SAGE.
All types are frozen dataclasses to ensure thread safety and
predictable behavior during concurrent agent execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple


class Phase(Enum):
    """Workflow phases in the SAGE problem-solving process."""

    RESEARCH = "research"
    DISCUSS = "discuss"
    SYNTHESIZE = "synthesize"
    COMPLETE = "complete"


@dataclass(frozen=True)
class Agent:
    """
    An agent with a specific role and area of focus.

    Agents represent distinct perspectives in the problem-solving process.
    Each agent analyzes problems through the lens of their assigned role.

    Attributes:
        role: Area of expertise (e.g., "researcher", "critic", "strategist").
        focus: Specific instructions guiding the agent's analysis.
        name: Display name. Defaults to "Agent-{Role}" if not provided.

    Example:
        >>> agent = Agent(role="security", focus="Identify vulnerabilities")
        >>> agent.display_name
        'Agent-Security'
    """

    role: str
    focus: str
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.role:
            raise ValueError("Agent role cannot be empty")
        if not self.focus:
            raise ValueError("Agent focus cannot be empty")

    @property
    def display_name(self) -> str:
        """Return the agent's display name."""
        return self.name or f"Agent-{self.role.title()}"


@dataclass(frozen=True)
class Config:
    """
    Configuration for a SAGE session.

    Attributes:
        model: LLM model identifier (e.g., "gpt-4o", "claude-3-opus").
        max_tokens: Maximum tokens per completion.
        temperature: Sampling temperature between 0.0 and 2.0.
    """

    model: str = "gpt-4o"
    max_tokens: int = 4096
    temperature: float = 0.7

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("Model identifier cannot be empty")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be a positive integer")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")


@dataclass(frozen=True)
class Message:
    """
    A message produced by an agent during problem solving.

    Attributes:
        agent_name: Name of the agent who produced this message.
        role: The agent's role.
        phase: Workflow phase when this message was created.
        content: The message content.
        timestamp: ISO format timestamp of creation.
    """

    agent_name: str
    role: str
    phase: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "agent_name": self.agent_name,
            "role": self.role,
            "phase": self.phase,
            "content": self.content,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class AgentContribution:
    """
    Summary of an agent's contribution to the solution.

    Attributes:
        agent_name: Name of the contributing agent.
        role: The agent's role.
        key_points: Main insights from this agent's analysis.
        messages: All messages produced by this agent.
    """

    agent_name: str
    role: str
    key_points: str
    messages: Tuple[Message, ...]


@dataclass(frozen=True)
class Result:
    """
    Complete result from a SAGE problem-solving session.

    Attributes:
        task: The original problem or question.
        summary: Synthesized solution combining all perspectives.
        contributions: Individual agent contributions.
        messages: Complete message history from all phases.
        model: LLM model used for this session.
        total_agents: Number of agents involved.
        phases_completed: Number of workflow phases completed.
        timestamp: ISO format timestamp of completion.
    """

    task: str
    summary: str
    contributions: Tuple[AgentContribution, ...]
    messages: Tuple[Message, ...]
    model: str
    total_agents: int
    phases_completed: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation for JSON serialization."""
        return {
            "task": self.task,
            "summary": self.summary,
            "contributions": [
                {
                    "agent_name": c.agent_name,
                    "role": c.role,
                    "key_points": c.key_points,
                }
                for c in self.contributions
            ],
            "messages": [m.to_dict() for m in self.messages],
            "metadata": {
                "model": self.model,
                "total_agents": self.total_agents,
                "phases_completed": self.phases_completed,
                "timestamp": self.timestamp,
            },
        }
