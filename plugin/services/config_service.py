"""Configuration service for RUBEM Hydrological plugin.

This service handles configuration-related business logic including
loading, saving, validation, and transformation of configuration data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from plugin.exceptions import ConfigurationError, FileOperationError, ValidationError
from plugin.logging import get_logger
from plugin.models import RUBEMConfig
from plugin.services import BaseService

logger = get_logger(__name__)


class ConfigService(BaseService):
    """Service for configuration management operations.

    This service provides:
    - Configuration loading from multiple formats
    - Configuration saving to multiple formats
    - Configuration validation
    - Configuration transformation and migration
    - Default configuration generation
    """

    def __init__(self) -> None:
        """Initialize configuration service."""
        super().__init__()
        self._cache: dict[str, RUBEMConfig] = {}

    def load_from_file(self, file_path: Path | str) -> RUBEMConfig:
        """Load configuration from file.

        Args:
            file_path: Path to configuration file.

        Returns:
            Loaded and validated configuration.

        Raises:
            FileOperationError: If file cannot be read.
            ConfigurationError: If configuration is invalid.
        """
        path = Path(file_path)
        logger.info(f"Loading configuration from: {path}")

        # Check cache first
        cache_key = str(path.absolute())
        if cache_key in self._cache:
            logger.debug(f"Returning cached configuration for: {path}")
            return self._cache[cache_key]

        if not path.exists():
            raise FileOperationError(
                f"Configuration file not found: {path}",
                details={"file": str(path)},
            )

        try:
            # Determine format and load
            if path.suffix == ".toml":
                config = RUBEMConfig.from_toml_file(path)
            elif path.suffix == ".json":
                config = RUBEMConfig.from_json_file(path)
            elif path.suffix == ".ini":
                config = RUBEMConfig.from_ini_file(path)
            else:
                raise ConfigurationError(
                    f"Unsupported file format: {path.suffix}",
                    details={"file": str(path), "supported": [".toml", ".json", ".ini"]},
                )

            # Validate after loading
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                raise ConfigurationError(
                    "Configuration validation failed",
                    details={"file": str(path), "errors": errors},
                )

            # Cache the loaded configuration
            self._cache[cache_key] = config

            logger.info(f"Configuration loaded successfully from: {path}")
            return config

        except Exception as e:
            if isinstance(e, (ConfigurationError, FileOperationError)):
                raise
            raise ConfigurationError(
                f"Failed to load configuration: {e}",
                details={"file": str(path), "error": str(e)},
            ) from e

    def save_to_file(
        self,
        config: RUBEMConfig,
        file_path: Path | str,
        format: str | None = None,
    ) -> None:
        """Save configuration to file.

        Args:
            config: Configuration to save.
            file_path: Path where to save.
            format: Optional format override ('toml', 'json', 'ini').
                   If None, inferred from file extension.

        Raises:
            ConfigurationError: If configuration cannot be saved.
        """
        path = Path(file_path)
        logger.info(f"Saving configuration to: {path}")

        # Validate before saving
        is_valid, errors = self.validate_config(config)
        if not is_valid:
            raise ConfigurationError(
                "Cannot save invalid configuration",
                details={"file": str(path), "errors": errors},
            )

        try:
            # Determine format
            if format is None:
                format = path.suffix.lstrip(".")

            # Create parent directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Save based on format
            if format == "toml":
                config.to_toml_file(path)
            elif format == "json":
                config.to_json_file(path)
            elif format == "ini":
                config.to_ini_file(path)
            else:
                raise ConfigurationError(
                    f"Unsupported format: {format}",
                    details={"file": str(path), "supported": ["toml", "json", "ini"]},
                )

            # Update cache
            cache_key = str(path.absolute())
            self._cache[cache_key] = config

            logger.info(f"Configuration saved successfully to: {path}")

        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(
                f"Failed to save configuration: {e}",
                details={"file": str(path), "error": str(e)},
            ) from e

    def validate_config(self, config: RUBEMConfig) -> tuple[bool, list[str]]:
        """Validate configuration.

        Args:
            config: Configuration to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors: list[str] = []

        try:
            # Validate simulation time
            if config.sim_time.duration_months < 1:
                errors.append("Simulation must be at least 1 month")

            # Validate directories exist
            if not config.directories.input.exists():
                errors.append(f"Input directory does not exist: {config.directories.input}")

            if not config.directories.output.exists():
                errors.append(f"Output directory does not exist: {config.directories.output}")

            # Validate raster files exist
            for field_name in ["dem", "clone", "soil"]:
                raster_path = getattr(config.raster_files, field_name)
                if not raster_path.exists():
                    errors.append(f"{field_name.upper()} file does not exist: {raster_path}")

            # Validate NDVI and land use directories
            if not config.raster_files.ndvi_dir.exists():
                errors.append(f"NDVI directory does not exist: {config.raster_files.ndvi_dir}")

            if not config.raster_files.landuse_dir.exists():
                errors.append(f"Land use directory does not exist: {config.raster_files.landuse_dir}")

            # Validate table files exist
            for field_name in ["climate", "landuse", "soil"]:
                table_path = getattr(config.table_files, field_name)
                if not table_path.exists():
                    errors.append(f"{field_name.title()} table does not exist: {table_path}")

            # Validate calibration parameters are in valid ranges
            if not (0.0 <= config.calibration.alpha <= 1.0):
                errors.append(f"Alpha must be between 0 and 1, got: {config.calibration.alpha}")

            if config.calibration.beta < 0.0:
                errors.append(f"Beta must be >= 0, got: {config.calibration.beta}")

            if not (0.0 <= config.calibration.lambda_factor <= 1.0):
                errors.append(f"Lambda factor must be between 0 and 1, got: {config.calibration.lambda_factor}")

            is_valid = len(errors) == 0

            if is_valid:
                logger.debug("Configuration validation passed")
            else:
                logger.warning(f"Configuration validation failed: {errors}")

            return is_valid, errors

        except Exception as e:
            logger.error(f"Configuration validation error: {e}", exc_info=True)
            errors.append(f"Validation error: {str(e)}")
            return False, errors

    def validate(self) -> tuple[bool, list[str]]:
        """Validate service state.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        # Service is stateless, always valid
        return True, []

    def create_default_config(
        self,
        input_dir: Path | None = None,
        output_dir: Path | None = None,
    ) -> RUBEMConfig:
        """Create a default configuration.

        Args:
            input_dir: Input directory path (defaults to home).
            output_dir: Output directory path (defaults to home).

        Returns:
            Default configuration instance.
        """
        from datetime import datetime

        from plugin.models import (
            CalibrationParameters,
            DirectoryConfig,
            RasterFiles,
            SimulationTime,
            TableFiles,
        )

        logger.info("Creating default configuration")

        if input_dir is None:
            input_dir = Path.home()
        if output_dir is None:
            output_dir = Path.home()

        config = RUBEMConfig(
            sim_time=SimulationTime(
                start=datetime.now().replace(day=1),
                end=datetime.now().replace(day=1, month=12),
            ),
            directories=DirectoryConfig(
                input=input_dir,
                output=output_dir,
            ),
            raster_files=RasterFiles(
                dem=input_dir / "dem.tif",
                clone=input_dir / "clone.map",
                ndvi_dir=input_dir / "ndvi",
                landuse_dir=input_dir / "landuse",
                soil=input_dir / "soil.tif",
            ),
            table_files=TableFiles(
                climate=input_dir / "climate.csv",
                landuse=input_dir / "landuse_params.csv",
                soil=input_dir / "soil_params.csv",
            ),
            calibration=CalibrationParameters(
                alpha=0.5,
                beta=1.5,
                lambda_factor=0.3,
                kc=1.0,
                field_capacity=0.35,
                wilting_point=0.15,
            ),
        )

        logger.info("Default configuration created")
        return config

    def convert_format(
        self,
        source_path: Path | str,
        target_path: Path | str,
    ) -> None:
        """Convert configuration file between formats.

        Args:
            source_path: Source configuration file.
            target_path: Target configuration file path (format inferred from extension).

        Raises:
            ConfigurationError: If conversion fails.
        """
        logger.info(f"Converting configuration: {source_path} -> {target_path}")

        try:
            # Load from source
            config = self.load_from_file(source_path)

            # Save to target
            self.save_to_file(config, target_path)

            logger.info("Configuration converted successfully")

        except Exception as e:
            raise ConfigurationError(
                f"Failed to convert configuration: {e}",
                details={
                    "source": str(source_path),
                    "target": str(target_path),
                    "error": str(e),
                },
            ) from e

    def clear_cache(self) -> None:
        """Clear configuration cache."""
        logger.debug("Clearing configuration cache")
        self._cache.clear()

    def cleanup(self) -> None:
        """Cleanup service resources."""
        self.clear_cache()
        super().cleanup()
