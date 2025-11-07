# Agent Instructions for RUBEM Hydrological

## Project Overview

**RUBEM Hydrological** is a QGIS 3 plugin that assists in configuration and execution of the Rainfall rUnoff Balance Enhanced Model (RUBEM), a distributed hydrological model for calculating monthly water flows with changes in land use over time. The plugin provides a GUI interface for setting up model parameters, running simulations, and visualizing results.

### Repository Details
- **Type**: QGIS Python Plugin
- **Language**: Python (3.9+)
- **Framework**: QGIS 3.22+ with PyQt5/qgis.PyQt
- **License**: GPLv3
- **Size**: ~140 files, primarily Python modules
- **Version**: 1.12.3 (as of metadata.txt)

## Critical Architecture & Layout

### Main Plugin Structure
```
├── __init__.py                    # Plugin entry point with classFactory()
├── metadata.txt                   # QGIS plugin metadata (version, min QGIS version)
├── pyproject.toml                 # Poetry config (Python 3.9+)
├── plugin/                        # Core plugin code
│   ├── __version__.py            # Version info
│   ├── core.py                   # Main RUBEMHydrological class, plugin initialization
│   ├── dialog/                   # UI logic modules
│   │   ├── __init__.py          # RUBEMHydrologicalDialog class
│   │   ├── _tab_*.py            # Tab-specific handlers (settings, soil, climate, etc.)
│   │   ├── _worker.py           # Background task execution
│   │   └── _*.py                # Helper modules (validation, plotting, etc.)
│   ├── gui/                     # UI resources
│   │   ├── core.ui              # Qt Designer UI file
│   │   ├── generated/           # GENERATED FILES - DO NOT EDIT
│   │   │   ├── core_ui.py      # Generated from core.ui via pyuic5
│   │   │   └── resources_rc.py # Generated from resources.qrc via pyrcc5
│   │   └── resources/
│   │       └── resources.qrc    # Qt resource file for images/icons
│   ├── validation/              # Input validation schemas and validators
│   ├── report/                  # Plotting and visualization
│   └── utils/                   # Utility functions (raster, series, workers)
├── test/                        # Test suite (unittest-based)
│   ├── integration/             # Integration tests (require QGIS)
│   └── unit/                    # Unit tests
├── doc/                         # Sphinx documentation
└── images/                      # Plugin icons and screenshots
```

### Key Files
- **Entry Point**: `__init__.py` contains `classFactory(iface)` required by QGIS
- **Main Class**: `plugin/core.py::RUBEMHydrological` - plugin lifecycle
- **Dialog**: `plugin/dialog/__init__.py::RUBEMHydrologicalDialog` - main window
- **Config Schema**: `plugin/validation/schemas.py::defaultConfigSchema` - configuration structure

### Dependencies
- **Runtime**: QGIS 3.22+, PCRaster Processing Provider plugin
- **GUI**: PyQt5 or qgis.PyQt (imports try qgis.PyQt first, fallback to PyQt5)
- **Testing**: QGIS API (tests fail without QGIS environment)
- **Documentation**: Sphinx, sphinx-rtd-theme, sphinxcontrib-email, sphinxcontrib-youtube

## Build & Validation Steps

### Environment Setup

**CRITICAL**: This is a QGIS plugin and requires QGIS to be installed for testing. Standard Python environments will NOT work for integration tests.

1. **For Documentation Only**: Install doc dependencies
   ```bash
   # Install Sphinx and extensions
   pip install Sphinx sphinx-rtd-theme sphinxcontrib-email sphinxcontrib-youtube
   ```

2. **For Testing**: Requires full QGIS installation with Python bindings
   - Tests import `qgis.core`, `qgis.gui`, `qgis.PyQt` which are only available in QGIS Python environment
   - Running `python -m unittest discover` outside QGIS will fail with `ModuleNotFoundError: No module named 'qgis'`

### Building Documentation

**ALWAYS use the Python module approach** (not `make` directly) to ensure correct Python environment:

```bash
cd doc
python -m sphinx -b html source build/html
```

**Expected Result**: Build succeeds with "build succeeded" message. HTML output in `doc/build/html/`.

**Common Issues**: 
- Error "sphinx-build: No such file or directory" → Install Sphinx first
- Missing extensions → Install all packages from `doc/requirements.txt`

### Testing

**Unit Tests** (test/unit/):
```bash
python -m unittest discover -s test/unit -p 'test*.py'
```

**Integration Tests** (test/integration/):
**DO NOT RUN** these outside a QGIS environment. They require:
- Full QGIS installation with Python bindings
- QGIS Python environment activated
- Will fail with `ModuleNotFoundError: No module named 'qgis'` in standard Python

**Test Status**: Only `test/integration/test_init.py::test_read_init` passes in standard Python. All other integration tests require QGIS.

### UI Regeneration (GENERATED FILES)

**NEVER manually edit** `plugin/gui/generated/core_ui.py` or `plugin/gui/generated/resources_rc.py`. These are generated:

```bash
# Regenerate UI Python code from Qt Designer file
pyuic5 plugin/gui/core.ui -o plugin/gui/generated/core_ui.py

# Regenerate resources from .qrc file
pyrcc5 plugin/gui/resources/resources.qrc -o plugin/gui/generated/resources_rc.py
```

**Only regenerate if**:
- Modified `plugin/gui/core.ui` in Qt Designer
- Modified `plugin/gui/resources/resources.qrc`

## Development Workflow

### Making Code Changes

1. **Update Plugin Version**: Modify both `plugin/__version__.py` and `metadata.txt` consistently
2. **UI Changes**: Edit `core.ui` in Qt Designer, then regenerate Python code
3. **Validation**: Check `plugin/validation/schemas.py` for configuration schema if adding new fields
4. **Documentation**: Update corresponding `.rst` files in `doc/source/` if changing user-facing features

### Cross-Platform Compatibility

The plugin must work on **Linux, Mac, and Windows**. Key considerations:
- Use `os.path.join()` for paths, never hardcode separators
- Qt/PyQt handles most platform differences
- Test file dialogs work correctly on each platform

### Configuration Files

Plugin configuration uses Python's `configparser` with schema defined in `plugin/validation/schemas.py::defaultConfigSchema`. Contains sections:
- `SIM_TIME`: Simulation period
- `DIRECTORIES`: Input/output paths
- `FILENAME_PREFIXES`: File naming patterns
- `RASTERS`: Spatial input files
- `TABLES`: Tabular input files
- `CALIBRATION`: Model parameters
- `GENERATE_FILE`: Output flags
- `RASTER_FILE_FORMAT`: Output format options

## Validation Pipeline

### Pre-Checkin Requirements

From `.github/pull_request_template.md`:
- [ ] Follow CONTRIBUTING.md guidelines
- [ ] No duplicate PRs
- [ ] Add tests for changes
- [ ] Update documentation for changes
- [ ] Ensure cross-platform compatibility

### No CI/CD Pipeline

**IMPORTANT**: This repository has NO automated CI/CD workflows (no `.github/workflows/` directory). All testing and validation must be done manually before submitting PRs.

### Documentation Build Validation

Always verify documentation builds without errors:
```bash
cd doc && python -m sphinx -b html source build/html
```

Check for warnings/errors in output. Documentation should build cleanly.

### Code Style

The codebase has numerous TODOs for missing docstrings. When adding new functions:
- Follow existing docstring format (Google style)
- Include type hints where present
- Add descriptive comments for complex logic

## Common Patterns & Conventions

### Import Pattern
All modules try QGIS imports first, fallback to direct PyQt5:
```python
try:
    from qgis.PyQt.QtCore import Qt
    from qgis.PyQt.QtWidgets import QDialog
except ImportError:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QDialog
```

### Module Organization
Dialog functionality is split across modules in `plugin/dialog/`:
- `_tab_*.py`: Tab-specific logic
- `_*.py`: Cross-cutting concerns (validation, plotting, messages)
- All imported in `__init__.py` as methods of `RUBEMHydrologicalDialog`

### File Paths
Plugin uses absolute paths internally. GUI helpers in `plugin/dialog/_file_dir_dialogs.py` provide directory/file selection dialogs.

## Limitations & Known Issues

1. **Testing Limitations**: Integration tests cannot run outside QGIS environment
2. **Generated Files**: `plugin/gui/generated/*` must be regenerated after UI changes
3. **Documentation Dependencies**: Requires custom Sphinx extensions (email, youtube)
4. **No Automated CI**: Manual validation required for all changes
5. **QGIS Version**: Minimum QGIS 3.22, experimental flag set in metadata
6. **External Dependency**: Requires PCRaster Processing Provider plugin

## Trust These Instructions

When working with this repository:
1. **Do NOT try to run integration tests** unless in QGIS Python environment
2. **Do NOT edit generated files** in `plugin/gui/generated/`
3. **Always rebuild documentation** after changing `.rst` files
4. **Update both version files** when bumping versions
5. **Only search for additional information** if these instructions are incomplete or proven incorrect

For questions not covered here, check:
- `doc/source/` RST files for user-facing documentation
- `CONTRIBUTING.md` for contribution guidelines
- `README.md` for general project info
- Code comments for implementation details
