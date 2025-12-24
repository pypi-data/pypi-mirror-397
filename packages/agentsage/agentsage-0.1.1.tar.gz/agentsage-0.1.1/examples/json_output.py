"""
JSON output example.

Shows how to get structured output from SAGE for programmatic use.
"""

import json
from sage import Sage, Agent


def main():
    sage = Sage(model="gpt-4o-mini")  # Use faster model for quick analysis

    agents = [
        Agent(role="technical", focus="Evaluate technical aspects and implementation"),
        Agent(role="business", focus="Assess business value and market fit"),
    ]

    task = "Should we build our own authentication system or use a third-party service like Auth0?"

    result = sage.solve(task, agents)

    # Convert to dictionary for JSON serialization
    output = result.to_dict()

    # Pretty print JSON output
    print(json.dumps(output, indent=2))

    # Access specific fields programmatically
    print("\n--- Programmatic Access ---")
    print(f"Task: {result.task}")
    print(f"Model used: {result.model}")
    print(f"Number of agents: {result.total_agents}")

    for contribution in result.contributions:
        print(f"\nAgent: {contribution.agent_name}")
        print(f"Key points: {contribution.key_points[:200]}...")


if __name__ == "__main__":
    main()
