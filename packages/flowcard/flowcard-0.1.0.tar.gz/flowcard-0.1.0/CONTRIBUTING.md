# Contributing to FlowCard

Thank you for your interest in contributing to FlowCard! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of HTML, Markdown, and Python packaging

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/flowcard.git
   cd flowcard
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## 📝 Code Style Guidelines

FlowCard follows strict coding standards to maintain consistency and quality:

### Python Standards
- **Python Version**: Target Python 3.11+
- **Type Hints**: All functions must have complete type annotations
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Code Style**: Follow PEP 8 with Black formatting
- **Import Order**: Use isort for consistent import organization

### Function Calls
Always use keyword arguments when calling functions with multiple parameters:

```python
# Good
component = TextComponent(
    content="Hello World",
    tag="h1",
    attributes={"class": "title"}
)

# Avoid
component = TextComponent("Hello World", "h1", {"class": "title"})
```

### Documentation Requirements
All public functions and classes must include:

```python
def process_component(content: str, component_type: str = "text") -> str:
    """Process a component and return formatted output.
    
    Args:
        content: The content to be processed.
        component_type: The type of component to create. Defaults to "text".
        
    Returns:
        The formatted output string.
        
    Raises:
        ValueError: If content is empty or component_type is invalid.
        ComponentError: If component processing fails.
    """
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=flowcard

# Run specific test file
pytest tests/test_components.py
```

### Writing Tests
- Use descriptive test names that explain the behavior being tested
- Include both positive and negative test cases
- Test edge cases and error conditions
- Use fixtures for common test data

Example test structure:
```python
def test_title_component_creates_h1_element():
    """Test that title component generates correct H1 HTML."""
    component = TitleComponent(content="Test Title")
    result = component.to_html()
    assert "<h1>Test Title</h1>" in result["body"]

def test_title_component_raises_error_with_empty_content():
    """Test that title component raises ValueError for empty content."""
    with pytest.raises(ValueError, match="Content cannot be empty"):
        TitleComponent(content="")
```

## 🏗️ Architecture Guidelines

### Component Structure
All components should inherit from the base `Component` class and implement:

- `to_html()` -> dict with "head" and "body" keys
- `to_markdown()` -> str
- `validate()` -> None (raises exceptions if invalid)

### Adding New Components

1. Create the component class in `flowcard/components/`
2. Add comprehensive tests in `tests/components/`
3. Update the component registry
4. Add documentation examples
5. Update the README if it's a major component

### Export Format Support
When adding new export formats:

1. Create a new template in `flowcard/templates/`
2. Add the export method to the main Flowcard class
3. Ensure all existing components support the new format
4. Add comprehensive tests for the new format

## 📋 Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow the coding standards above
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Quality Checks**
   ```bash
   # Format code
   black flowcard tests
   
   # Sort imports
   isort flowcard tests
   
   # Type checking
   mypy flowcard
   
   # Run tests
   pytest --cov=flowcard
   
   # Lint code
   flake8 flowcard tests
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new component for data tables"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
Use conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `style:` for formatting changes

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Environment Information**
   - Python version
   - FlowCard version
   - Operating system

2. **Clear Description**
   - What you expected to happen
   - What actually happened
   - Steps to reproduce

3. **Code Examples**
   - Minimal reproducible example
   - Error messages and stack traces

4. **Additional Context**
   - Screenshots if relevant
   - Related issues or PRs

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check existing issues to avoid duplicates
2. Clearly describe the use case
3. Provide examples of how the feature would be used
4. Consider the impact on existing functionality

## 🏆 Recognition

Contributors will be recognized in:
- The project README
- Release notes for their contributions
- The project's contributor page

## 📞 Getting Help

- **Documentation**: Check the README and docstrings first
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Code Review**: Don't hesitate to ask for feedback on your PR

## 📄 License

By contributing to FlowCard, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to FlowCard! 🚀