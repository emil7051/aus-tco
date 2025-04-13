# Development Guide

This guide outlines development standards and best practices for the Australian Heavy Vehicle TCO Modeller project.

## Code Quality Standards

### Style and Formatting

- **Python Version**: This project requires Python 3.9+
- **Code Formatting**: Use Black with a line length of 88 characters
- **Import Sorting**: Use isort with Black profile
- **Linting**: Follow PEP 8 guidelines, enforced through tools like flake8

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .
```

### Naming Conventions

- **Functions/Methods**: Use `snake_case` for function and method names
- **Classes**: Use `PascalCase` for class names
- **Constants**: Use `UPPER_SNAKE_CASE` for constants
- **Variables**: Use descriptive `snake_case` names that reveal intent
- **Private members**: Prefix with underscore (e.g., `_private_method`)

### TCO Model Field Naming Conventions

The TCO model uses specific naming conventions for key concepts. These are documented in `docs/naming_conventions.md` and standardized constants are available in `tco_model/terminology.py`.

Key naming standards:
- Use `total_tco` for the total cost of ownership (rather than `npv_total`)
- Use `lcod` for levelized cost of driving (rather than `lcod_per_km`)
- Use `tco_difference` for TCO comparisons (rather than `npv_difference`)
- Use `tco_percentage` for percentage differences (rather than `npv_difference_percentage`)

When adding new fields or methods, reference the terminology module for consistent naming.

### Clean Code Principles

- **Single Responsibility**: Each function and class should have a single responsibility
- **DRY (Don't Repeat Yourself)**: Extract repeated code into reusable functions
- **Function Size**: Keep functions small, typically under 30 lines
- **Argument Count**: Limit function arguments to 3-4; use data classes for more
- **Nested Conditionals**: Minimize deeply nested code (maximum 2-3 levels)
- **Magic Numbers**: Replace hard-coded values with named constants

## Documentation

### Docstrings

All modules, classes, methods, and functions must include docstrings following the Google style format.
See `docs/docstring_template.md` for examples and templates.

Key requirements:
- Module docstrings should describe the purpose and contents
- Class docstrings should describe purpose and list attributes
- Method/function docstrings need:
  - Brief description
  - Detailed explanation (if complex)
  - Args section
  - Returns section (if applicable)
  - Raises section (if applicable)
  - Example usage (where helpful)

### Comments

- Use comments sparingly and only to explain **why**, not **what**
- Complex logic should include comments explaining the reasoning
- Don't comment obvious code
- Keep comments current when changing code

### Project Documentation

- README.md should provide a comprehensive overview and quick start
- SETUP.md for detailed installation instructions
- API documentation should be generated from docstrings

## Type Checking

This project uses static type checking with mypy to improve code quality and catch errors early.

### Type Annotation Guidelines

- All function parameters and return types must be annotated
- Use appropriate types from the `typing` module
- Complex types should use type aliases for readability
- Provide annotations for class attributes
- Use Optional[T] for values that could be None

```python
from typing import Dict, List, Optional, Union, Tuple

# Good examples
def calculate_cost(distance: float, rate: float) -> float:
    return distance * rate

def find_vehicle(id_or_name: Union[int, str]) -> Optional[Vehicle]:
    ...

# Type aliases for complex types
CostBreakdown = Dict[str, float]
def get_costs() -> CostBreakdown:
    ...
```

### Running Type Checks

Run mypy checks regularly during development:

```bash
# Run mypy on the whole project
mypy .

# Run mypy on a specific file or directory
mypy tco_model/calculator.py
```

## Testing

### Test Coverage

- All core functionality should be covered by unit tests
- Aim for at least 80% code coverage
- Integration tests for complex component interactions

### Test Organization

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Test fixtures in `tests/fixtures/`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=tco_model

# Run specific test file
pytest tests/unit/test_calculator.py
```

## Git Workflow

### Commit Messages

Write clear, descriptive commit messages:

```
feat: Add battery degradation calculation

Add a new model for calculating battery degradation over time based on
usage patterns and charging cycles. This implements feature #123.
```

Use conventional commit prefixes:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding or modifying tests
- `chore:` for routine tasks, dependency updates, etc.

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch, should always be in a working state
- Feature branches - Named as `feature/feature-name`
- Bug fix branches - Named as `fix/bug-description`

## Development Workflow

1. **Setup**: Ensure your development environment is properly set up
2. **Branch**: Create a feature or fix branch from `develop`
3. **Develop**: Write code that adheres to all standards
4. **Test**: Run tests to ensure functionality and maintain coverage
5. **Type Check**: Run mypy to verify type correctness
6. **Format**: Run Black and isort before committing
7. **Document**: Ensure all new code is properly documented
8. **Pull Request**: Submit a PR with a clear description of changes
9. **Code Review**: Address feedback from code review

## Development Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/aus-tco.git
cd aus-tco

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install -r requirements-dev.txt

# 5. Set up pre-commit hooks
pre-commit install
```

## Streamlit Development Tips

When working with Streamlit components:

- Ensure proper state management with `st.session_state`
- Avoid unnecessary reruns which can slow down the application
- Organize UI components into logical modules
- Test UI changes interactively with `streamlit run app.py`

## Performance Considerations

- Profile code to identify bottlenecks
- Vectorize calculations with NumPy where possible
- Cache expensive computations with `@st.cache_data` or `@functools.lru_cache`
- Monitor memory usage with large datasets

## Additional Resources

- [Python Type Checking Guide](https://mypy.readthedocs.io/en/stable/)
- [Effective Python](https://effectivepython.com/)
- [Clean Code in Python](https://www.packtpub.com/product/clean-code-in-python/9781788835831)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [Plotly Python Graphing Library](https://plotly.com/python/) 