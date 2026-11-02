"""Run RUBEM from the git submodule inside this repository.

The model is not an executable shipped beside the plugin. ``external/rubem-model``
is the pinned source, and :meth:`rubem.api.Model.run_isolated` is the supported
way to run it without leaving PCRaster's process-wide clone inside QGIS.

PCRaster itself is not a pip package. The PCRaster Tools plugin
(https://plugins.qgis.org/plugins/pcraster_tools/) is the QGIS integration, and
its manual requires PCRaster in the same environment as QGIS. The release
published on 2025-05-27 (0.4.0) declares ``qgisMaximumVersion`` 3.99, so QGIS
4.2 cannot install that package from the official repository.
"""

from __future__ import annotations

import multiprocessing
import sys
from pathlib import Path

PCRASTER_TOOLS_ID = "pcraster_tools"
PCRASTER_TOOLS_NAME = "PCRaster Tools"
PCRASTER_TOOLS_URL = "https://plugins.qgis.org/plugins/pcraster_tools/"
PCRASTER_TOOLS_MANUAL = "https://jvdkwast.github.io/qgis-processing-pcraster/"


def submodule_path() -> Path:
    """Return the RUBEM checkout pinned next to this plugin.

    :returns: ``<plugin root>/external/rubem-model``.
    """
    return Path(__file__).resolve().parents[1] / "external" / "rubem-model"


def ensure_submodule_on_path(root: Path | None = None) -> Path:
    """Put the submodule on ``sys.path`` so ``import rubem`` resolves to it.

    :param root: Override the checkout, used by tests.
    :raises FileNotFoundError: The checkout has no ``rubem/api.py``.
    """
    path = submodule_path() if root is None else Path(root)
    api = path / "rubem" / "api.py"
    if not api.is_file():
        raise FileNotFoundError(
            f"The RUBEM submodule is not available at {path}. "
            "Initialize it with 'git submodule update --init external/rubem-model'."
        )
    entry = str(path)
    if entry not in sys.path:
        sys.path.insert(0, entry)
    return path


def pcraster_tools_message() -> str:
    """Explain the missing PCRaster Tools plugin without offering to pip-install it."""
    return (
        f"{PCRASTER_TOOLS_NAME} is not active. RUBEM's PCRaster operations come "
        f"from that plugin ({PCRASTER_TOOLS_URL}). Its manual is {PCRASTER_TOOLS_MANUAL}. "
        "The package published as 0.4.0 declares QGIS <= 3.99, so QGIS 4 does not "
        "install that release. This plugin does not download or pip-install it."
    )


def assert_pcraster_tools(active_ids: list[str]) -> None:
    """Require the PCRaster Tools plugin directory to be active.

    :param active_ids: Directory names from ``qgis.utils.active_plugins``.
    :raises RuntimeError: The plugin is not in that list.
    """
    if PCRASTER_TOOLS_ID not in active_ids:
        raise RuntimeError(pcraster_tools_message())


def qgis_active_plugin_ids() -> list[str]:
    """Return the directory ids of plugins QGIS has loaded."""
    try:
        from qgis.utils import active_plugins
    except Exception:
        return []
    return list(active_plugins)


def assert_ready() -> Path:
    """Check the submodule and the native ``pcraster`` and GDAL imports.

    The published PCRaster Tools plugin declares QGIS <= 3.99, so a hard
    dependency on it cannot be installed on QGIS 4. RUBEM imports the
    ``pcraster`` module itself.

    :raises FileNotFoundError: The submodule is missing.
    :raises ImportError: ``pcraster`` or GDAL cannot be imported.
    """
    root = ensure_submodule_on_path()
    from rubem._deps import missing_runtime_deps, runtime_deps_message

    missing = missing_runtime_deps()
    if missing:
        raise ImportError(runtime_deps_message(missing))
    return root


def configure_spawn_executable() -> None:
    """Point multiprocessing at a Python interpreter when QGIS is the host.

    CPython documents ``multiprocessing.set_executable`` for programs embedded
    in another executable. On Windows, QGIS has reported ``sys.executable`` as
    the QGIS program rather than Python. This only switches when the current
    executable is not named like Python and a sibling ``python3`` exists.
    """
    executable = Path(sys.executable)
    if executable.name.lower().startswith("python"):
        return
    for candidate in (executable.with_name("python3"), executable.with_name("python")):
        if candidate.is_file():
            multiprocessing.set_executable(str(candidate))
            return


def run_project(config_path: str) -> str:
    """Run one project through the submodule API, outside the QGIS process.

    :param config_path: Legacy JSON project written by the dialog.
    :returns: A one-line description of the run result.
    :raises ImportError: PCRaster or GDAL is missing.
    :raises RuntimeError: The isolated subprocess dies.
    """
    assert_ready()
    configure_spawn_executable()
    from rubem.api import Model

    result = Model.from_file(config_path).run_isolated()
    return f"RUBEM wrote {result.output_directory}"
