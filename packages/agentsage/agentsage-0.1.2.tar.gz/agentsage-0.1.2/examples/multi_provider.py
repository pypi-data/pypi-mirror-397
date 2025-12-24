"""
Multi-provider example.

Shows how to use SAGE with different LLM providers.
"""

import os
from sage import Sage, Agent


def with_openai():
    """Use OpenAI GPT models."""
    sage = Sage(model="gpt-4o")

    agents = [
        Agent(role="researcher", focus="Gather relevant facts"),
        Agent(role="critic", focus="Identify potential issues"),
    ]

    result = sage.solve("What is the best approach for API versioning?", agents)
    return result


def with_anthropic():
    """Use Anthropic Claude models.

    Requires: pip install sage[anthropic]
    Environment: ANTHROPIC_API_KEY
    """
    sage = Sage(
        model="claude-3-opus-20240229",
        provider="anthropic",
    )

    agents = [
        Agent(role="architect", focus="Evaluate system design"),
        Agent(role="security", focus="Identify vulnerabilities"),
    ]

    result = sage.solve("Review this microservices architecture", agents)
    return result


def with_ollama():
    """Use Ollama for local models.

    Requires: pip install sage[ollama]
    Prerequisite: Ollama running locally with a model pulled
    """
    sage = Sage(
        model="llama2:latest",
        provider="ollama",
        tools_enabled=False,  # Local models may not support tools
    )

    agents = [
        Agent(role="analyst", focus="Analyze the situation"),
        Agent(role="advisor", focus="Provide recommendations"),
    ]

    result = sage.solve("What are key considerations for data privacy?", agents)
    return result


def with_google():
    """Use Google Gemini models.

    Requires: pip install sage[google]
    Environment: GOOGLE_API_KEY
    """
    sage = Sage(
        model="gemini-pro",
        provider="google",
    )

    agents = [
        Agent(role="researcher", focus="Research the topic"),
        Agent(role="synthesizer", focus="Combine insights"),
    ]

    result = sage.solve("Compare different cloud providers", agents)
    return result


def main():
    print("SAGE Multi-Provider Example")
    print("=" * 50)

    # Default: OpenAI
    if os.getenv("OPENAI_API_KEY"):
        print("\n[OpenAI GPT-4o]")
        result = with_openai()
        print(result.summary[:500] + "...")
    else:
        print("\nSkipping OpenAI (OPENAI_API_KEY not set)")

    # Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        print("\n[Anthropic Claude]")
        result = with_anthropic()
        print(result.summary[:500] + "...")
    else:
        print("\nSkipping Anthropic (ANTHROPIC_API_KEY not set)")

    # Google
    if os.getenv("GOOGLE_API_KEY"):
        print("\n[Google Gemini]")
        result = with_google()
        print(result.summary[:500] + "...")
    else:
        print("\nSkipping Google (GOOGLE_API_KEY not set)")


if __name__ == "__main__":
    main()
