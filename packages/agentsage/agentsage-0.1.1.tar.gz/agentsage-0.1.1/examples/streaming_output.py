"""
Streaming output example.

Shows how to use callbacks to stream agent responses in real-time.
"""

from sage import Sage, Agent


def on_phase_change(phase: str) -> None:
    """Called when SAGE enters a new phase."""
    print(f"\n{'=' * 50}")
    print(f"  PHASE: {phase.upper()}")
    print('=' * 50)


def on_agent_message(name: str, role: str, content: str) -> None:
    """Called when an agent produces a message."""
    print(f"\n[{name}] ({role}):")
    # Truncate long messages for display
    if len(content) > 500:
        print(f"  {content[:500]}...")
    else:
        print(f"  {content}")


def main():
    # Create SAGE with callbacks for real-time output
    sage = Sage(model="gpt-4o", temperature=0.7)
    sage.on_phase(on_phase_change)
    sage.on_message(on_agent_message)

    agents = [
        Agent(role="analyst", focus="Break down the problem into components"),
        Agent(role="innovator", focus="Generate creative solutions"),
        Agent(role="pragmatist", focus="Evaluate feasibility and implementation"),
    ]

    task = "How can a small team effectively compete with larger companies in the AI space?"

    print("\nSAGE: Synchronized Agents for Generalized Expertise")
    print("=" * 50)
    print(f"Task: {task}")
    print(f"Model: gpt-4o")

    result = sage.solve(task, agents)

    print("\n" + "=" * 50)
    print("  FINAL SUMMARY")
    print("=" * 50)
    print(f"\n{result.summary}")

    # Access detailed results
    print(f"\nStats: {result.total_agents} agents, {result.phases_completed} phases")


if __name__ == "__main__":
    main()
