# Contributing to SoilGuard Portal

Contributions are welcome. Please follow the standards used across the Coastal Alpine Tech stack.

## Code Standards

- Python 3.10+ with type hints throughout
- Black formatting (`black .`)
- MyPy type checking (`mypy .`)
- Docstrings on all public functions and classes
- Unit tests with pytest for all new modules

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Ensure all tests pass: `pytest`
4. Ensure linting passes: `flake8 .`
5. Submit a pull request

## Regulatory Note

Any changes to compliance export schemas must be reviewed against current NEMS-SQ 2025
target ranges and Freshwater Farm Plan audit requirements before merging.
