"""
Custom agents example.

Shows how to create specialized agents for domain-specific problems.
"""

from sage import Sage, Agent


def code_review_team():
    """Agents specialized for code review."""
    return [
        Agent(
            role="security_analyst",
            focus="Identify security vulnerabilities, injection risks, and authentication issues",
        ),
        Agent(
            role="performance_engineer",
            focus="Spot performance bottlenecks, memory leaks, and optimization opportunities",
        ),
        Agent(
            role="maintainability_expert",
            focus="Evaluate code readability, design patterns, and long-term maintenance concerns",
        ),
    ]


def business_strategy_team():
    """Agents specialized for business decisions."""
    return [
        Agent(
            role="market_analyst",
            focus="Analyze market trends, competition, and customer needs",
        ),
        Agent(
            role="financial_advisor",
            focus="Evaluate costs, revenue potential, and financial risks",
        ),
        Agent(
            role="operations_expert",
            focus="Assess implementation feasibility and operational requirements",
        ),
    ]


def research_team():
    """Agents specialized for research analysis."""
    return [
        Agent(
            role="domain_expert",
            focus="Provide deep technical knowledge and state-of-the-art insights",
        ),
        Agent(
            role="methodologist",
            focus="Evaluate research methods, experimental design, and validity",
        ),
        Agent(
            role="synthesizer",
            focus="Connect findings to broader context and practical applications",
        ),
    ]


def main():
    sage = Sage(model="gpt-4o")

    # Example: Use the code review team
    print("Code Review Analysis")
    print("=" * 50)

    task = """
    Review this Python function for issues:

    def process_user_input(data):
        query = f"SELECT * FROM users WHERE id = {data['user_id']}"
        result = db.execute(query)
        return eval(data['callback'])(result)
    """

    result = sage.solve(task, code_review_team())
    print(result.summary)


if __name__ == "__main__":
    main()
