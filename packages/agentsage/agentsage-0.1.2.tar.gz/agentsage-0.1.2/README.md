<p align="center">
  <img src="assets/SAGE.png" alt="SAGE - Synchronized Agents for Generalized Expertise" width="800">
</p>

<p align="center">
  <strong>A multi-agent framework where AI agents research, debate, and synthesize answers together.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/agentsage/"><img src="https://img.shields.io/pypi/v/agentsage.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/agentsage/"><img src="https://img.shields.io/pypi/pyversions/agentsage.svg" alt="Python versions"></a>
  <a href="https://github.com/najmulhasan-code/sage/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://github.com/najmulhasan-code/sage/stargazers"><img src="https://img.shields.io/github/stars/najmulhasan-code/sage.svg" alt="GitHub stars"></a>
</p>

<p align="center">
  <a href="#installation">Installation</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#how-it-works">How It Works</a> &bull;
  <a href="#python-api">Python API</a> &bull;
  <a href="#supported-models">Models</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

---

## Why SAGE?

When you ask a single LLM a question, you get one perspective. **SAGE creates a team of specialized agents** that approach problems from different angles:

| Phase | What Happens |
|-------|--------------|
| **Research** | Each agent independently analyzes the problem using web search and file reading |
| **Discussion** | Agents review findings, challenge assumptions, and debate approaches |
| **Synthesis** | Insights are combined into a comprehensive, balanced answer |

This produces more thorough analysis than any single prompt could achieve.

```bash
sage "What database should I use for a high-traffic e-commerce platform?"
```

---

## Installation

```bash
pip install agentsage
```

For additional LLM providers:

```bash
pip install agentsage[anthropic]    # Claude models
pip install agentsage[google]       # Gemini models
pip install agentsage[ollama]       # Local models
pip install agentsage[all]          # All providers
```

---

## Quick Start

### 1. Set your API key

```bash
export OPENAI_API_KEY=sk-...
```

Or create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
```

### 2. Run SAGE

```bash
sage "What are the pros and cons of microservices vs monolithic architecture?"
```

That's it. SAGE assembles a default team (researcher, critic, strategist), runs the three-phase workflow, and returns a synthesized answer.

---

## How It Works

SAGE orchestrates multiple AI agents through a structured workflow powered by [LangGraph](https://github.com/langchain-ai/langgraph):

```
                         SAGE WORKFLOW

  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │  RESEARCH    │    │  DISCUSSION  │    │  SYNTHESIS   │
  │              │    │              │    │              │
  │  Agent 1 ────┼───►│  Agent 1 ────┼───►│              │
  │  Agent 2 ────┼───►│  Agent 2 ────┼───►│   Combined   │
  │  Agent 3 ────┼───►│  Agent 3 ────┼───►│    Answer    │
  │              │    │              │    │              │
  │  Web Search  │    │  Code Exec   │    │              │
  │  File Read   │    │  Validation  │    │              │
  └──────────────┘    └──────────────┘    └──────────────┘
```

### Phase 1: Research

Each agent independently analyzes the problem from their unique perspective. They can use tools:
- **Web Search**: Search the internet for current information
- **File Reading**: Read local files for context
- **Directory Listing**: Explore project structures

### Phase 2: Discussion

Agents review each other's findings and engage in structured debate:
- Challenge assumptions and identify gaps
- Validate technical claims with code execution
- Build on each other's insights

### Phase 3: Synthesis

All perspectives are combined into a final answer that:
- Addresses the original question directly
- Incorporates diverse viewpoints
- Provides actionable recommendations

---

## CLI Usage

```bash
# Basic usage
sage "What are the trade-offs between GraphQL and REST?"

# Custom agent team
sage "Review this code for security issues" --agents security,performance,reviewer

# Different models
sage "Explain quantum computing" --model gpt-4o-mini
sage "Complex analysis task" --model claude-sonnet-4-5 --provider anthropic

# Local models with Ollama
sage "Summarize this document" --model llama3.2:latest --provider ollama

# Control tools
sage "Simple question" --no-tools
sage "Research task" --no-code-exec
sage "Code review" --no-web-search

# Output formats
sage "Compare options" --json
sage "Debug this" --verbose
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--model` | Model to use (default: `gpt-4o`) |
| `--provider` | LLM provider: `openai`, `anthropic`, `google`, `ollama` |
| `--agents` | Comma-separated agent roles (default: `researcher,critic,strategist`) |
| `--temperature` | Sampling temperature 0.0-2.0 (default: 0.7) |
| `--no-tools` | Disable all agent tools |
| `--no-web-search` | Disable web search |
| `--no-code-exec` | Disable code execution |
| `--no-file-read` | Disable file reading |
| `--json` | Output as JSON |
| `--verbose` | Show detailed output with tool calls |
| `--quiet` | Suppress progress output |

---

## Python API

### Basic Usage

```python
from sage import Sage, Agent

sage = Sage(model="gpt-4o")

agents = [
    Agent(role="researcher", focus="Gather relevant facts and data"),
    Agent(role="critic", focus="Identify flaws, risks, and counterarguments"),
    Agent(role="strategist", focus="Propose practical solutions"),
]

result = sage.solve(
    "How should we handle authentication in our microservices?",
    agents
)

print(result.summary)
```

### Custom Agent Teams

```python
# Security review team
security_team = [
    Agent(role="security_analyst", focus="Identify vulnerabilities and attack vectors"),
    Agent(role="compliance_expert", focus="Check regulatory requirements (GDPR, SOC2)"),
    Agent(role="penetration_tester", focus="Think like an attacker"),
]

# Architecture review team
architecture_team = [
    Agent(role="system_architect", focus="Evaluate scalability and design patterns"),
    Agent(role="devops_engineer", focus="Consider deployment and infrastructure"),
    Agent(role="performance_engineer", focus="Identify bottlenecks and optimizations"),
]

result = sage.solve("Review our authentication system design", security_team)
```

### Real-Time Callbacks

```python
sage = Sage(model="gpt-4o")

# Track progress in real-time
sage.on_phase(lambda phase: print(f"Entering: {phase}"))
sage.on_message(lambda name, role, content: print(f"[{name}] {content[:100]}..."))
sage.on_tool_call(lambda agent, tool, args: print(f"{agent} used {tool}"))

result = sage.solve(task, agents)
```

### Configuration Options

```python
sage = Sage(
    model="gpt-4o",           # Model identifier
    provider=None,            # Auto-detected from model name
    temperature=0.7,          # Creativity (0.0-2.0)
    max_tokens=4096,          # Max response length
    tools_enabled=True,       # Enable agent tools
    web_search=True,          # Web search capability
    code_execution=True,      # Python code execution
    file_reading=True,        # Local file access
)
```

### Result Structure

```python
result = sage.solve(task, agents)

# Access the synthesized answer
print(result.summary)

# Get individual agent contributions
for contribution in result.contributions:
    print(f"{contribution.agent_name}: {contribution.key_points}")

# Export as JSON
import json
print(json.dumps(result.to_dict(), indent=2))

# Metadata
print(f"Model: {result.model}")
print(f"Agents: {result.total_agents}")
print(f"Phases: {result.phases_completed}")
```

---

## Supported Models

SAGE works with **any model** from supported providers, just pass the model name and it works.

| Provider | Models | Setup |
|----------|--------|-------|
| **OpenAI** | `gpt-5`, `gpt-5-mini`, `o3`, `o3-pro`, `o4-mini`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini` | `OPENAI_API_KEY` |
| **Anthropic** | `claude-opus-4-5`, `claude-sonnet-4-5`, `claude-haiku-4-5`, `claude-opus-4`, `claude-sonnet-4` | `ANTHROPIC_API_KEY` |
| **Google** | `gemini-3-flash-preview`, `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-flash` | `GOOGLE_API_KEY` |
| **Ollama** | `deepseek-r1`, `llama3.2`, `llama3.1`, `qwen3`, `qwen2.5`, `mistral`, `gemma3`, `codellama`, `phi4` | Local installation |

The provider is auto-detected from the model name:

```python
# Auto-detected as OpenAI
sage = Sage(model="gpt-5")

# Auto-detected as Anthropic
sage = Sage(model="claude-sonnet-4-5")

# Auto-detected as Google
sage = Sage(model="gemini-2.5-flash")

# Auto-detected as Ollama (has colon)
sage = Sage(model="llama3.2:latest")
```

---

## Project Structure

```
sage/
├── src/sage/
│   ├── __init__.py          # Package exports
│   ├── core.py              # Main Sage class
│   ├── types.py             # Data types (Agent, Config, Result)
│   ├── cli.py               # Command-line interface
│   ├── graph/
│   │   ├── state.py         # LangGraph state schema
│   │   └── workflow.py      # Workflow definition
│   ├── agents/
│   │   ├── base.py          # SageAgent with tool support
│   │   └── nodes.py         # Phase node functions
│   ├── tools/
│   │   ├── web_search.py    # DuckDuckGo/Tavily search
│   │   ├── code_exec.py     # Python REPL
│   │   └── file_reader.py   # File operations
│   └── providers/
│       └── factory.py       # Multi-provider model factory
└── examples/
    ├── basic_usage.py       # Simple usage example
    ├── custom_agents.py     # Custom agent teams
    ├── multi_provider.py    # Using different LLM providers
    ├── streaming_output.py  # Real-time callbacks
    └── json_output.py       # JSON output format
```

---

## Built-in Agent Roles

SAGE includes predefined focuses for common roles:

| Role | Default Focus |
|------|---------------|
| `researcher` | Gather relevant facts and information |
| `critic` | Identify potential flaws, risks, and counterarguments |
| `strategist` | Propose practical solutions and next steps |
| `analyst` | Analyze data and identify patterns |
| `creative` | Generate novel ideas and alternative approaches |
| `technical` | Evaluate technical feasibility and implementation details |
| `reviewer` | Review for completeness and quality |
| `security` | Identify security vulnerabilities and risks |
| `performance` | Analyze performance implications and optimizations |

Or create your own:

```python
Agent(role="your_role", focus="Your specific instructions")
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

```bash
# Clone the repository
git clone https://github.com/najmulhasan-code/sage.git
cd sage

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/ --fix

# Type check
mypy src/sage/
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

