# Changelog

All notable changes to the RUBEM Hydrological plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-07

### Added

- **Modern Python Support**: Full support for Python 3.13+ with type hints throughout the codebase
- **QGIS 3.44+ Compatibility**: Updated to work with latest QGIS LTR and features
- **Pydantic Configuration**: Modern configuration management using Pydantic v2 for validation
  - Support for INI, JSON, and TOML configuration formats
  - Comprehensive validation with clear error messages
  - Type-safe configuration access
- **Structured Logging**: Professional logging system with:
  - File rotation to prevent excessive disk usage
  - Integration with QGIS message log
  - Configurable log levels
  - Structured log formatting
- **Exception Hierarchy**: Custom exception classes for better error handling
  - `RUBEMException` base class
  - Specific exceptions for different error types
  - Detailed error context with `details` dictionary
- **Testing Infrastructure**: Comprehensive test suite using pytest
  - Unit tests that don't require QGIS
  - Integration tests with QGIS mocking
  - Test fixtures and utilities
  - Code coverage reporting
- **CI/CD Pipeline**: GitHub Actions workflows for:
  - Code linting with Ruff and Black
  - Type checking with MyPy
  - Automated testing
  - Documentation building
- **Development Tools**:
  - Pre-commit hooks for code quality
  - EditorConfig for consistent formatting
  - Black code formatter configuration
  - Ruff linter configuration
  - MyPy type checker configuration

### Changed

- **Refactored Core Plugin**: Complete rewrite of `core.py` with:
  - Type hints for all methods and attributes
  - Comprehensive docstrings (Google style)
  - Better resource management
  - Improved error handling
  - Lazy loading of dialog for faster startup
- **Updated Dependencies**: Moved from Poetry 1.0 to latest version
  - Added modern development dependencies
  - Organized dependencies into groups (dev, docs)
  - Updated all package versions
- **Metadata Updates**:
  - Minimum QGIS version: 3.44
  - Minimum Python version: 3.13
  - Updated plugin metadata with detailed changelog
  - Changed experimental flag to False
  - Added proper category (Raster)
- **Project Structure**: Better organization with:
  - `plugin/models/` for data models
  - `plugin/exceptions.py` for custom exceptions
  - `plugin/logging.py` for logging configuration
  - Clear separation of concerns

### Fixed

- Fixed incorrect repository URLs in `pyproject.toml`
- Corrected license identifier to `GPL-3.0-or-later`
- Fixed icon path separator for cross-platform compatibility
- Improved translator loading with better error handling

### Documentation

- Updated all docstrings to Google/NumPy style
- Added comprehensive module-level documentation
- Type hints serve as inline documentation
- Created this CHANGELOG file
- Updated configuration examples

### Deprecated

- Old ConfigParser-based configuration (still supported but deprecated)
- Direct file imports without type checking guards

### Infrastructure

- Added `.editorconfig` for consistent code style
- Added `.pre-commit-config.yaml` for automated checks
- Added GitHub Actions CI workflow
- Added comprehensive `.gitignore`

### Developer Experience

- Type hints enable better IDE support
- Linting and formatting tools ensure code quality
- Pre-commit hooks catch issues before commit
- Comprehensive test suite builds confidence
- Clear exception hierarchy aids debugging

## [1.12.3] - 2024-03-19

### Previous Release

This was the last release before the major refactoring. See Git history for details.

---

## Migration Guide from 1.x to 2.0

### For Users

The plugin interface remains largely the same. However:

1. **QGIS Version**: Ensure you're using QGIS 3.44 or later
2. **Python Version**: QGIS installation must use Python 3.13+
3. **Configuration**: Old `.ini` files are still supported but consider migrating to `.toml` format

### For Developers

If you've extended or modified the plugin:

1. **Type Hints**: Add type hints to your code for better compatibility
2. **Imports**: Use the new exception classes instead of generic exceptions
3. **Logging**: Use `plugin.logging.get_logger(__name__)` instead of `print()` or direct logging
4. **Configuration**: Consider using `RUBEMConfig` Pydantic models instead of raw ConfigParser
5. **Testing**: Write pytest tests instead of unittest
6. **Code Style**: Run `black` and `ruff` on your code
7. **Type Checking**: Run `mypy` to catch type errors

### Breaking Changes

- Minimum QGIS version increased from 3.0 to 3.44
- Minimum Python version increased from 3.9 to 3.13
- Some internal APIs changed (see refactored modules)
- Configuration schema structure changed (backwards compatible loader provided)

[2.0.0]: https://github.com/LabSid-USP/RUBEMHydrological/compare/v1.12.3...v2.0.0
[1.12.3]: https://github.com/LabSid-USP/RUBEMHydrological/releases/tag/v1.12.3
