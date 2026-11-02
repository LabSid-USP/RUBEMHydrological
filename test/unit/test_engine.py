"""Deploy configuration for the RUBEM process lives in the environment."""

from __future__ import annotations

import pytest

from plugin.engine import child_environment, command_prefix


@pytest.mark.unit
def test_executable_env_wins_over_python_and_path() -> None:
    """``RUBEM_EXECUTABLE`` is its own variable, not a named environment."""
    prefix = command_prefix(
        {
            "RUBEM_EXECUTABLE": "/opt/rubem/bin/rubem",
            "RUBEM_PYTHON": "/opt/rubem/bin/python",
            "PATH": "/usr/bin",
        }
    )
    assert prefix == ["/opt/rubem/bin/rubem"]


@pytest.mark.unit
def test_python_env_uses_the_module_entry_point() -> None:
    """``RUBEM_PYTHON`` launches ``python -m rubem``."""
    prefix = command_prefix({"RUBEM_PYTHON": "/opt/rubem/bin/python", "PATH": ""})
    assert prefix == ["/opt/rubem/bin/python", "-m", "rubem"]


@pytest.mark.unit
def test_missing_engine_names_the_variables() -> None:
    """An unconfigured deploy fails before a project file is involved."""
    with pytest.raises(FileNotFoundError, match="RUBEM_EXECUTABLE"):
        command_prefix({"PATH": ""})


@pytest.mark.unit
def test_child_environment_drops_qgis_library_paths() -> None:
    """The model process does not inherit QGIS's GDAL or Python path."""
    env = child_environment(
        {
            "PATH": "/usr/bin",
            "PYTHONPATH": "/qgis/python",
            "GDAL_DATA": "/qgis/gdal",
            "PROJ_DATA": "/qgis/proj",
            "HOME": "/home/user",
        }
    )
    assert env["PATH"] == "/usr/bin"
    assert env["HOME"] == "/home/user"
    assert "PYTHONPATH" not in env
    assert "GDAL_DATA" not in env
    assert "PROJ_DATA" not in env
