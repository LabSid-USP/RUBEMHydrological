"""Pure-Python packages the QGIS interpreter does not ship.

PCRaster stays a native library of the QGIS environment. Pydantic is the
schema library the RUBEM submodule already requires (``pydantic>=2.11,<3``).
When it is missing, the plugin can install that one package into an isolated
virtual environment after the user agrees. The install is ``python -m pip``
with a fixed argument list, and its output is kept on the logger
``rubem_hydrological.dependencies``.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

PYDANTIC_REQUIREMENT = "pydantic>=2.11,<3"
_LOGGER = logging.getLogger("rubem_hydrological.dependencies")


class PydanticUnavailable(ImportError):
    """Pydantic is missing or older than the submodule requires."""


def ensure_pydantic(*, install: bool = False) -> None:
    """Import a new enough Pydantic, optionally installing it first.

    :param install: When true and the import fails, create the isolated
        environment and install :data:`PYDANTIC_REQUIREMENT`.
    :raises PydanticUnavailable: The package is missing and ``install`` is false.
    :raises RuntimeError: The install was requested and pip failed.
    """
    if _pydantic_is_usable():
        return
    if not install:
        raise PydanticUnavailable(
            "Pydantic "
            f"{PYDANTIC_REQUIREMENT} is not available to this QGIS Python. "
            "It is the schema library of the RUBEM submodule. "
            "The plugin can install it into an isolated environment."
        )
    _install_pydantic()
    if not _pydantic_is_usable():
        raise RuntimeError(
            f"pip reported success but {PYDANTIC_REQUIREMENT} still does not import."
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


def _pydantic_is_usable() -> bool:
    try:
        import pydantic
    except ImportError:
        return False
    numbers: list[int] = []
    for piece in pydantic.__version__.split("."):
        digits = ""
        for character in piece:
            if not character.isdigit():
                break
            digits += character
        if not digits:
            break
        numbers.append(int(digits))
    return tuple(numbers[:2]) >= (2, 11)


def _install_pydantic() -> None:
    destination = dependency_environment()
    python = _venv_python(destination)
    _LOGGER.info("Installing %s into %s", PYDANTIC_REQUIREMENT, destination)
    if not python.is_file():
        _run([sys.executable, "-m", "venv", str(destination)])
    _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            PYDANTIC_REQUIREMENT,
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
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.stdout:
        _LOGGER.info(completed.stdout.rstrip())
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
