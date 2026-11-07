"""GDAL raster helper unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _write_tiny_geotiff(path: Path) -> None:
    gdal = pytest.importorskip("osgeo.gdal")
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(str(path), 2, 2, 1, gdal.GDT_Float32)
    ds.SetGeoTransform((0.0, 1.0, 0.0, 0.0, 0.0, -1.0))
    band = ds.GetRasterBand(1)
    band.WriteArray(__import__("numpy").array([[1.0, 2.0], [3.0, 4.0]]))
    ds.FlushCache()
    ds = None


def test_get_value_from_raster_reads_pixel(tmp_path: Path) -> None:
    """Sample a known pixel from a tiny GeoTIFF."""
    pytest.importorskip("numpy")
    path = tmp_path / "tiny.tif"
    _write_tiny_geotiff(path)
    from plugin.utils.raster import getValueFromRaster

    # Geotransform origin (0,0), pixel (0,0) → value 1.0
    assert getValueFromRaster(str(path), 0.5, -0.5) == pytest.approx(1.0)


def test_get_values_from_raster_series(tmp_path: Path) -> None:
    """Series helper returns one value per raster path."""
    pytest.importorskip("numpy")
    path = tmp_path / "tiny.tif"
    _write_tiny_geotiff(path)
    from plugin.utils.raster import getValuesFromRasterSeries

    values = getValuesFromRasterSeries([str(path), str(path)], 0.5, -0.5)
    assert len(values) == 2
    assert values[0] == pytest.approx(1.0)
    assert values[1] == pytest.approx(1.0)
