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
    entry = str(path.resolve())
    # Prefer the pinned checkout over any earlier ``rubem`` on ``sys.path``.
    while entry in sys.path:
        sys.path.remove(entry)
    sys.path.insert(0, entry)

    loaded = sys.modules.get("rubem")
    if loaded is not None:
        loaded_file = getattr(loaded, "__file__", None)
        if loaded_file is not None:
            loaded_root = Path(loaded_file).resolve().parents[1]
            if loaded_root != path.resolve():
                for name in list(sys.modules):
                    if name == "rubem" or name.startswith("rubem."):
                        del sys.modules[name]
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
    ``pcraster`` module itself. The submodule's pure-Python requirements
    (``humanize`` and ``python-dateutil``) are checked after the native
    ones, with the plugin's isolated dependency environment activated.

    :raises FileNotFoundError: The submodule is missing.
    :raises ImportError: ``pcraster``, GDAL, ``humanize`` or ``dateutil``
        cannot be imported.
    """
    root = ensure_submodule_on_path()
    from rubem._deps import missing_runtime_deps, runtime_deps_message

    missing = missing_runtime_deps()
    if missing:
        raise ImportError(runtime_deps_message(missing))
    try:
        try:
            from .dependencies import _activate_existing_environment
        except ImportError:
            from dependencies import _activate_existing_environment

        _activate_existing_environment()
    except Exception:
        pass
    import importlib.util

    missing_pure: list[str] = []
    for module_name, requirement in (
        ("humanize", "humanize"),
        ("dateutil", "python-dateutil"),
    ):
        try:
            found = importlib.util.find_spec(module_name) is not None
        except (ImportError, ValueError):
            found = False
        if not found:
            missing_pure.append(requirement)
    if missing_pure:
        raise ImportError(
            "RUBEM cannot run because the following pure-Python dependencies "
            f"are not installed: {', '.join(missing_pure)}. They are installed "
            "with pydantic into the plugin's isolated dependency environment "
            "when a project is opened or saved."
        )
    return root


def _looks_like_python(path: Path) -> bool:
    return path.name.lower().startswith("python")


def resolve_host_python(
    *,
    executable: str | Path | None = None,
    base_executable: str | Path | None = None,
    prefixes: list[str | Path] | tuple[str | Path, ...] | None = None,
    platform: str | None = None,
    version_info: tuple[int, int] | None = None,
) -> Path | None:
    """Find the host Python interpreter when QGIS, not Python, is ``sys.executable``.

    Preference order: ``sys.executable`` itself when it is named like Python,
    then interpreters under ``sys.exec_prefix`` / ``sys.prefix`` /
    ``sys.base_prefix`` (so the interpreter that owns the running stdlib
    wins), then ``sys._base_executable``, then siblings of the host
    executable, then the OSGeo4W ``apps/Python<major><minor>`` layout
    (other ``Python*`` globs after it) on Windows or
    ``<host dir>/bin/python3`` elsewhere. Every candidate
    after ``sys.executable`` itself must exist on disk; nothing is taken from
    ``PATH``. The keyword arguments exist for tests and default to the running
    interpreter's ``sys`` values.

    :returns: The interpreter path, or ``None`` when no candidate exists.
    """
    platform_name = sys.platform if platform is None else platform
    is_windows = platform_name == "win32"
    major, minor = (
        (sys.version_info[0], sys.version_info[1])
        if version_info is None
        else version_info
    )

    if executable is None:
        executable = sys.executable
    if not executable:
        return None
    executable = Path(executable)
    if _looks_like_python(executable):
        return executable

    if base_executable is None:
        base_executable = getattr(sys, "_base_executable", None)

    if prefixes is None:
        prefixes = [
            value
            for attr in ("exec_prefix", "prefix", "base_exec_prefix", "base_prefix")
            if (value := getattr(sys, attr, None))
        ]

    candidates: list[Path] = []
    seen: set[str] = set()

    def add(candidate: Path) -> None:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            candidates.append(candidate)

    # Prefix-derived interpreters first: they own the stdlib already in use.
    seen_prefixes: set[str] = set()
    for raw_prefix in prefixes:
        prefix = Path(raw_prefix)
        if str(prefix) in seen_prefixes:
            continue
        seen_prefixes.add(str(prefix))
        if is_windows:
            for name in ("python.exe", "python3.exe", "pythonw.exe"):
                add(prefix / name)
            add(prefix / "Scripts" / "python.exe")
        else:
            for name in ("python3", "python", f"python{major}.{minor}"):
                add(prefix / "bin" / name)

    if base_executable:
        base_path = Path(base_executable)
        if _looks_like_python(base_path):
            add(base_path)

    # Siblings of the host executable (e.g. python.exe beside qgis-bin.exe).
    if is_windows:
        for name in ("python.exe", "python3.exe", "pythonw.exe"):
            add(executable.with_name(name))
    else:
        for name in ("python3", "python", f"python{major}.{minor}"):
            add(executable.with_name(name))

    # Layout-specific fallbacks (no PATH lookup).
    if is_windows:
        exact = f"Python{major}{minor}"
        for base in (executable.parent.parent, executable.parent):
            apps = base / "apps"
            add(apps / exact / "python.exe")
            # Only same major.minor: a mismatched Python3xx would create a
            # venv whose site-packages path does not match this process.
            for candidate in sorted(apps.glob("Python*/python.exe")):
                folder = candidate.parent.name
                if folder.lower() == exact.lower():
                    continue
                digits = "".join(ch for ch in folder if ch.isdigit())
                if digits == f"{major}{minor}":
                    add(candidate)
    else:
        add(executable.parent / "bin" / "python3")
        add(executable.parent / "bin" / "python")
        add(executable.parent / "bin" / f"python{major}.{minor}")
        if platform_name == "darwin":
            # Contents/MacOS/bin/python3 in an app bundle; this is the
            # ``executable.parent / bin`` candidate above when the host
            # binary itself lives in Contents/MacOS.
            add(executable.parent / "MacOS" / "bin" / "python3")

    return next((c for c in candidates if c.is_file()), None)


def configure_spawn_executable() -> None:
    """Point multiprocessing at a Python interpreter when QGIS is the host.

    CPython documents ``multiprocessing.set_executable`` for programs embedded
    in another executable. On Windows, QGIS has reported ``sys.executable`` as
    the QGIS program rather than Python. This switches to the interpreter
    found by :func:`resolve_host_python`. When the host is not Python and no
    candidate exists, raise instead of leaving ``qgis-bin`` as the spawn
    executable.
    """
    executable = resolve_host_python()
    host = Path(sys.executable) if sys.executable else None
    if executable is None:
        if host is None or not _looks_like_python(host):
            raise RuntimeError(
                "Could not find a Python interpreter for the isolated RUBEM "
                f"process: sys.executable is {sys.executable!r}."
            )
        return
    if host is None or executable != host:
        multiprocessing.set_executable(str(executable))


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
