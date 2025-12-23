---
name: python
description: "Python development conventions with uv, type checking, linting, testing, and Docker deployment."
---

# ABOUTME: Complete Python development with uv package manager, quality tools, and Docker
# ABOUTME: Modern workflow with uv, ruff, pytest, type checking, and containerization

# Python Development

## Quick Reference

```bash
# Project setup
uv init myproject && cd myproject

# Dependencies
uv add requests pytest ruff
uv sync --locked

# Run code
uv run python main.py
uv run pytest

# Quality checks
uv run ruff check .
uvx ty check

# Docker build
docker build -t myapp .
```

**See also:**
- Code search: `_AST_GREP.md`
- Patterns: `_PATTERNS.md`
- Git workflow: `source-control`

---

## When to Use This Skill

- Setting up Python projects
- Managing dependencies with uv
- Running tests and linters
- Type checking
- Containerizing Python applications
- CI/CD for Python

---

## § Package Management with UV

### Overview

**UV is the ONLY way to manage Python projects. Do NOT use pip, poetry, or pipenv.**

- 10-100× faster than pip/poetry
- Universal lockfile for reproducibility
- Built-in Python version management
- Replaces pip, pip-tools, pipx, pyenv, virtualenv

### Daily Workflows

#### Project Setup (Cargo-style)

```bash
# Create new project
uv init myproject
cd myproject

# Project structure created:
# myproject/
# ├── pyproject.toml
# ├── uv.lock
# ├── .venv/
# └── .python-version

# Add dependencies
uv add requests httpx rich
uv add --dev pytest ruff mypy

# Sync environment
uv sync
```

#### Dependency Management

```bash
# Add packages
uv add package-name
uv add --dev dev-package

# Remove packages
uv remove package-name

# Update lockfile
uv lock

# Sync from lockfile (CI-safe)
uv sync --locked

# Production-only install
uv sync --no-dev --locked
```

#### Running Code

```bash
# Run Python scripts
uv run python main.py
uv run pytest
uv run ruff check .

# Run inline scripts (PEP 723)
echo 'print("hi")' > hello.py
uv run hello.py

# With transient dependencies
uv run --with rich script.py
```

#### CLI Tools (pipx replacement)

```bash
# Ephemeral run
uvx ruff check .
uvx black .

# Install globally
uv tool install ruff
uv tool install pytest

# List installed tools
uv tool list

# Update all tools
uv tool update --all
```

#### Python Version Management

```bash
# Install Python versions
uv python install 3.10 3.11 3.12

# Pin project version
uv python pin 3.12
# Creates .python-version

# Run with specific version
uv run --python 3.10 script.py
```

### Configuration

#### pyproject.toml

```toml
[project]
name = "myproject"
version = "0.1.0"
description = "My Python project"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31.0",
    "httpx>=0.24.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"  # Auto-detect async tests, no @pytest.mark.asyncio needed
```

### Performance Tuning

```bash
# Environment variables
export UV_CONCURRENT_DOWNLOADS=16    # Parallel downloads
export UV_CONCURRENT_INSTALLS=8      # Parallel installs
export UV_OFFLINE=1                  # Cache-only mode
export UV_INDEX_URL=https://pypi.org/simple  # Custom index

# Cache management
uv cache dir    # Show cache location
uv cache info   # Show cache stats
uv cache clean  # Clear cache
```

### Legacy pip Interface

```bash
# For legacy workflows only (prefer uv native commands)
uv venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

uv pip install -r requirements.txt
uv pip sync -r requirements.txt  # Deterministic
```

---

## § Code Quality

### Python Version

**Target Python 3.12+** as default.

### Type Annotations

# **Python 3.12+ Type Hinting Guidelines**

Context: Enforce modern Python 3.12+ type hinting standards (PEPs 585, 604, 695).
Strictness: High. Flag legacy syntax as technical debt.

## **1\. Syntax Replacement Rules**

*Transform legacy typing module usage to built-in/operator syntax.*

| Legacy Pattern (REJECT) | Modern Pattern (USE) | Rationale |
| :---- | :---- | :---- |
| from typing import List, Dict, Set, Tuple | **list, dict, set, tuple** | PEP 585 (Built-in generics) |
| typing.Union\[X, Y\] | **X | Y** | PEP 604 (Union operator) |
| typing.Optional\[X\] | **X | None** | Explicit nullability; clearer intent. |
| TypeAlias \= X (assignment) | **type TypeAlias \= X** | PEP 695 (Explicit type aliases) |
| class MyClass(Generic\[T\]): | **class MyClass\[T\]:** | PEP 695 (New Generic syntax) |
| def func\[T\](x: T) \-\> T: | **def func\[T\](x: T) \-\> T:** | PEP 695 (Native Function Generics) |

## **2\. Semantic Best Practices**

### **A. Strictness & Any**

* **Avoid Any:** Treat Any as a linter violation unless interfacing with untyped 3rd-party libs.
* **Alternatives:**
  * Unknown structure but no method access? Use object.
  * Input-dependent output? Use TypeVar (or PEP 695 \[T\]).
  * Specific behavior needed? Use Protocol.

### **B. Argument Types (Duck Typing)**

* **Inputs:** Prefer collections.abc interfaces over concrete types.
  * Use Iterable\[T\] or Sequence\[T\] instead of list\[T\].
  * Use Mapping\[K, V\] instead of dict\[K, V\].
  * Use Callable\[\[A\], B\] for functions.
* **Outputs:** Prefer concrete types (e.g., return list\[str\], not Iterable\[str\]) to allow the caller to use specific methods.

## **3\. Example Implementation**

**Bad (Legacy/Loose):**

```python
from typing import List, Optional, Dict, Any, Union

# "Any" bypasses checks; "Optional" is verbose; "List/Dict" are deprecated
def process_data(items: List[Union[str, int]]) -> Optional[Dict[str, Any]]:
    if not items: return None
    return {"data": items}

```

**Good (Modern/Strict):**

```python
from collections.abc import Sequence

# Uses built-ins, pipe operator, and ABCs for input flexibility
def process_data(items: Sequence[str | int]) -> dict[str, object] | None:
    if not items:
        return None
    return {"data": items}
```

**Use `TYPE_CHECKING` for import-only types:**

```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from myproject.services import ServiceProvider

def create_tool(services: "ServiceProvider") -> None:
    ...
```

### Linting with Ruff

```bash
# Check code
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

**Configuration:**

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.lint.isort]
known-first-party = ["myproject"]
```

### Testing with pytest

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=myproject --cov-report=html

# Specific tests
uv run pytest tests/test_user.py::test_create_user

# Watch mode (with pytest-watch)
uv run ptw
```

**Async tests - no decorator required:**

With `asyncio_mode = "auto"` in pyproject.toml, async tests are auto-detected:

```python
# ✅ CORRECT - no decorator needed
async def test_my_async_function() -> None:
    result = await my_async_function()
    assert result is not None

# ❌ WRONG - redundant decorator
@pytest.mark.asyncio  # Don't add this!
async def test_my_async_function() -> None:
    ...
```

**Test structure (Arrange-Act-Assert):**

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def user_service(mock_repo: Mock, mock_logger: Mock) -> UserService:
    return UserService(repo=mock_repo, logger=mock_logger)

def test_find_user_success(user_service: UserService, mock_repo: Mock) -> None:
    """Test that finding a user returns the correct user object."""
    # Arrange
    mock_repo.find.return_value = User(id="1", name="Max")

    # Act
    user = user_service.find("1")

    # Assert
    assert user.name == "Max"
    mock_repo.find.assert_called_once_with("1")

@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("invalid", False),
])
def test_email_validation(email: str, expected: bool) -> None:
    assert validate_email(email) == expected
```

**Use `autospec=True` with mocks:**

```python
# ✅ GOOD: Typos are caught immediately
@patch("google.cloud.bigquery.Client", autospec=True)
def test_query(mock_client: Mock) -> None:
    mock_client.qury()  # AttributeError - typo caught!

# ❌ BAD: Typos go unnoticed
@patch("google.cloud.bigquery.Client")
def test_query(mock_client: Mock) -> None:
    mock_client.qury()  # Silently succeeds
```

---

## § Workflow

### Branch Strategy

- Create new branch for each feature/bugfix
- Frequent commits for each subtask
- Leverage git heavily

### Testing & Code Snippets

- Always have runnable test snippets
- Make them persistent (don't use ephemeral code)
- **Always** ensure tests run before commits
- If tests broken: fix in separate PR first

### Pre-commit Checks

**ALWAYS run before committing:**

```bash
# Linting
uv run ruff check .

# Type checking
uvx ty check

# Tests
uv run pytest
```

**Setup pre-commit hook:**

```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

echo "Running pre-commit checks..."

uv run ruff check .
uvx ty check
uv run pytest -q

echo "✓ All checks passed"
```

```bash
chmod +x .git/hooks/pre-commit
```

### Makefile Heuristic

Provide standardized commands via Makefile to prevent AI (and humans) from guessing or using ineffective shortcuts.

```makefile
# Makefile
.PHONY: install test lint typecheck fmt clean run dev docker-rebuild

# Default target
all: fmt lint typecheck test

# Install dependencies
install:
	uv sync

# Format code
fmt:
	uv run ruff format .

# Lint
lint:
	uv run ruff check .

# Type check
typecheck:
	uvx ty check

# Run tests
test:
	uv run pytest -v

# Run tests with coverage
test-cov:
	uv run pytest --cov=. --cov-report=html

# Run application
run:
	uv run python -m app

# Development mode (watch for changes)
dev:
	uv run python -m app --reload

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

# Docker rebuild
docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Lambda package (if using AWS Lambda)
package:
	uv export --no-dev --frozen > requirements.txt
	pip install -r requirements.txt -t package/
	cd package && zip -r ../lambda.zip .
	zip -g lambda.zip app/*.py
```

**Benefits:**
- Prevents AI from using ineffective commands (e.g., `docker-compose restart` when rebuild needed)
- Documents canonical development workflow
- Consistent commands across team and CI/CD
- Self-documenting (run `make` to see targets)

**Usage examples:**
```bash
make install        # Install all dependencies
make test          # Run tests
make               # Run all quality checks (default)
make docker-rebuild # Rebuild and restart Docker containers
```

---

## § Docker Deployment

### Multistage Dockerfile with UV

**Optimized production build:**

```dockerfile
# Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies to virtual environment
RUN uv sync --frozen --no-cache --no-dev

# Production stage
FROM python:3.12-slim

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Run application
CMD ["uv", "run", "python", "-m", "myapp"]
```

### Docker Build Patterns

#### Basic Build

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY . .

CMD ["uv", "run", "python", "main.py"]
```

#### With System Dependencies

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev

# Production stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY --from=builder /app/.venv /app/.venv

WORKDIR /app
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "python", "main.py"]
```

### Docker Tips

1. **Layer caching**: Copy `pyproject.toml` and `uv.lock` before code
2. **Use `--frozen`**: Ensures exact versions from lockfile
3. **Use `--no-cache`**: Prevents UV cache from bloating image
4. **Use `--no-dev`**: Skip development dependencies in production
5. **Set PATH**: Ensure virtual environment is activated
6. **Non-root user**: Run as non-root for security
7. **Multi-stage**: Keep final image small (no build tools)

### Docker Compose Example

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
    volumes:
      - .:/app
    command: uv run python main.py

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## § CI/CD

### GitHub Actions

```yaml
name: tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Install Python
        run: uv python install

      - name: Install dependencies
        run: uv sync --locked

      - name: Run linter
        run: uv run ruff check .

      - name: Run type checker
        run: uvx ty check

      - name: Run tests
        run: uv run pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### GitLab CI

```yaml
image: ghcr.io/astral-sh/uv:python3.12-bookworm-slim

stages:
  - test
  - build

test:
  stage: test
  script:
    - uv sync --locked
    - uv run ruff check .
    - uvx ty check
    - uv run pytest --cov
  cache:
    paths:
      - .venv/

build:
  stage: build
  script:
    - docker build -t myapp .
  only:
    - main
```

---

## § Migration from pip/poetry

### From pip + requirements.txt

```bash
# Convert requirements.txt to pyproject.toml
uv init --name myproject
uv add $(cat requirements.txt | grep -v '^#' | grep -v '^$')

# Or import directly
uv pip compile requirements.txt -o requirements.lock
uv pip sync requirements.lock
```

### From poetry

```bash
# Poetry's pyproject.toml is compatible
uv sync

# Migrate lockfile
rm poetry.lock
uv lock
```

### From pipenv

```bash
# Convert Pipfile
uv init
# Manually add dependencies from Pipfile to pyproject.toml
uv sync
```

---

## § Troubleshooting

| Symptom                        | Solution                                      |
|--------------------------------|-----------------------------------------------|
| Python X.Y not found           | `uv python install X.Y`                       |
| Proxy issues                   | `export UV_HTTP_TIMEOUT=120`                  |
| C-extension build errors       | Install build dependencies, or use wheels     |
| Need fresh environment         | `uv cache clean && rm -rf .venv && uv sync`   |
| Lockfile conflicts             | `uv lock --upgrade-package problematic-pkg`   |
| Import not found after install | Check `uv sync` ran successfully              |

**Debug mode:**

```bash
# Verbose output
RUST_LOG=debug uv sync
```

---

## § Coding Conventions

### Documentation Style

**Follow Google-style docstrings:**

```python
def execute_query(query: str, max_rows: int = 1000) -> list[dict[str, Any]]:
    """Execute a BigQuery SQL query and return results.

    Args:
        query: The SQL query to execute
        max_rows: Maximum number of rows to return (default: 1000)

    Returns:
        List of dictionaries representing query result rows

    Raises:
        BigQueryError: If query execution fails
        ValueError: If query is empty or malformed
    """
    ...
```

### Exception Handling

**Do NOT use exceptions for control flow. Check conditions proactively:**

```python
# ✅ GOOD: Proactive checking
if asset_key in asset_metadata:
    value = asset_metadata[asset_key]
else:
    handle_missing_asset()

# ❌ BAD: Using exceptions for control flow
try:
    value = asset_metadata[asset_key]
except KeyError:
    handle_missing_asset()
```

**Add context when re-raising, never swallow silently:**

```python
# ✅ GOOD: Adding context
try:
    validate_config(config)
except ValidationError as e:
    raise ConfigurationError(f"Tool '{tool_name}' has invalid config: {e}") from e

# ❌ BAD: Silently swallowing
try:
    process_item(item)
except Exception:
    pass  # Never do this
```

### Data Structures

**Use Pydantic `BaseModel` for configs with validation:**

```python
from pydantic import BaseModel, Field

class ToolConfig(BaseModel):
    name: str
    description: str = Field(default="", description="Tool description")
    tags: list[str] = Field(default_factory=list)

# Immutable-style updates
new_config = config.model_copy(update={"name": "new_name"})
```

**Use `@dataclass` for simple data containers without validation needs.**

### CLI Development

**Use Rich + Typer for CLIs. Never use `print()` in production code:**

```python
from rich.console import Console
import typer

console = Console()
app = typer.Typer()

@app.command()
def my_command() -> None:
    # ✅ GOOD: Use Rich console
    console.print("[green]Processing started...[/green]")
    console.print(f"Found {count} items")

    # ❌ BAD: Don't use print
    print("Processing...")  # Never do this
```

### Logging

**Use `logging` module with module-level loggers:**

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: dict[str, Any]) -> None:
    logger.debug(f"Processing data with {len(data)} keys")
    logger.info("Data processing completed successfully")
    logger.warning("Deprecated field 'old_field' will be removed in v2.0")
```

### Literal Types for String Enums

```python
from typing import Literal

OutputFormat = Literal["markdown", "text", "json", "key_value"]
FilterMode = Literal["all", "any", "none"]

def format_output(data: str, format: OutputFormat = "markdown") -> str:
    ...
```

---

## § Best Practices Summary

### ✅ DO

- Use `uv` for everything (not pip/poetry)
- Target Python 3.12+
- Use modern type syntax (`list[str]`, `X | None`)
- Use `TYPE_CHECKING` blocks for import-only types
- Run linter before commits (`ruff check`)
- Run type checker before commits (`uvx ty check`)
- Use `uv sync --locked` in CI
- Use Pydantic `BaseModel` for configs with validation
- Use Google-style docstrings
- Use Rich + Typer for CLIs
- Use `logging` module (not `print()`)
- Use multistage Docker builds
- Pin Python version with `.python-version`
- Use `pyproject.toml` for all configuration

### ❌ DON'T

- Use pip, easy_install, poetry, or pipenv
- Use old-style typing (`List`, `Dict`, `Optional`)
- Use exceptions for control flow
- Swallow exceptions silently
- Use `print()` in production code
- Commit without running tests
- Ignore type errors
- Use `uv sync` without `--locked` in CI
- Include `.venv` in git (use `.gitignore`)
- Use `requirements.txt` for new projects (use pyproject.toml)

---

## § Resources

**UV Documentation:**
- https://docs.astral.sh/uv/

**Python Tools:**
- Ruff: https://docs.astral.sh/ruff/
- pytest: https://docs.pytest.org/
- mypy: https://mypy.readthedocs.io/

**Related Skills:**
- Code search: `_AST_GREP.md`
- Patterns: `_PATTERNS.md`
- Git: `source-control/SKILL.md`

---

**End of SKILL: Python Development**