"""Raster processing service for RUBEM Hydrological plugin.

This service handles all raster data operations.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

try:
    from qgis.core import (
        QgsRasterLayer,
        QgsRasterBandStats,
        QgsRectangle,
    )
except ImportError:
    QgsRasterLayer = None  # type: ignore
    QgsRasterBandStats = None  # type: ignore
    QgsRectangle = None  # type: ignore

from plugin.exceptions import RasterOperationError
from plugin.logging import get_logger
from plugin.services import BaseService

logger = get_logger(__name__)


class RasterService(BaseService):
    """Service for raster data operations.

    This service provides:
    - Raster loading and validation
    - Raster statistics calculation
    - Raster format conversion
    - Raster clipping and resampling
    """

    def __init__(self) -> None:
        """Initialize raster service."""
        super().__init__()
        self._loaded_rasters: dict[str, QgsRasterLayer] = {}

    def load_raster(self, file_path: str | Path) -> QgsRasterLayer:
        """Load raster file.

        Args:
            file_path: Path to raster file.

        Returns:
            Loaded raster layer.

        Raises:
            RasterOperationError: If loading fails.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Raster file not found: {path}")

            path_str = str(path)

            # Check cache
            if path_str in self._loaded_rasters:
                logger.debug(f"Returning cached raster: {path_str}")
                return self._loaded_rasters[path_str]

            # Load raster
            if QgsRasterLayer is None:
                raise ImportError("QGIS not available")

            layer = QgsRasterLayer(path_str, path.stem)

            if not layer.isValid():
                raise RasterOperationError(
                    f"Invalid raster layer: {path}",
                    details={"path": path_str},
                )

            # Cache layer
            self._loaded_rasters[path_str] = layer

            logger.info(f"Raster loaded successfully: {path}")
            return layer

        except Exception as e:
            logger.error(f"Failed to load raster: {e}")
            raise RasterOperationError(
                f"Failed to load raster: {file_path}",
                details={"error": str(e)},
            ) from e

    def get_raster_info(self, file_path: str | Path) -> dict:
        """Get raster information.

        Args:
            file_path: Path to raster file.

        Returns:
            Dictionary with raster information.

        Raises:
            RasterOperationError: If operation fails.
        """
        try:
            layer = self.load_raster(file_path)

            info = {
                "path": str(file_path),
                "width": layer.width(),
                "height": layer.height(),
                "band_count": layer.bandCount(),
                "extent": {
                    "xmin": layer.extent().xMinimum(),
                    "xmax": layer.extent().xMaximum(),
                    "ymin": layer.extent().yMinimum(),
                    "ymax": layer.extent().yMaximum(),
                },
                "crs": layer.crs().authid(),
            }

            logger.debug(f"Raster info retrieved: {info}")
            return info

        except Exception as e:
            logger.error(f"Failed to get raster info: {e}")
            raise RasterOperationError(
                f"Failed to get raster info: {file_path}",
                details={"error": str(e)},
            ) from e

    def get_raster_statistics(
        self,
        file_path: str | Path,
        band: int = 1,
    ) -> dict:
        """Get raster band statistics.

        Args:
            file_path: Path to raster file.
            band: Band number (1-based).

        Returns:
            Dictionary with statistics.

        Raises:
            RasterOperationError: If operation fails.
        """
        try:
            layer = self.load_raster(file_path)

            if band < 1 or band > layer.bandCount():
                raise ValueError(f"Invalid band number: {band}")

            provider = layer.dataProvider()
            stats = provider.bandStatistics(band)

            statistics = {
                "min": stats.minimumValue,
                "max": stats.maximumValue,
                "mean": stats.mean,
                "stddev": stats.stdDev,
                "sum": stats.sum,
                "range": stats.range,
            }

            logger.debug(f"Raster statistics: {statistics}")
            return statistics

        except Exception as e:
            logger.error(f"Failed to get raster statistics: {e}")
            raise RasterOperationError(
                f"Failed to get raster statistics: {file_path}",
                details={"error": str(e), "band": band},
            ) from e

    def validate_raster(self, file_path: str | Path) -> tuple[bool, list[str]]:
        """Validate raster file.

        Args:
            file_path: Path to raster file.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        try:
            path = Path(file_path)

            # Check file exists
            if not path.exists():
                errors.append(f"File does not exist: {path}")
                return False, errors

            # Try to load
            try:
                layer = self.load_raster(path)
            except Exception as e:
                errors.append(f"Failed to load raster: {e}")
                return False, errors

            # Check validity
            if not layer.isValid():
                errors.append("Invalid raster layer")
                return False, errors

            # Check has data
            if layer.bandCount() < 1:
                errors.append("Raster has no bands")
                return False, errors

            logger.debug(f"Raster validation passed: {path}")
            return True, []

        except Exception as e:
            logger.error(f"Raster validation error: {e}")
            errors.append(str(e))
            return False, errors

    def validate(self) -> tuple[bool, list[str]]:
        """Validate service state.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        return True, []  # Service has no state to validate

    def cleanup(self) -> None:
        """Cleanup service resources."""
        logger.debug("Cleaning up raster service")
        self._loaded_rasters.clear()
