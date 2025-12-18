# Contributing to x402-python-client

Thank you for your interest in contributing to x402-python-client!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/agentokratia/x402-python-client.git
   cd x402-python-client
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .
```

We use [mypy](https://mypy.readthedocs.io/) for type checking:

```bash
mypy src/
```

## Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=x402_client
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run linting and tests
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Commit Messages

Please use clear, descriptive commit messages. We follow conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## Reporting Issues

When reporting issues, please include:

- Python version
- Package version
- Minimal reproducible example
- Expected vs actual behavior
- Error messages/stack traces

## Questions?

Feel free to open an issue for any questions about contributing.
