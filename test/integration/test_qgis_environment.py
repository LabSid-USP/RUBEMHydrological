"""Basic QGIS runtime sanity checks for the integration job."""

from __future__ import annotations

import pytest
from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry, QgsRasterLayer

pytestmark = pytest.mark.integration


def test_providers_include_gdal_and_ogr(qgis_app) -> None:
    """GDAL/OGR providers must be available in the QGIS test image."""
    del qgis_app  # fixture ensures QgsApplication is initialized
    keys = QgsProviderRegistry.instance().providerList()
    assert "gdal" in keys
    assert "ogr" in keys


def test_wgs84_crs_is_valid(qgis_app) -> None:
    """EPSG:4326 must resolve so CRS-dependent UI paths do not crash."""
    del qgis_app
    crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
    assert crs.isValid()


def test_invalid_raster_path_is_not_valid(qgis_app, tmp_path) -> None:
    """A missing raster path yields an invalid layer (API smoke)."""
    del qgis_app
    layer = QgsRasterLayer(str(tmp_path / "missing.tif"), "missing")
    assert not layer.isValid()
