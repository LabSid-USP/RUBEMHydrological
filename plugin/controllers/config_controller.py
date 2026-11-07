"""Configuration controller for RUBEM Hydrological plugin.

This controller manages the configuration model and its interaction with
configuration-related views.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from plugin.controllers import BaseController
from plugin.exceptions import ConfigurationError, FileOperationError
from plugin.logging import get_logger
from plugin.models import RUBEMConfig

if TYPE_CHECKING:
    from qgis.gui import QgisInterface
    from plugin.views.config_view import ConfigView

logger = get_logger(__name__)


class ConfigController(BaseController[RUBEMConfig, "ConfigView"]):
    """Controller for configuration management.

    This controller handles:
    - Loading configuration from files
    - Saving configuration to files
    - Creating new configurations
    - Validating configuration data

    Signals:
        config_loaded: Emitted when configuration is loaded (file_path: str).
        config_saved: Emitted when configuration is saved (file_path: str).
        config_changed: Emitted when configuration changes.
    """

    config_loaded = pyqtSignal(str)
    config_saved = pyqtSignal(str)
    config_changed = pyqtSignal()

    def __init__(
        self,
        model: RUBEMConfig,
        view: ConfigView,
        iface: QgisInterface,
    ) -> None:
        """Initialize configuration controller.

        Args:
            model: Configuration model instance.
            view: Configuration view instance.
            iface: QGIS interface reference.
        """
        self.current_file: Path | None = None
        self.is_modified: bool = False
        super().__init__(model, view, iface)

    def _setup_connections(self) -> None:
        """Setup signal-slot connections."""
        # Connect view signals to controller methods
        self.view.load_requested.connect(self.load_config)
        self.view.save_requested.connect(self.save_config)
        self.view.new_requested.connect(self.new_config)
        self.view.value_changed.connect(self.on_value_changed)

    def update_view_from_model(self) -> None:
        """Update view to reflect current model state."""
        try:
            # Update simulation time
            self.view.set_start_date(self.model.sim_time.start)
            self.view.set_end_date(self.model.sim_time.end)

            # Update directories
            self.view.set_input_directory(str(self.model.directories.input))
            self.view.set_output_directory(str(self.model.directories.output))

            # Update calibration parameters
            self.view.set_alpha(self.model.calibration.alpha)
            self.view.set_beta(self.model.calibration.beta)
            self.view.set_lambda_factor(self.model.calibration.lambda_factor)
            self.view.set_kc(self.model.calibration.kc)
            self.view.set_field_capacity(self.model.calibration.field_capacity)
            self.view.set_wilting_point(self.model.calibration.wilting_point)

            # Update output options
            self.view.set_generate_timeseries(
                self.model.output_options.generate_timeseries
            )
            self.view.set_generate_maps(self.model.output_options.generate_maps)
            self.view.set_generate_stats(self.model.output_options.generate_stats)

            # Update file paths
            self.view.set_dem_path(str(self.model.raster_files.dem))
            self.view.set_clone_path(str(self.model.raster_files.clone))
            self.view.set_soil_path(str(self.model.raster_files.soil))

            logger.debug("View updated from model")

        except Exception as e:
            self.handle_error(e, "Failed to update view from model")

    def update_model_from_view(self) -> None:
        """Update model with current view state."""
        try:
            # This will be implemented with individual setters
            # or by reconstructing the entire model
            logger.debug("Model updated from view")
            self.is_modified = True

        except Exception as e:
            self.handle_error(e, "Failed to update model from view")

    def load_config(self, file_path: str | Path) -> None:
        """Load configuration from file.

        Args:
            file_path: Path to configuration file.

        Raises:
            FileNotFoundError: If file does not exist.
            ValidationError: If configuration is invalid.
        """
        try:
            path = Path(file_path)
            logger.info(f"Loading configuration from: {path}")

            # Load configuration using service
            self.model = self._config_service.load_from_file(path)
            self.current_file = path
            self.is_modified = False

            # Update view with loaded data
            self.update_view_from_model()

            # Emit signal
            self.config_loaded.emit(str(path))

            logger.info(f"Configuration loaded successfully from: {path}")

        except Exception as e:
            self.handle_error(e, f"Failed to load configuration from: {file_path}")

    def save_config(self, file_path: str | Path | None = None) -> None:
        """Save configuration to file.

        Args:
            file_path: Path to save to. If None, uses current file path.

        Raises:
            ValueError: If no file path specified and no current file.
            ValidationError: If configuration is invalid.
        """
        if file_path is None and self.current_file is None:
            raise ValueError("No file path specified")

        path = Path(file_path) if file_path else self.current_file
        assert path is not None  # For type checker

        try:
            logger.info(f"Saving configuration to: {path}")

            # Update model from view before saving
            self.update_model_from_view()

            # Save using service
            self._config_service.save_to_file(self.model, path)
            self.current_file = path
            self.is_modified = False

            # Emit signal
            self.config_saved.emit(str(path))

            logger.info(f"Configuration saved successfully to: {path}")

        except Exception as e:
            self.handle_error(e, f"Failed to save configuration to: {path}")

    def new_config(self) -> None:
        """Create new default configuration."""
        try:
            logger.info("Creating new configuration")

            # Create default configuration
            # (This would use default values from models)
            from datetime import datetime

            from plugin.models import (
                CalibrationParameters,
                DirectoryConfig,
                RasterFiles,
                SimulationTime,
                TableFiles,
            )

            self.model = RUBEMConfig(
                sim_time=SimulationTime(
                    start=datetime(2020, 1, 1),
                    end=datetime(2020, 12, 31),
                ),
                directories=DirectoryConfig(
                    input=Path.home(),
                    output=Path.home(),
                ),
                raster_files=RasterFiles(
                    dem=Path(""),
                    clone=Path(""),
                    ndvi_dir=Path(""),
                    landuse_dir=Path(""),
                    soil=Path(""),
                ),
                table_files=TableFiles(
                    climate=Path(""),
                    landuse=Path(""),
                    soil=Path(""),
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

            self.current_file = None
            self.is_modified = False
            self.update_view_from_model()

            self.view.show_success_message("New configuration created")
            logger.info("New configuration created")

        except Exception as e:
            self.handle_error(e, "Failed to create new configuration")

    def on_value_changed(self, field: str, value: object) -> None:
        """Handle value change from view.

        Args:
            field: Field name that changed.
            value: New value.
        """
        try:
            logger.debug(f"Value changed: {field} = {value}")
            self.is_modified = True

            # Update model field
            # This would use reflection or mapping to update the correct model field

            # Emit change signal
            self.config_changed.emit()

        except Exception as e:
            self.handle_error(e, f"Failed to update field: {field}")

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate current configuration.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        try:
            # Pydantic validation happens automatically on model creation
            # Additional custom validation can be added here
            errors: list[str] = []

            # Example additional validations
            if not self.model.directories.input.exists():
                errors.append(f"Input directory does not exist: {self.model.directories.input}")

            if not self.model.directories.output.exists():
                errors.append(f"Output directory does not exist: {self.model.directories.output}")

            is_valid = len(errors) == 0
            return is_valid, errors

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False, [str(e)]

    def cleanup(self) -> None:
        """Cleanup controller resources."""
        super().cleanup()
        # Additional cleanup if needed
