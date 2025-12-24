"""
Basic SAGE usage example.

Demonstrates the simplest way to use SAGE for problem solving.
"""

from sage import Sage, Agent


def main():
    # Create a SAGE instance with your preferred model
    sage = Sage(model="gpt-4o")

    # Define agents with different perspectives
    agents = [
        Agent(role="researcher", focus="Gather relevant facts and background information"),
        Agent(role="critic", focus="Identify potential flaws, risks, and counterarguments"),
        Agent(role="strategist", focus="Propose practical solutions and action items"),
    ]

    # Solve a problem
    task = "What are the key considerations when choosing between microservices and monolithic architecture for a startup?"

    print("SAGE: Synchronized Agents for Generalized Expertise")
    print("=" * 50)
    print(f"Task: {task}")
    print(f"Agents: {', '.join(a.role for a in agents)}")
    print("=" * 50)

    result = sage.solve(task, agents)

    print("\nFINAL RESULT:")
    print("-" * 50)
    print(result.summary)


if __name__ == "__main__":
    main()
