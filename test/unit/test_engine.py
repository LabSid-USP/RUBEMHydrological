"""The model comes from the submodule, not from an executable path."""

from __future__ import annotations

from pathlib import Path

import pytest

from plugin.engine import (
    PCRASTER_TOOLS_ID,
    assert_pcraster_tools,
    assert_ready,
    ensure_submodule_on_path,
    pcraster_tools_message,
    submodule_path,
)


@pytest.mark.unit
def test_installed_pydantic_satisfies_the_submodule_pin() -> None:
    """A usable Pydantic does not trigger another install."""
    from plugin.dependencies import ensure_pydantic

    ensure_pydantic()


@pytest.mark.unit
def test_submodule_path_is_the_pinned_checkout() -> None:
    """The runner looks at external/rubem-model and nowhere else."""
    path = submodule_path()
    assert path.name == "rubem-model"
    assert path.parent.name == "external"
    assert (path / "rubem" / "api.py").is_file()


@pytest.mark.unit
def test_missing_submodule_is_reported(tmp_path: Path) -> None:
    """A checkout without the package is not treated as an installed command."""
    with pytest.raises(FileNotFoundError, match="git submodule update --init"):
        ensure_submodule_on_path(tmp_path)


@pytest.mark.unit
def test_inactive_pcraster_tools_names_the_plugin_and_refuses_pip() -> None:
    """The message points at the QGIS plugin and does not offer pip."""
    with pytest.raises(RuntimeError, match="PCRaster Tools") as exc:
        assert_pcraster_tools([])
    text = str(exc.value)
    assert PCRASTER_TOOLS_ID in pcraster_tools_message() or "plugins.qgis.org" in text
    assert "pip" in text
    assert "3.99" in text


@pytest.mark.unit
def test_ready_check_reaches_the_native_import_after_the_plugin() -> None:
    """With the plugin id present, the next failure is the missing pcraster module."""
    with pytest.raises(ImportError, match="pcraster"):
        assert_ready([PCRASTER_TOOLS_ID])
