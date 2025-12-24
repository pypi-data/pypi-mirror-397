# Contributing to SAGE

Thank you for your interest in contributing to SAGE!

## Getting Started

### Development Setup

```bash
# Clone the repository
git clone https://github.com/najmulhasan-code/sage.git
cd sage

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Style

We use `black` for formatting and `ruff` for linting:

```bash
# Format code
black src/

# Check linting
ruff check src/

# Type checking
mypy src/
```

## How to Contribute

### Reporting Bugs

Open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS)

### Suggesting Features

Open an issue with:
- Description of the feature
- Use case / motivation
- Proposed implementation (if any)

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black src/ && ruff check src/`
6. Commit: `git commit -m "Add my feature"`
7. Push: `git push origin feature/my-feature`
8. Open a Pull Request

## Project Structure

```
src/sage/
├── core.py          # Main Sage class
├── types.py         # Data types
├── cli.py           # CLI interface
├── graph/           # LangGraph workflow
├── agents/          # Agent implementations
├── tools/           # Agent tools
└── providers/       # LLM providers
```

## Code Guidelines

- Write clear docstrings for public functions
- Add type hints to all functions
- Keep functions focused and small
- Write tests for new features

## Questions?

Open an issue or start a discussion. We're happy to help!
