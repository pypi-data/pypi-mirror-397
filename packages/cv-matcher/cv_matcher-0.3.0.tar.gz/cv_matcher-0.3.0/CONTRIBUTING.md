# Contributing to CV Matcher

Thank you for your interest in contributing to CV Matcher! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/cv-matcher.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=cv_matcher --cov-report=html

# Run specific test file
pytest tests/test_matcher.py -v
```

## Code Style

We use the following tools for code quality:

```bash
# Format code
black src/cv_matcher

# Lint code
ruff check src/cv_matcher

# Type checking
mypy src/cv_matcher
```

## Commit Guidelines

- Use clear, descriptive commit messages
- Follow conventional commits format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(parser): add support for DOCX files
fix(matcher): handle empty CV files gracefully
docs(readme): update installation instructions
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR with clear description

## Code Review

All submissions require review before merging. We'll review your PR for:

- Code quality and style
- Test coverage
- Documentation
- Breaking changes

## Questions?

Feel free to open an issue for any questions or concerns!
