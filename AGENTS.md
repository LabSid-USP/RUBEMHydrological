# RUBEM Hydrological

QGIS plugin (QGIS 4.0+, Python 3.13.16 per the local QGIS 4.2 interpreter) that turns user input into the legacy JSON file RUBEM reads, runs that model in a separate process and plots what it writes. The plugin contains no hydrology itself.

Two generations of code coexist: the v1 dialog path, which is what QGIS actually loads, and a v2 layer (pydantic + MVC) that is scaffolding not yet wired in. Check `__init__.py::classFactory` before assuming v2 is live.

## Commands

Every test module imports `qgis` (through `test/__init__.py`), so tests need an interpreter where `qgis` is importable: QGIS's own Python, or a venv created with `--system-site-packages` on top of it. Run pytest as `python -m pytest` from the repo root, which puts the root on `sys.path` so `import plugin` resolves; bare `pytest` fails at collection.

```bash
# Unit tests (pytest, marked `unit`). --no-cov skips the htmlcov/ + coverage.xml that pyproject addopts generate
python -m pytest test/unit -m unit --no-cov
python -m pytest test/unit/test_exceptions.py::TestRUBEMException --no-cov   # single class or test

# Integration tests: legacy unittest classes with no pytest markers, so `pytest -m integration` (as in ci.yml) selects none
QT_QPA_PLATFORM=offscreen python -m unittest discover -s test/integration -p 'test*.py'
QT_QPA_PLATFORM=offscreen python -m unittest test.integration.test_init      # single module

# Lint / format / types (mirrors .github/workflows/ci.yml)
ruff check .
black --check .
mypy plugin/ --ignore-missing-imports
pre-commit run --all-files

# Docs (CI builds with -W, so warnings fail); Read the Docs installs doc/requirements.txt
cd doc && python -m sphinx -b html source build/html -W

# Regenerate Qt output after editing plugin/gui/core.ui or plugin/gui/resources/resources.qrc
# pyuic6 comes from the QGIS 4 environment. The resource file is binary because
# Qt 6's Python rcc emits PySide6, and this plugin loads resources with PyQt6.
pyuic6 plugin/gui/core.ui -o plugin/gui/generated/core_ui.py
rcc --binary plugin/gui/resources/resources.qrc -o plugin/gui/generated/resources.rcc
```

- Never edit `plugin/gui/generated/` by hand. Ruff and Black exclude that directory in `pyproject.toml`.
- The integration tests are legacy plugin-template tests and several fail on current setups (for example `test_rubem_hydrological_dialog.py` expects a `button_box` widget the dialog does not define). Compare against the base branch before treating a failure as a regression.
- Known CI gap: the `test-unit` job installs only Poetry dependencies, without QGIS, while `test/__init__.py` imports `qgis`; the `test-integration` job runs `pytest -m integration`, which selects nothing.
- Python tooling is configured in `pyproject.toml` (ruff, black, mypy, pytest). Mark every new unit test `@pytest.mark.unit`, or `-m unit` (as in ci.yml) skips it; `--strict-markers` rejects markers not registered there.

## Workflow

- Per `CONTRIBUTING.md`, anything beyond a trivial fix starts with an issue and a branch named after it, for example `fix/135-csv-file-visualization-error-in-qgis-plugin`. Fill in `.github/pull_request_template.md` when opening a PR.
- Commit subjects: the `commitizen` hook in `.pre-commit-config.yaml` enforces Conventional Commits, but only after `pre-commit install --hook-type commit-msg`. History before 2.0 uses plain imperative subjects (`Fix #128`).
- Version bump: `cz bump` rewrites `pyproject.toml`, `plugin/__version__.py` and `metadata.txt` together and updates `CHANGELOG.md`. `doc/source/conf.py` keeps its own `__version__`/`__release__` and is not touched, so update it by hand.
- User-facing changes also need the matching `.rst` page in `doc/source/` updated.
- The plugin must work on Linux, macOS and Windows: build paths with `os.path.join` or `pathlib`.

## v1 architecture (the live plugin)

**Load path:** `__init__.py::classFactory` → `plugin/core.py::RUBEMHydrological` (toolbar action, menu, translator) → `plugin/dialog/__init__.py::RUBEMHydrologicalDialog` (a `QDialog` mixed with the generated `Ui_RUBEMHydrological`).

**Dialog methods are spread across modules.** The class body of `RUBEMHydrologicalDialog` imports module-level functions from `plugin/dialog/_*.py` (`from ._tab_climate import ...`, `from ._project import ...`), which binds them as methods. Every function in those modules takes `self` = the dialog and reaches widgets by their Qt Designer object names (`self.textBrowser_log`, `self.progressBar`, ...). To add a handler, write it in the matching `_tab_*.py` / `_*.py` and add its name to the import list in the class body.

**Project file.** The dialog keeps values in a `ConfigParser` seeded from `plugin/validation/schemas.py::defaultConfigSchema`. `saveProject()` writes the legacy JSON document RUBEM `main` accepts (uppercase sections, no `version` field) and a sibling `<name>.qgs`. `RASTERS.demtif` in the dialog is `RASTERS.georeference` in that JSON. `DIRECTORIES.input` stays in the dialog and is omitted from the file. Format 1.0 (`version` present) is a different document and `read_legacy_json` rejects it. The model checkout is part of the codebase (the submodule), not a path stored in the environment (`https://12factor.net/codebase`). `plugin/validation/legacy_json.py` validates that document with the submodule's pydantic model `ModelConfigurationFile`. Pydantic `>=2.11,<3` is the same requirement as the submodule. When the QGIS interpreter does not have it, saving or opening a project asks before installing that one package into an isolated environment.

**Execution:** `dialog/_worker.py::setRunState` calls `plugin/engine.py`, which imports the pinned submodule `external/rubem-model` and runs `rubem.api.Model.from_file(...).run_isolated()`. There is no `rubem` executable. The run is gated on importing native `pcraster` and GDAL. The PCRaster Tools processing plugin, release 0.4.0, declares QGIS <= 3.99, so it is not a `plugin_dependencies` entry for this QGIS 4 plugin. PCRaster is a conda or OSGeo4W library, not a pip package. Plugin updates stay with the QGIS plugin manager. Cancel explains that the isolated process is not stopped.

**Results:** `_tab_results.py` finds output files by the names in `_mappings.py` and lists them in tree views. `report/plotter.py` plots time series (matplotlib/pandas) and `utils/raster.py` reads rasters through GDAL.

**Imports:** `plugin/` has no `__init__.py`, and QGIS imports the plugin under whatever its install folder is named. v1 modules therefore use relative imports with a bare-name fallback. Qt comes from `qgis.PyQt`, which on QGIS 4.2 is PyQt6. The dialog class is generated by `pyuic6`. There is no PyQt5 fallback.

```python
try:
    from ..utils.series import splitDirFilePrefix
except ImportError:
    from utils.series import splitDirFilePrefix
```

**Docstrings:** v1 modules use reST (`:param x:`) and v2 modules use Google style. Use the style of the module you are editing.

## v2 layer (scaffolding, not wired in)

The v2 layer is `plugin/{models,services,controllers,views,workers}/`, `plugin/core_refactored.py`, `plugin/exceptions.py` and `plugin/logging.py`. Its design is written up in `DEVELOPMENT.md`, `MIGRATION.md` and `MVC_IMPLEMENTATION.md`. These points aren't obvious from those docs:

- Nothing on the QGIS load path imports it. `classFactory` still loads `plugin/core.py`, and `MainController` has no caller outside `plugin/controllers/`.
- It uses absolute `from plugin.X import ...`. That resolves under `python -m pytest` from the repo root but not when QGIS loads the package by folder name. Wiring it in means switching to the v1 relative-import pattern.
- `plugin/models::RUBEMConfig` (pydantic) uses different field names from `defaultConfigSchema`'s INI sections and keys, and `_transform_ini_dict` / `to_ini_file` are stubs. Do not treat it as the project document or as the JSON the model runs. Its calibration bounds (for example `alpha <= 1`) disagree with the live default `4.500`.
- The live save and open path validates the project with the submodule's pydantic model. `plugin/models::RUBEMConfig` is not that model.
