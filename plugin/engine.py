"""Locate the RUBEM process without baking a deploy path into the source.

`RUBEM_EXECUTABLE` and `RUBEM_PYTHON` are orthogonal environment variables, as
`https://12factor.net/config`_ requires. The hydrological project is a JSON
file, not this deploy config. The model is a separate process: its environment
does not inherit the QGIS library paths.
"""

from __future__ import annotations

import os
import shutil

# QGIS activation exports these. Leaving them in the child makes the model use
# QGIS's GDAL, PROJ and Python instead of its own.
_QGIS_PROCESS_KEYS = (
    "PYTHONPATH",
    "PYTHONHOME",
    "GDAL_DATA",
    "GDAL_DRIVER_PATH",
    "PROJ_DATA",
    "PROJ_LIB",
    "QT_PLUGIN_PATH",
    "QGIS_PREFIX_PATH",
    "GEOTIFF_CSV",
    "PDAL_DRIVER_PATH",
)


def command_prefix(environ: dict[str, str] | None = None) -> list[str]:
    """Return the argv prefix that invokes ``rubem``.

    :param environ: Environment to read. Defaults to :data:`os.environ`.
    :returns: ``[executable]`` or ``[python, "-m", "rubem"]``.
    :raises FileNotFoundError: Neither variable is set and ``rubem`` is not on
        ``PATH``.
    """
    env = os.environ if environ is None else environ
    executable = env.get("RUBEM_EXECUTABLE", "").strip()
    if executable:
        return [executable]
    python = env.get("RUBEM_PYTHON", "").strip()
    if python:
        return [python, "-m", "rubem"]
    found = shutil.which("rubem", path=env.get("PATH"))
    if found:
        return [found]
    raise FileNotFoundError(
        "RUBEM is not configured. Set RUBEM_EXECUTABLE to the rubem program "
        "or RUBEM_PYTHON to the interpreter of a RUBEM environment."
    )


def child_environment(environ: dict[str, str] | None = None) -> dict[str, str]:
    """Copy ``environ`` without the variables QGIS injects into this process.

    :param environ: Environment to copy. Defaults to :data:`os.environ`.
    """
    env = dict(os.environ if environ is None else environ)
    for key in _QGIS_PROCESS_KEYS:
        env.pop(key, None)
    return env
