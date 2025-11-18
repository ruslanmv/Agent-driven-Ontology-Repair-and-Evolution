# Contributing to ADORE

Thank you for your interest in contributing to **ADORE** (Agent-Driven Ontology Repair and Evolution)! We welcome contributions from the community and are excited to collaborate with you.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful, inclusive environment. We follow the principles of:
- **Respect**: Treat all contributors with respect
- **Collaboration**: Work together constructively
- **Openness**: Be open to feedback and new ideas
- **Inclusivity**: Welcome contributors from all backgrounds

---

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (Python version, OS, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

We love new ideas! When suggesting enhancements:
- Use a clear, descriptive title
- Provide detailed explanation of the feature
- Explain why this enhancement would be useful
- Include examples or mockups if applicable

### Contributing Code

1. Check existing issues and PRs to avoid duplicates
2. Fork the repository
3. Create a feature branch
4. Make your changes
5. Submit a pull request

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- `uv` (recommended) or `pip`
- Java 17+ (for OWL reasoning)
- Git

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Agent-driven-Ontology-Repair-and-Evolution.git
cd Agent-driven-Ontology-Repair-and-Evolution

# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
make dev-install

# Verify installation
make test
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
make test

# Run linting
make lint

# Run type checking
make type-check

# Run all checks (recommended before committing)
make ci
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Clear, descriptive commit message"
```

See [Commit Messages](#commit-messages) for guidelines.

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## Code Standards

### Python Style

We use **Ruff** for linting and formatting:

```bash
# Format code
make format

# Check for issues
make lint
```

### Type Hints

- **100% type coverage required**
- Use Python 3.10+ type syntax
- Run `mypy` before committing:

```bash
make type-check
```

### Documentation

All public APIs must have **Google-style docstrings**:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of the function.

    Longer description if needed, explaining what the function does,
    any important details, and usage examples.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is negative.

    Example:
        >>> example_function("test", 5)
        True
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    return len(param1) > param2
```

---

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Mirror the source structure
- Use `pytest` fixtures for setup
- Aim for >80% code coverage

Example test structure:

```python
"""Tests for module_name."""

import pytest
from adore.module_name import SomeClass


@pytest.fixture
def sample_instance():
    """Create a sample instance for testing."""
    return SomeClass(param="value")


def test_basic_functionality(sample_instance):
    """Test basic functionality."""
    result = sample_instance.method()
    assert result == expected_value


def test_error_handling():
    """Test error handling."""
    with pytest.raises(ValueError):
        SomeClass(param="invalid")
```

### Running Tests

```bash
# All tests
make test

# Specific file
pytest tests/test_agents.py -v

# With coverage report
pytest --cov=src/adore --cov-report=html
```

---

## Documentation

### Code Documentation

- **All public functions/classes**: Docstrings required
- **Complex logic**: Inline comments
- **Examples**: Provide usage examples in docstrings

### README Updates

If your change affects usage:
- Update the main README.md
- Add examples if applicable
- Update CLI help text

---

## Commit Messages

### Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic changes)
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Examples

```
feat: Add async support to LLM service

Implement asynchronous LLM invocations using asyncio.
This improves performance when running multiple cycles
concurrently.

Closes #123
```

```
fix: Resolve ontology duplication memory leak

Properly close isolated worlds after consistency checks
to prevent memory accumulation.

Fixes #456
```

---

## Pull Request Process

### Before Submitting

1. ✅ All tests pass (`make test`)
2. ✅ Code is formatted (`make format`)
3. ✅ Type checks pass (`make type-check`)
4. ✅ Linting passes (`make lint`)
5. ✅ Documentation updated
6. ✅ CHANGELOG.md updated (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] All tests pass locally
```

### Review Process

1. Automated CI checks must pass
2. At least one maintainer review required
3. Address review comments
4. Squash commits if requested
5. Maintainer will merge when ready

---

## Getting Help

- **Documentation**: Check README.md and code docstrings
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions for questions
- **Contact**: Reach out to maintainers

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Acknowledged in academic publications (if applicable)

---

## License

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**.

---

## Thank You!

Your contributions make ADORE better for everyone. We appreciate your time and effort! 🎉

