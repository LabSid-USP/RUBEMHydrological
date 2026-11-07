"""Pure-Python packages the QGIS interpreter does not ship.

PCRaster stays a native library of the QGIS environment. Pydantic is the
schema library the RUBEM submodule already requires (``pydantic>=2.11,<3``);
``humanize>=4`` and ``python-dateutil>=2`` are its other pure-Python
requirements. When pydantic is missing, the plugin can install those packages
into an isolated virtual environment after the user agrees. The environment
is created with the interpreter from ``resolve_host_python`` (``sys.executable``
can be QGIS itself), never by assuming the host executable is Python. The
install is ``python -m pip``
with a fixed argument list, and its output is kept on the logger
``rubem_hydrological.dependencies``.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from pathlib import Path

try:
    from .engine import resolve_host_python
except ImportError:
    from engine import resolve_host_python

PYDANTIC_REQUIREMENT = "pydantic>=2.11,<3"
HUMANIZE_REQUIREMENT = "humanize>=4"
DATEUTIL_REQUIREMENT = "python-dateutil>=2"
ISOLATED_REQUIREMENTS = (
    PYDANTIC_REQUIREMENT,
    HUMANIZE_REQUIREMENT,
    DATEUTIL_REQUIREMENT,
)
_LOGGER = logging.getLogger("rubem_hydrological.dependencies")


class PydanticUnavailable(ImportError):
    """Pydantic is missing or older than the submodule requires."""


def ensure_pydantic(*, install: bool = False) -> None:
    """Import a new enough Pydantic, optionally installing it first.

    An environment created earlier is put on ``sys.path`` before the import.
    A Pydantic that is already imported and outside :data:`PYDANTIC_REQUIREMENT`
    is not replaced: Python will keep serving the cached module.

    :param install: When true and no compatible package can be imported, create
        the isolated environment and install :data:`PYDANTIC_REQUIREMENT`.
    :raises PydanticUnavailable: The package is missing, or an incompatible
        copy is already loaded.
    :raises RuntimeError: The install was requested and pip failed.
    """
    if _cached_pydantic_status() == "ok":
        _require_or_install_extras(install=install)
        return
    if _cached_pydantic_status() == "incompatible":
        raise PydanticUnavailable(
            "This interpreter already loaded Pydantic "
            f"{_loaded_version()}, which is outside {PYDANTIC_REQUIREMENT}. "
            "Restart QGIS with a compatible installation. "
            "This plugin will not replace a package that is already imported."
        )
    _activate_existing_environment()
    found = _distribution_version()
    if found and pydantic_version_is_supported(found):
        import pydantic  # noqa: F401

        _require_or_install_extras(install=install)
        return
    if not install:
        raise PydanticUnavailable(
            "Pydantic "
            f"{PYDANTIC_REQUIREMENT} is not available to this QGIS Python. "
            "It is the schema library of the RUBEM submodule. "
            "The plugin can install it into an isolated environment."
        )
    _install_pydantic()
    _activate_existing_environment()
    if "pydantic" in sys.modules and _cached_pydantic_status() != "ok":
        raise PydanticUnavailable(
            f"Installed {PYDANTIC_REQUIREMENT}, but this process already "
            "imported another Pydantic. Restart QGIS and open the project again."
        )
    import pydantic

    if not pydantic_version_is_supported(pydantic.__version__):
        raise PydanticUnavailable(
            f"Installed {PYDANTIC_REQUIREMENT}, but imported "
            f"{pydantic.__version__}. Restart QGIS and open the project again."
        )


def _pure_python_modules_missing() -> list[str]:
    """Return import names still missing after activating the isolated env."""
    import importlib.util

    missing: list[str] = []
    for module_name in ("humanize", "dateutil"):
        try:
            found = importlib.util.find_spec(module_name) is not None
        except (ImportError, ValueError):
            found = False
        if not found:
            missing.append(module_name)
    return missing


def _require_or_install_extras(*, install: bool) -> None:
    """Ensure humanize/dateutil are importable once Pydantic itself is usable.

    Save and open call ``ensure_pydantic()`` without ``install=True``. When
    Pydantic is already present but the extras are not, raise
    :class:`PydanticUnavailable` so the dialog can offer the same isolated
    install path that Run otherwise never reaches.
    """
    _activate_existing_environment()
    missing = _pure_python_modules_missing()
    if not missing:
        return
    if install:
        _ensure_isolated_extras()
        return
    labels = ", ".join(
        "python-dateutil" if name == "dateutil" else name for name in missing
    )
    raise PydanticUnavailable(
        "RUBEM also needs "
        f"{labels}. The plugin can install {', '.join(ISOLATED_REQUIREMENTS)} "
        "into an isolated environment."
    )


def _ensure_isolated_extras() -> None:
    """Install humanize/dateutil when Pydantic is already present but they are not."""
    _activate_existing_environment()
    if not _pure_python_modules_missing():
        return
    _install_pydantic()
    _activate_existing_environment()
    still_missing = _pure_python_modules_missing()
    if still_missing:
        raise RuntimeError(
            "Installed "
            + ", ".join(ISOLATED_REQUIREMENTS)
            + f" but still missing: {', '.join(still_missing)}"
        )


def dependency_environment() -> Path:
    """Directory of the isolated environment for pure-Python packages.

    ``RUBEM_HYDROLOGICAL_PYTHON_DEPS`` overrides the default under the user
    data directory. The repository tree is not a place for an installed
    environment.
    """
    override = os.environ.get("RUBEM_HYDROLOGICAL_PYTHON_DEPS", "").strip()
    if override:
        return Path(override)
    return Path.home() / ".local" / "share" / "rubem-hydrological" / "python-deps"


def pydantic_version_is_supported(version: str) -> bool:
    """Return whether ``version`` is inside ``>=2.11,<3``."""
    numbers: list[int] = []
    for piece in version.split("."):
        digits = ""
        for character in piece:
            if not character.isdigit():
                break
            digits += character
        if not digits:
            break
        numbers.append(int(digits))
    while len(numbers) < 3:
        numbers.append(0)
    major, minor, patch = numbers[:3]
    return (major, minor, patch) >= (2, 11, 0) and major < 3


def _loaded_version() -> str | None:
    module = sys.modules.get("pydantic")
    if module is None:
        return None
    return getattr(module, "__version__", None)


def _cached_pydantic_status() -> str:
    """Classify the Pydantic module only if it is already imported."""
    version = _loaded_version()
    if version is None:
        return "missing"
    if pydantic_version_is_supported(version):
        return "ok"
    return "incompatible"


def _distribution_version() -> str | None:
    """Return the installed Pydantic version without importing the module."""
    try:
        return distribution_version("pydantic")
    except PackageNotFoundError:
        return None


def _activate_existing_environment() -> None:
    """Add an already-created dependency environment to ``sys.path``."""
    site = _site_packages(dependency_environment())
    if not site.is_dir():
        return
    entry = str(site)
    if entry not in sys.path:
        sys.path.insert(0, entry)


def _install_pydantic() -> None:
    destination = dependency_environment()
    python = _venv_python(destination)
    _LOGGER.info("Installing %s into %s", ", ".join(ISOLATED_REQUIREMENTS), destination)
    if not python.is_file():
        host_python = resolve_host_python()
        if host_python is None:
            raise RuntimeError(
                "Could not find a Python interpreter to create the "
                f"dependency environment at {destination}: sys.executable "
                f"is {sys.executable!r} and no Python interpreter was found "
                "under the interpreter prefixes or beside it."
            )
        _run([str(host_python), "-m", "venv", str(destination)])
    _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            *ISOLATED_REQUIREMENTS,
        ]
    )
    site = _site_packages(destination)
    entry = str(site)
    if entry not in sys.path:
        sys.path.insert(0, entry)


def _venv_python(destination: Path) -> Path:
    if sys.platform == "win32":
        return destination / "Scripts" / "python.exe"
    return destination / "bin" / "python"


def _site_packages(destination: Path) -> Path:
    if sys.platform == "win32":
        return destination / "Lib" / "site-packages"
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    return destination / "lib" / version / "site-packages"


def _run(command: list[str]) -> None:
    completed = subprocess.run(
        command, check=False, capture_output=True, text=True, timeout=300
    )
    if completed.stdout:
        _LOGGER.info(completed.stdout.rstrip())
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
