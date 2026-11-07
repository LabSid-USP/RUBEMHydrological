# Changelog

All notable changes to the RUBEM Hydrological plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Accumulated Total Runoff (ARN) output option**: new Generate Files checkbox for the ARN raster series, and a `tss_arn` time series when station time series generation is enabled. Wired end-to-end: dialog, project save/load, results listing and plotting.
- **Boolean token validation**: project file booleans are validated before the RUBEM model loads them. Unknown tokens such as "maybe" are rejected with the offending `SECTION.key` in the message; documented tokens (yes/no/true/false/t/f/1/0, case-insensitive) and true booleans are accepted.
- **Defaults on load**: missing model-required defaults (for example `GENERATE_FILE.arn`) are filled when a project file is loaded, so older files open correctly.

### Changed

- **JSON round-trip preserves relative paths**: loading a project stores relative paths exactly as written; RUBEM resolves them from the JSON file's directory instead of the dialog resolving them to absolute paths at load time.
- **Total Runoff units corrected**: RNF and `tss_rnf` are labelled [mm] throughout the dialog and results views; Accumulated Total Runoff (ARN) is labelled [m³/s].
- **Weight factor validation**: the weight-factor sum check uses the stored values that will be written to the project file, not the rounded 3-decimal widget display.
- **DEM georeference is optional**: an empty DEM `.tif` field is valid; a non-empty path must still point to an existing file.
- **Project file permissions**: project JSON written by the dialog honours the user's umask instead of being created read/write by owner only.
- **CI**: unit tests run in the `qgis/qgis:4.2` container; the no-QGIS Poetry unit-test job was removed.
- **Docs**: QGIS 4 is the prerequisite; the PCRaster Tools plugin is no longer required (PCRaster and GDAL are native libraries installed with OSGeo4W or conda); documentation version set to 2.0.0.

## [2.0.0] - 2025-01-07

### Added

- **Modern Python Support**: Full support for Python 3.13+ with type hints throughout the codebase
- **QGIS 4**: The plugin targets QGIS 4.2 and PyQt6
- **Pydantic Configuration**: Project files are the legacy JSON document RUBEM reads, validated by the submodule's Pydantic model
  - Pydantic ``>=2.11,<3``, the same requirement as the RUBEM submodule
  - INI and TOML are not project formats
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
  - Minimum QGIS version: 4.0
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

1. **QGIS Version**: Ensure you're using QGIS 4.2
2. **Python Version**: QGIS installation must use Python 3.13+
3. **Configuration**: Project files are the JSON document RUBEM reads. INI and TOML are not project formats.

### For Developers

If you've extended or modified the plugin:

1. **Type Hints**: Add type hints to your code for better compatibility
2. **Imports**: Prefer the live dialog helpers; the v2 ``plugin.exceptions`` /
   ``plugin.logging`` layer is scaffolding and is not what QGIS loads
3. **Logging**: Keep using ``QgsMessageLog`` / dialog log widgets on the live path
4. **Configuration**: The live project file is still the legacy JSON document,
   validated by the submodule's ``ModelConfigurationFile``. ``plugin.models.RUBEMConfig``
   is unwired scaffolding with different field names and stubs — do not use it as
   the project document or as a migration target yet
5. **Testing**: Write pytest tests instead of unittest
6. **Code Style**: Run `black` and `ruff` on your code
7. **Type Checking**: Run `mypy` to catch type errors

### Breaking Changes

- Minimum QGIS version is 4.0
- Minimum Python version increased from 3.9 to 3.13
- Some internal APIs changed (see refactored modules)
- Project files are the legacy JSON RUBEM reads (not INI/TOML); older JSON without
  ``GENERATE_FILE.arn`` still opens because the plugin applies defaults on load

[2.0.0]: https://github.com/LabSid-USP/RUBEMHydrological/compare/v1.12.3...v2.0.0
[1.12.3]: https://github.com/LabSid-USP/RUBEMHydrological/releases/tag/v1.12.3
