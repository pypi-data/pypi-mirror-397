# GitHub Copilot Instructions for FlowCard Project

## General Guidelines

This is a Python package project called "flowcard" that deals with card, HTML, and markdown functionality.

## Python Version and Compatibility
- **Target Python version: 3.11+**
- Use modern Python features available in 3.11+
- Leverage new typing features and performance improvements

## Python Coding Standards

### Function and Method Calls
- **Always use keyword arguments instead of positional arguments** when calling functions or methods, especially when there are multiple parameters
- This improves code readability and maintainability

Example:
```python
# Preferred
setup(
    name='flowcard',
    version='0.0.1',
    description='Card HTML markdown package',
    packages=['flowcard'],
    python_requires='>=3.11'
)

# Avoid
setup('flowcard', '0.0.1', 'Card HTML markdown package', ['flowcard'])
```

### Documentation Standards
- **Use Google-style docstrings** for all functions, classes, and modules
- Include type information in docstrings
- Document all parameters, returns, and exceptions

Example:
```python
def process_card(content: str, card_type: str = "default") -> str:
    """Process card content and return formatted HTML.
    
    Args:
        content: The raw content to be processed.
        card_type: The type of card to generate. Defaults to "default".
        
    Returns:
        The formatted HTML string for the card.
        
    Raises:
        ValueError: If content is empty or card_type is invalid.
    """
    pass
```

### Type Hints and Modern Python Features
- Use type hints for all function parameters and return values
- Leverage Python 3.11+ features like:
  - `Self` type for method chaining
  - `Literal` types for string enums
  - `TypedDict` for structured dictionaries
  - Exception groups and `ExceptionGroup`
  - New union syntax `X | Y` instead of `Union[X, Y]`

### Code Style and Best Practices
- Follow PEP 8 naming conventions
- Use descriptive variable and function names
- Prefer f-strings for string formatting
- Use list/dict comprehensions when appropriate
- Add proper error handling with specific exception types
- Use `pathlib.Path` instead of `os.path` for file operations
- Prefer `match/case` statements for complex conditionals (Python 3.10+ feature)

### Project-Specific Guidelines
- Package name: flowcard
- Main functionality: Card, HTML, and markdown processing
- Use semantic versioning
- Include unit tests for new features
- Add logging where appropriate using the `logging` module

## Code Generation Preferences
- Generate code compatible with Python 3.11+
- Include comprehensive docstrings in Google format
- Add appropriate type hints
- Suggest unit tests when implementing new features
- Use modern Python idioms and features
- Include proper error handling with descriptive messages

## Dependencies and Packaging
- Use `pyproject.toml` as the primary configuration file
- Specify `python_requires = ">=3.11"`
- Use modern packaging tools and standards
- Keep dependencies minimal and well-justified
- When running command in terminal, use the package manager to precise the venv (like `uv run python ...` rather than just `python ...`)