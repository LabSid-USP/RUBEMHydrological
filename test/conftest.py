"""Pytest configuration and fixtures for RUBEM Hydrological tests.

Unit tests fake QGIS and must run with ``-p no:pytest_qgis -p no:pytestqt``.
Integration/GUI tests use pytest-qgis + pytest-qt against a real offscreen
QGIS application.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESOURCES_RCC = ROOT / "plugin" / "gui" / "generated" / "resources.rcc"


@pytest.fixture
def plugin_dir() -> Path:
    """Path to the live ``plugin/`` package."""
    return ROOT / "plugin"


@pytest.fixture
def test_data_dir() -> Path:
    """Path to ``test/fixtures``."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_qgis_iface() -> MagicMock:
    """Minimal iface stub for constructing ``RUBEMHydrologicalDialog``."""
    iface = MagicMock()
    iface.mainWindow.return_value = None
    iface.mapCanvas.return_value = MagicMock()
    iface.addToolBarIcon = MagicMock()
    iface.removeToolBarIcon = MagicMock()
    iface.addPluginToRasterMenu = MagicMock()
    iface.removePluginRasterMenu = MagicMock()
    iface.newProject = MagicMock()
    iface.messageBar.return_value = MagicMock()
    return iface


# Keep the historical name used by older docs/examples.
@pytest.fixture
def mock_qgis_interface(mock_qgis_iface: MagicMock) -> MagicMock:
    """Alias of :func:`mock_qgis_iface`."""
    return mock_qgis_iface


@pytest.fixture
def registered_resources() -> str:
    """Register the plugin ``.rcc`` once per test that needs ``:/...`` icons."""
    from qgis.PyQt.QtCore import QResource

    path = str(RESOURCES_RCC)
    if not QResource.registerResource(path):
        pytest.fail(f"Could not register Qt resources: {path}")
    try:
        yield path
    finally:
        QResource.unregisterResource(path)


@pytest.fixture
def dialog(qgis_iface, registered_resources, qtbot):
    """Real ``RUBEMHydrologicalDialog`` owned by pytest-qgis + qtbot."""
    from plugin.dialog import RUBEMHydrologicalDialog

    assert registered_resources  # ensure .rcc fixture ran
    dlg = RUBEMHydrologicalDialog(qgis_iface)
    qtbot.addWidget(dlg)
    return dlg
