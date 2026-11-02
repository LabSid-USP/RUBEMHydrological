# Development Guide

This guide provides information for developers who want to contribute to or extend the RUBEM Hydrological plugin.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Building and Packaging](#building-and-packaging)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Development Environment Setup

### Prerequisites

- **QGIS 3.44+** with Python 3.13+ bindings
- **Poetry** for dependency management
- **Git** for version control
- **Qt Designer** (optional, for UI editing)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/LabSid-USP/RUBEMHydrological.git
   cd RUBEMHydrological
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install --with dev,docs
   ```

4. **Install pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```

### Development Workflow

#### Using the Plugin in QGIS

For development, create a symbolic link in QGIS plugins directory:

**Linux/Mac**:
```bash
ln -s $(pwd) ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/rubem_hydrological
```

**Windows**:
```cmd
mklink /D %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\rubem_hydrological C:\path\to\RUBEMHydrological
```

Then restart QGIS and enable the plugin in Plugin Manager.

#### Hot Reload for Development

Use the QGIS Plugin Reloader plugin for faster development:

1. Install "Plugin Reloader" from QGIS Plugin Repository
2. Configure it to reload RUBEM Hydrological
3. Use Ctrl+F5 (or configured shortcut) to reload after code changes

## Code Style and Standards

### Python Style Guide

We follow modern Python best practices:

- **PEP 8** with line length of 88 characters (Black default)
- **Type hints** for all functions and methods (PEP 484, 585, 604)
- **Docstrings** in Google or NumPy style
- **Import ordering**: standard library, third-party, local (managed by isort/ruff)

### Type Hints

Use modern Python 3.13+ type hint syntax:

```python
from __future__ import annotations  # Enable postponed evaluation

def process_data(
    input_path: Path,
    output_dir: Path | None = None,
    options: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    """Process input data and save results.
    
    Args:
        input_path: Path to input file.
        output_dir: Optional output directory.
        options: Optional processing options.
        
    Returns:
        Tuple of (success, message).
    """
    ...
```

### Docstring Format

Use Google-style docstrings:

```python
def calculate_runoff(
    precipitation: float,
    infiltration: float,
    evapotranspiration: float,
) -> float:
    """Calculate surface runoff using water balance equation.
    
    This function computes runoff as the residual of precipitation
    after accounting for infiltration and evapotranspiration.
    
    Args:
        precipitation: Total precipitation in mm.
        infiltration: Infiltration amount in mm.
        evapotranspiration: Actual evapotranspiration in mm.
        
    Returns:
        Calculated runoff in mm.
        
    Raises:
        ValueError: If any input is negative.
        
    Example:
        >>> runoff = calculate_runoff(100.0, 30.0, 40.0)
        >>> print(f"Runoff: {runoff} mm")
        Runoff: 30.0 mm
    """
    if any(x < 0 for x in [precipitation, infiltration, evapotranspiration]):
        raise ValueError("All inputs must be non-negative")
    return max(0, precipitation - infiltration - evapotranspiration)
```

### Automated Formatting

We use several tools to maintain code quality:

#### Black (Code Formatter)

```bash
# Format all Python files
poetry run black .

# Check without modifying
poetry run black --check .
```

#### Ruff (Linter)

```bash
# Lint all files
poetry run ruff check .

# Auto-fix issues
poetry run ruff check --fix .
```

#### MyPy (Type Checker)

```bash
# Type check the plugin
poetry run mypy plugin/

# Type check specific file
poetry run mypy plugin/core.py
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Run manually on all files
poetry run pre-commit run --all-files

# Skip hooks for a commit (not recommended)
git commit --no-verify
```

## Testing

### Test Structure

Tests are organized in `test/` directory:

```
test/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests (no QGIS required)
│   ├── test_exceptions.py
│   ├── test_models.py
│   └── test_utils.py
└── integration/          # Integration tests (require QGIS)
    ├── test_plugin.py
    ├── test_dialog.py
    └── test_qgis_integration.py
```

### Running Tests

#### Unit Tests Only

```bash
# Run unit tests (fast, no QGIS required)
poetry run pytest test/unit -m unit -v

# With coverage
poetry run pytest test/unit -m unit -v --cov --cov-report=html
```

#### Integration Tests

Integration tests require QGIS environment:

```bash
# Run in QGIS Python environment
# This depends on your QGIS installation
python -m pytest test/integration -m integration -v
```

#### All Tests

```bash
# Run all tests
poetry run pytest -v

# With coverage report
poetry run pytest -v --cov --cov-report=html --cov-report=term
```

### Writing Tests

#### Unit Test Example

```python
"""Unit tests for configuration models."""

import pytest
from plugin.models import SimulationTime, ConfigurationError


@pytest.mark.unit
class TestSimulationTime:
    """Test cases for SimulationTime model."""
    
    def test_valid_time_period(self) -> None:
        """Test creating valid simulation time period."""
        sim_time = SimulationTime(
            start="2020-01-01",
            end="2020-12-31"
        )
        assert sim_time.duration_months == 11
        
    def test_invalid_time_period(self) -> None:
        """Test that end before start raises error."""
        with pytest.raises(ValueError, match="End date must be after"):
            SimulationTime(
                start="2020-12-31",
                end="2020-01-01"
            )
```

#### Integration Test Example

```python
"""Integration tests for plugin dialog."""

import pytest
from unittest.mock import MagicMock


@pytest.mark.integration
class TestRUBEMDialog:
    """Test cases for plugin dialog."""
    
    def test_dialog_initialization(self, mock_qgis_interface: MagicMock) -> None:
        """Test dialog initializes correctly."""
        from plugin.dialog import RUBEMHydrologicalDialog
        
        dlg = RUBEMHydrologicalDialog(mock_qgis_interface)
        assert dlg is not None
        assert dlg.iface == mock_qgis_interface
```

### Test Markers

Use pytest markers to categorize tests:

- `@pytest.mark.unit`: Unit tests (fast, no QGIS)
- `@pytest.mark.integration`: Integration tests (require QGIS)
- `@pytest.mark.slow`: Slow-running tests

## Building and Packaging

### Regenerating UI Files

After editing `.ui` files in Qt Designer:

```bash
# Regenerate Python code from UI file
pyuic5 plugin/gui/core.ui -o plugin/gui/generated/core_ui.py

# Regenerate resources
pyrcc5 plugin/gui/resources/resources.qrc -o plugin/gui/generated/resources_rc.py
```

**Important**: Never manually edit files in `plugin/gui/generated/`!

### Building Documentation

```bash
cd doc
poetry run python -m sphinx -b html source build/html
```

Open `doc/build/html/index.html` in a browser to view.

### Creating Plugin Package

```bash
# Build plugin ZIP for distribution
python scripts/build_plugin.py

# The plugin will be in dist/rubem_hydrological.zip
```

### Version Bumping

We use Commitizen for semantic versioning:

```bash
# Bump version (automatically updates all version files)
poetry run cz bump

# Bump to specific version
poetry run cz bump --version 2.1.0

# Preview what would be bumped
poetry run cz bump --dry-run
```

## Documentation

### Code Documentation

- Add docstrings to all public functions, classes, and methods
- Use type hints for all parameters and return values
- Include examples in docstrings when helpful

### Sphinx Documentation

Documentation is in `doc/source/` as reStructuredText files:

```bash
# Build documentation
cd doc
poetry run python -m sphinx -b html source build/html

# Watch for changes and auto-rebuild
poetry run sphinx-autobuild source build/html
```

### Adding New Documentation

1. Create `.rst` file in `doc/source/`
2. Add to table of contents in `index.rst`
3. Build and verify

## Contributing

### Workflow

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make changes** following code style guidelines
4. **Write tests** for new functionality
5. **Run tests and linters**: `poetry run pytest && poetry run ruff check .`
6. **Commit** with conventional commit messages
7. **Push** to your fork
8. **Create Pull Request**

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(models): add support for TOML configuration format
fix(dialog): prevent crash when loading invalid config
docs(readme): update installation instructions
refactor(core): improve error handling in plugin initialization
```

### Pull Request Guidelines

- Ensure all tests pass
- Update documentation if needed
- Add entry to CHANGELOG.md
- Reference related issues
- Keep changes focused and atomic

## Debugging

### QGIS Python Console

Use QGIS Python console for quick debugging:

```python
# Reload plugin module
import importlib
import plugin.core
importlib.reload(plugin.core)

# Access plugin instance
iface.mainWindow().findChild(QAction, 'mActionShowRUBEM').trigger()
```

### Logging

Use the plugin's logging system:

```python
from plugin.logging import get_logger

logger = get_logger(__name__)
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)  # Include traceback
```

View logs in:
- QGIS Log Messages Panel
- Log files in `~/.local/share/QGIS/QGIS3/profiles/default/logs/rubem_hydrological/`

### Remote Debugging

For remote debugging with PyCharm or VS Code:

```python
# Add to your code
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)
```

## Resources

- [QGIS Python API Documentation](https://qgis.org/pyqgis/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
