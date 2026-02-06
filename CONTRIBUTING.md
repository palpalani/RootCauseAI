# Contributing to RootCauseAI

Thank you for your interest in contributing to RootCauseAI! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rootcauseai.git
   cd rootcauseai
   ```
3. **Set up the development environment**:
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync --dev
   ```

## Development Workflow

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following our coding standards:
   - Follow PEP 8 style guidelines (enforced by Ruff)
   - Add type hints to all functions
   - Write docstrings for all public functions and classes
   - Keep functions focused and small

3. **Run checks locally** before committing:
   ```bash
   # Format code
   uv run ruff format .
   
   # Lint code
   uv run ruff check .
   
   # Type check
   uv run mypy rootcauseai tests
   
   # Run tests
   uv run pytest
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   
   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `style:` for formatting changes
   - `refactor:` for code refactoring
   - `test:` for test additions/changes
   - `chore:` for maintenance tasks

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style

- Use Ruff for linting and formatting (configuration in `pyproject.toml`)
- Follow PEP 8 conventions
- Use type hints for all function parameters and return types
- Use `from __future__ import annotations` for forward references

### Code Organization

- Keep functions focused on a single responsibility
- Use descriptive variable and function names
- Add docstrings to all public functions, classes, and modules
- Group related functionality into modules

### Testing

- Write tests for all new features and bug fixes
- Aim for high test coverage
- Use pytest fixtures for test setup
- Mock external API calls in tests

### Documentation

- Update README.md if adding new features
- Add docstrings following Google style
- Update `.env.example` if adding new configuration options

## Pull Request Process

1. **Ensure all checks pass**:
   - Linting (Ruff)
   - Type checking (MyPy)
   - Tests (Pytest)
   - Security scans

2. **Update documentation** as needed

3. **Add tests** for new functionality

4. **Keep PRs focused** - one feature or fix per PR

5. **Request review** from maintainers

## Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Relevant logs or error messages

## Suggesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:
- Clear description of the feature
- Problem it solves
- Proposed solution
- Use cases

## Questions?

Feel free to open an issue for questions or reach out to maintainers.

Thank you for contributing! 🎉
