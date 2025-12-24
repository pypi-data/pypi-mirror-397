"""
Command-line interface for SAGE.

Usage:
    sage "Your task here"
    sage "Your task" --model gpt-4o-mini
    sage "Your task" --model claude-3-opus-20240229 --provider anthropic
    sage "Your task" --agents researcher,critic,strategist
    sage "Your task" --no-tools
"""

import argparse
import sys
import json
import warnings
from typing import List

# Suppress Python REPL warning for cleaner output
warnings.filterwarnings("ignore", message=".*can execute arbitrary code.*")

# Auto-load .env file for API keys
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.live import Live

from .core import Sage
from .types import Agent
from . import __version__


console = Console()


# ASCII art banner - matches the SAGE branding (Windows-compatible)
SAGE_BANNER = """[bold green]
   ____    _    ____ _____
  / ___|  / \\  / ___| ____|
  \\___ \\ / _ \\| |  _|  _|
   ___) / ___ \\ |_| | |___
  |____/_/   \\_\\____|_____|
[/bold green]
[dim]  Synchronized Agents for Generalized Expertise[/dim]"""


def print_welcome() -> None:
    """Print the welcome banner with usage information."""
    console.print(SAGE_BANNER)
    console.print()
    console.print(f"  [dim]Version:[/dim] [green]{__version__}[/green]")
    console.print()
    console.print("  [bold]Usage:[/bold]")
    console.print('    sage "Your question or task here"')
    console.print()
    console.print("  [bold]Examples:[/bold]")
    console.print('    sage "What are the pros and cons of microservices?"')
    console.print('    sage "Review this code for security issues" --agents security,performance')
    console.print('    sage "Explain quantum computing" --model gpt-4o-mini')
    console.print()
    console.print("  [bold]Options:[/bold]")
    console.print("    --model       Model to use (default: gpt-4o)")
    console.print("    --provider    LLM provider (openai, anthropic, google, ollama)")
    console.print("    --agents      Custom agent roles (comma-separated)")
    console.print("    --verbose     Show detailed agent activity")
    console.print("    --help        Show all options")
    console.print()
    console.print("  [dim]Set your API key:[/dim]")
    console.print("    export OPENAI_API_KEY=sk-...")
    console.print()
    console.print("  [dim]Documentation:[/dim] [link]https://github.com/najmulhasan-code/sage[/link]")
    console.print()


class ActivityLog:
    """Track and display real agent activity - what they're actually doing."""

    def __init__(self):
        self.activities = []  # List of activity strings
        self.current_phase = ""
        self.current_agent = ""
        self.max_activities = 8  # Keep last N activities visible

    def on_phase(self, phase: str):
        """Called when entering a new phase."""
        if phase == "complete":
            return
        self.current_phase = phase
        phase_labels = {"research": "Research", "discuss": "Discussion", "synthesize": "Synthesis"}
        self.activities.append(("phase", f"Starting {phase_labels.get(phase, phase)} phase..."))

    def on_agent_start(self, name: str, role: str):
        """Called when an agent starts working."""
        self.current_agent = name
        self.activities.append(("agent", f"{name} ({role}) is analyzing..."))

    def on_agent_done(self, name: str, role: str, content: str):
        """Called when an agent completes - show key insight."""
        # Extract first meaningful line as a preview
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
        preview = lines[0][:60] + "..." if lines and len(lines[0]) > 60 else (lines[0] if lines else "Done")
        self.activities.append(("done", f"{name}: {preview}"))

    def on_tool_call(self, agent: str, tool: str, args: dict):
        """Called when a tool is invoked - show what's happening."""
        if tool == "duckduckgo_search":
            query = args.get("query", args.get("tool_input", ""))[:40]
            self.activities.append(("tool", f"  Searching: \"{query}\""))
        elif tool == "read_file":
            path = args.get("file_path", args.get("tool_input", ""))
            self.activities.append(("tool", f"  Reading: {path}"))
        elif tool == "list_directory":
            path = args.get("dir_path", args.get("tool_input", "."))
            self.activities.append(("tool", f"  Listing: {path}"))
        elif tool == "Python_REPL":
            self.activities.append(("tool", f"  Running Python code..."))
        else:
            self.activities.append(("tool", f"  Using {tool}..."))

    def render(self) -> Text:
        """Render current activity log."""
        text = Text()
        text.append("\n")

        # Show recent activities
        recent = self.activities[-self.max_activities:] if len(self.activities) > self.max_activities else self.activities

        for activity_type, message in recent:
            if activity_type == "phase":
                text.append(f"  {message}\n", style="bold white")
            elif activity_type == "agent":
                text.append(f"  {message}\n", style="white")
            elif activity_type == "tool":
                text.append(f"  {message}\n", style="dim")
            elif activity_type == "done":
                text.append(f"  {message}\n", style="green")

        # Add a blank line at the end
        text.append("\n")
        return text

# Simple color scheme - professional and neutral
AGENT_COLORS = ["white", "white", "white", "white", "white", "white"]

# Phase styles - just numbered, no colors
PHASE_STYLES = {
    "research": ("white", "1"),
    "discuss": ("white", "2"),
    "synthesize": ("white", "3"),
}


DEFAULT_AGENTS = [
    Agent(role="researcher", focus="Gather relevant facts and information"),
    Agent(role="critic", focus="Identify potential flaws, risks, and counterarguments"),
    Agent(role="strategist", focus="Propose practical solutions and next steps"),
]


def parse_agents(agent_string: str) -> List[Agent]:
    """
    Parse a comma-separated list of agent roles.

    Args:
        agent_string: Comma-separated roles (e.g., "researcher,critic,strategist")

    Returns:
        List of Agent instances with default focuses.
    """
    roles = [r.strip() for r in agent_string.split(",")]

    role_focuses = {
        "researcher": "Gather relevant facts and information",
        "critic": "Identify potential flaws, risks, and counterarguments",
        "strategist": "Propose practical solutions and next steps",
        "analyst": "Analyze data and identify patterns",
        "creative": "Generate novel ideas and alternative approaches",
        "technical": "Evaluate technical feasibility and implementation details",
        "reviewer": "Review for completeness and quality",
        "security": "Identify security vulnerabilities and risks",
        "performance": "Analyze performance implications and optimizations",
    }

    agents = []
    for role in roles:
        focus = role_focuses.get(role, f"Provide {role} perspective and insights")
        agents.append(Agent(role=role, focus=focus))

    return agents


def get_agent_color(index: int) -> str:
    """Get color for agent by index."""
    return AGENT_COLORS[index % len(AGENT_COLORS)]


def print_header(task: str, model: str, provider: str, agents: List[Agent], tools: List[str]) -> None:
    """Print the SAGE header with task info."""
    # Main header - sage green color
    header = Text()
    header.append("SAGE", style="bold green")
    header.append(" - Synchronized Agents for Generalized Expertise", style="dim")

    console.print()
    console.print(Panel(header, border_style="green"))

    # Info table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("Task", Text(task, style="bold white"))
    table.add_row("Model", Text(model + (f" ({provider})" if provider else ""), style="cyan"))

    # Agents with colors
    agent_text = Text()
    for i, agent in enumerate(agents):
        if i > 0:
            agent_text.append(", ")
        agent_text.append(agent.role, style=get_agent_color(i))
    table.add_row("Agents", agent_text)

    # Tools
    if tools:
        table.add_row("Tools", Text(", ".join(tools), style="green"))
    else:
        table.add_row("Tools", Text("disabled", style="dim"))

    console.print(table)
    console.print()


def print_phase(phase: str) -> None:
    """Print phase transition (only in verbose mode)."""
    if phase == "complete":
        return  # Don't print complete phase
    style, number = PHASE_STYLES.get(phase, ("white", "-"))
    console.print()
    console.print(f"[dim][{number}] {phase.upper()}[/dim]")


def print_message(name: str, role: str, content: str, agent_index: int = 0) -> None:
    """Print agent message (compact format for verbose mode)."""
    color = get_agent_color(agent_index)

    # Truncate content for display
    lines = content.split('\n')
    if len(lines) > 10:
        display_content = '\n'.join(lines[:10])
        display_content += f"\n[dim]... ({len(lines) - 10} more lines)[/dim]"
    else:
        display_content = content

    console.print(f"\n[{color}]{name}[/{color}] [dim]({role})[/dim]")
    console.print(f"[dim]{display_content[:500]}{'...' if len(display_content) > 500 else ''}[/dim]")


def print_tool_call(agent: str, tool: str, args: dict) -> None:
    """Print tool invocation."""
    args_str = json.dumps(args) if args else "{}"
    if len(args_str) > 80:
        args_str = args_str[:80] + "..."

    console.print(f"  [dim]> {tool}[/dim]({args_str})", style="dim")


def print_compact_header(task: str) -> None:
    """Print a compact header for normal mode."""
    console.print()
    header = Text()
    # Sage green color to match the SAGE branding
    header.append("SAGE", style="bold green")
    console.print(Panel(header, border_style="green", padding=(0, 1)))
    console.print(f"  [dim]Task:[/dim] {task[:80]}{'...' if len(task) > 80 else ''}")


def print_result(result) -> None:
    """Print the final result - clean and simple like ChatGPT."""
    console.print()

    # Render the summary as markdown
    md = Markdown(result.summary)
    console.print(md)

    # Simple footer
    console.print()
    console.print(f"[dim]Model: {result.model} | Agents: {result.total_agents}[/dim]")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SAGE: Synchronized Agents for Generalized Expertise",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    sage "What are the pros and cons of microservices?"
    sage "Review this code for issues" --model gpt-4o-mini
    sage "Analyze market trends" --agents researcher,analyst,strategist
    sage "Design a system" --json

Multi-provider examples:
    sage "Explain quantum computing" --model claude-3-opus-20240229 --provider anthropic
    sage "Local LLM test" --model llama2:latest --provider ollama
    sage "Use Gemini" --model gemini-pro --provider google

Tool control:
    sage "Simple question" --no-tools
    sage "Research task" --no-code-exec
    sage "Debug with verbose" --verbose
        """,
    )

    parser.add_argument(
        "task",
        type=str,
        nargs="?",
        default=None,
        help="The task or question to solve",
    )

    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version and exit",
    )

    # Model configuration
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="Model to use (default: gpt-4o)",
    )

    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["openai", "anthropic", "google", "ollama", "azure", "bedrock"],
        help="LLM provider (auto-detected from model if not specified)",
    )

    # Agent configuration
    parser.add_argument(
        "--agents",
        type=str,
        default=None,
        help="Comma-separated agent roles (default: researcher,critic,strategist)",
    )

    # Model parameters
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature 0.0-2.0 (default: 0.7)",
    )

    # Tool configuration
    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Disable all agent tools",
    )

    parser.add_argument(
        "--no-web-search",
        action="store_true",
        help="Disable web search tool",
    )

    parser.add_argument(
        "--no-code-exec",
        action="store_true",
        help="Disable code execution tool",
    )

    parser.add_argument(
        "--no-file-read",
        action="store_true",
        help="Disable file reading tool",
    )

    # Output configuration
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show tool calls and detailed output",
    )

    args = parser.parse_args()

    # Show version or welcome screen if no task provided
    if args.version:
        console.print(f"agentsage version {__version__}")
        return 0

    if args.task is None:
        print_welcome()
        return 0

    # Parse agents
    agents = parse_agents(args.agents) if args.agents else DEFAULT_AGENTS

    # Create SAGE instance
    try:
        sage = Sage(
            model=args.model,
            provider=args.provider,
            temperature=args.temperature,
            tools_enabled=not args.no_tools,
            web_search=not args.no_web_search,
            code_execution=not args.no_code_exec,
            file_reading=not args.no_file_read,
        )
    except ValueError as e:
        console.print(f"[red]Error initializing SAGE:[/red] {e}")
        return 1

    # Build tools list for display
    tools_list = []
    if not args.no_tools:
        if not args.no_web_search:
            tools_list.append("web_search")
        if not args.no_code_exec:
            tools_list.append("code_exec")
        if not args.no_file_read:
            tools_list.append("file_read")

    # Track agent index for colors
    agent_indices = {a.display_name: i for i, a in enumerate(agents)}

    # Set up callbacks - only show details in verbose mode
    if not args.quiet and not args.json:
        if args.verbose:
            # Verbose mode: show everything
            print_header(args.task, args.model, args.provider, agents, tools_list)
            sage.on_phase(print_phase)
            sage.on_message(lambda name, role, content: print_message(
                name, role, content, agent_indices.get(name, 0)
            ))
            sage.on_tool_call(print_tool_call)

    try:
        if args.json:
            result = sage.solve(args.task, agents)
            print(json.dumps(result.to_dict(), indent=2))
        elif args.verbose:
            result = sage.solve(args.task, agents)
            print_result(result)
        else:
            # Normal mode: show real activity
            print_compact_header(args.task)

            activity_log = ActivityLog()
            live_display = None

            def on_phase(phase: str):
                activity_log.on_phase(phase)
                if live_display:
                    live_display.update(activity_log.render())

            def on_agent(name: str, role: str, content: str):
                activity_log.on_agent_done(name, role, content)
                if live_display:
                    live_display.update(activity_log.render())

            def on_tool(agent: str, tool: str, tool_args: dict):
                activity_log.on_tool_call(agent, tool, tool_args)
                if live_display:
                    live_display.update(activity_log.render())

            sage.on_phase(on_phase)
            sage.on_message(on_agent)
            sage.on_tool_call(on_tool)

            with Live(activity_log.render(), console=console, refresh_per_second=4, transient=True) as live:
                live_display = live
                result = sage.solve(args.task, agents)

            print_result(result)

        return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        return 1
    except Exception as e:
        if args.verbose:
            console.print_exception()
        console.print(f"\n[red]Error:[/red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
