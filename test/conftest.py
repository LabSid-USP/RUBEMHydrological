"""Pytest configuration and fixtures for RUBEM Hydrological tests.

This module provides common fixtures and configuration for all tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def plugin_dir() -> Path:
    """Fixture providing the plugin directory path.

    Returns:
        Path to the plugin directory.
    """
    return Path(__file__).parent.parent / "plugin"


@pytest.fixture
def test_data_dir() -> Path:
    """Fixture providing the test data directory path.

    Returns:
        Path to the test fixtures directory.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_qgis_interface() -> MagicMock:
    """Fixture providing a mocked QGIS interface.

    Returns:
        Mock object simulating QgisInterface.
    """
    iface = MagicMock()
    iface.mainWindow.return_value = MagicMock()
    iface.mapCanvas.return_value = MagicMock()
    iface.addToolBarIcon = MagicMock()
    iface.removeToolBarIcon = MagicMock()
    iface.addPluginToMenu = MagicMock()
    iface.removePluginMenu = MagicMock()
    return iface


@pytest.fixture
def sample_config_dict() -> dict[str, Any]:
    """Fixture providing a sample configuration dictionary.

    Returns:
        Dictionary with sample configuration data.
    """
    return {
        "sim_time": {
            "start": "2020-01-01",
            "end": "2020-12-31",
        },
        "directories": {
            "input": "/path/to/input",
            "output": "/path/to/output",
        },
        "filename_prefixes": {
            "dem": "dem",
            "clone": "clone",
            "ndvi": "ndvi",
            "landuse": "lulc",
            "soil": "soil",
        },
        "raster_files": {
            "dem": "/path/to/dem.tif",
            "clone": "/path/to/clone.map",
            "ndvi_dir": "/path/to/ndvi/",
            "landuse_dir": "/path/to/lulc/",
            "soil": "/path/to/soil.tif",
        },
        "table_files": {
            "climate": "/path/to/climate.csv",
            "landuse": "/path/to/landuse_params.csv",
            "soil": "/path/to/soil_params.csv",
        },
        "calibration": {
            "alpha": 0.5,
            "beta": 1.5,
            "lambda_factor": 0.3,
            "kc": 1.0,
            "field_capacity": 0.35,
            "wilting_point": 0.15,
        },
        "output_options": {
            "generate_timeseries": True,
            "generate_maps": True,
            "generate_stats": True,
        },
        "raster_format": {
            "format": "geotiff",
            "compression": True,
            "compression_level": 6,
        },
    }


@pytest.fixture
def sample_ini_config(tmp_path: Path) -> Path:
    """Fixture creating a sample INI configuration file.

    Args:
        tmp_path: Temporary directory path provided by pytest.

    Returns:
        Path to the created configuration file.
    """
    config_content = """[SIM_TIME]
start = 2020-01-01
end = 2020-12-31

[DIRECTORIES]
input = /path/to/input
output = /path/to/output

[FILENAME_PREFIXES]
dem = dem
clone = clone
ndvi = ndvi
landuse = lulc
soil = soil

[RASTERS]
dem = /path/to/dem.tif
clone = /path/to/clone.map
ndvi_dir = /path/to/ndvi/
landuse_dir = /path/to/lulc/
soil = /path/to/soil.tif

[TABLES]
climate = /path/to/climate.csv
landuse = /path/to/landuse_params.csv
soil = /path/to/soil_params.csv

[CALIBRATION]
alpha = 0.5
beta = 1.5
lambda_factor = 0.3
kc = 1.0
field_capacity = 0.35
wilting_point = 0.15

[GENERATE_FILE]
generate_timeseries = True
generate_maps = True
generate_stats = True

[RASTER_FILE_FORMAT]
format = geotiff
compression = True
compression_level = 6
"""

    config_file = tmp_path / "test_config.ini"
    config_file.write_text(config_content)
    return config_file


def pytest_configure(config: Any) -> None:
    """Configure pytest with custom markers.

    Args:
        config: Pytest configuration object.
    """
    config.addinivalue_line("markers", "unit: Unit tests that don't require QGIS")
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring QGIS environment"
    )
    config.addinivalue_line("markers", "slow: Slow running tests")
