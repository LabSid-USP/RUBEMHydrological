"""Smoke-test the QGIS load path for the live core plugin."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[2]


def test_entry_point_targets_live_core_not_v2() -> None:
    """Root ``classFactory`` must not load unwired ``core_refactored``."""
    source = (ROOT / "__init__.py").read_text(encoding="utf-8")
    assert "plugin.core" in source
    assert "core_refactored" not in source
    assert "MainController" not in source


def test_live_core_plugin_init_and_unload(qgis_iface, registered_resources) -> None:
    """Toolbar/menu registration must round-trip without raising."""
    del registered_resources
    from plugin.core import RUBEMHydrological

    plugin = RUBEMHydrological(qgis_iface)
    plugin.initGui()
    assert plugin.actions
    plugin.unload()
