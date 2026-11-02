"""Main controller for RUBEM Hydrological plugin.

This module provides the main controller that orchestrates all tab controllers
and manages the overall application state.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

try:
    from qgis.core import QgsApplication
    from qgis.gui import QgisInterface
except ImportError:
    QgsApplication = None  # type: ignore
    QgisInterface = None  # type: ignore

from plugin.controllers.config_controller import ConfigController
from plugin.controllers.tab_controllers import (
    ClimateController,
    LandUseController,
    ParametersController,
    ResultsController,
    RunController,
    SoilController,
)
from plugin.exceptions import PluginInitializationError
from plugin.logging import get_logger
from plugin.models import RUBEMConfig
from plugin.services.config_service import ConfigService

if TYPE_CHECKING:
    from plugin.views.config_view import ConfigView
    from plugin.views.tab_views import (
        ClimateView,
        LandUseView,
        ParametersView,
        ResultsView,
        RunView,
        SoilView,
    )

logger = get_logger(__name__)


class MainController:
    """Main controller orchestrating all plugin functionality.

    This controller:
    - Manages the lifecycle of all sub-controllers
    - Coordinates communication between controllers
    - Manages configuration loading/saving
    - Handles global plugin state
    """

    def __init__(
        self,
        iface: QgisInterface | None,
        config_view: ConfigView,
        climate_view: ClimateView,
        landuse_view: LandUseView,
        soil_view: SoilView,
        parameters_view: ParametersView,
        results_view: ResultsView,
        run_view: RunView,
    ) -> None:
        """Initialize main controller.

        Args:
            iface: QGIS interface.
            config_view: Configuration view.
            climate_view: Climate data view.
            landuse_view: Land use data view.
            soil_view: Soil data view.
            parameters_view: Parameters view.
            results_view: Results view.
            run_view: Model execution view.

        Raises:
            PluginInitializationError: If initialization fails.
        """
        try:
            self.iface = iface
            self._current_config: RUBEMConfig | None = None
            self._current_file: Path | None = None
            self._is_modified = False

            # Create configuration service
            self._config_service = ConfigService()

            # Initialize with default configuration
            self._current_config = self._config_service.create_default_config()

            # Initialize sub-controllers
            self._config_controller = ConfigController(
                model=self._current_config,
                view=config_view,
                iface=iface,
            )

            self._climate_controller = ClimateController(
                model=self._current_config,
                view=climate_view,
            )

            self._landuse_controller = LandUseController(
                model=self._current_config,
                view=landuse_view,
            )

            self._soil_controller = SoilController(
                model=self._current_config,
                view=soil_view,
            )

            self._parameters_controller = ParametersController(
                model=self._current_config,
                view=parameters_view,
            )

            self._results_controller = ResultsController(
                model=self._current_config,
                view=results_view,
            )

            self._run_controller = RunController(
                model=self._current_config,
                view=run_view,
            )

            # Setup inter-controller connections
            self._setup_connections()

            logger.info("Main controller initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize main controller: {e}")
            raise PluginInitializationError(
                "Failed to initialize main controller",
                details={"error": str(e)},
            ) from e

    def _setup_connections(self) -> None:
        """Setup connections between controllers."""
        # Config controller signals
        self._config_controller.config_loaded.connect(self._on_config_loaded)
        self._config_controller.config_saved.connect(self._on_config_saved)
        self._config_controller.config_changed.connect(self._on_config_changed)

        logger.debug("Main controller connections established")

    @property
    def current_config(self) -> RUBEMConfig | None:
        """Get current configuration.

        Returns:
            Current configuration or None.
        """
        return self._current_config

    @property
    def current_file(self) -> Path | None:
        """Get current configuration file path.

        Returns:
            Current file path or None.
        """
        return self._current_file

    @property
    def is_modified(self) -> bool:
        """Check if configuration has been modified.

        Returns:
            True if modified, False otherwise.
        """
        return self._is_modified

    def new_project(self) -> None:
        """Create a new project with default configuration."""
        try:
            logger.info("Creating new project")

            # Create default configuration
            self._current_config = self._config_service.create_default_config()
            self._current_file = None
            self._is_modified = False

            # Update all controllers with new config
            self._update_all_controllers()

            logger.info("New project created successfully")

        except Exception as e:
            logger.error(f"Failed to create new project: {e}")
            raise

    def load_project(self, file_path: str | Path) -> None:
        """Load project from file.

        Args:
            file_path: Path to configuration file.

        Raises:
            FileNotFoundError: If file does not exist.
            ValidationError: If configuration is invalid.
        """
        try:
            path = Path(file_path)
            logger.info(f"Loading project from: {path}")

            # Load configuration
            self._current_config = self._config_service.load_from_file(path)
            self._current_file = path
            self._is_modified = False

            # Update all controllers
            self._update_all_controllers()

            logger.info(f"Project loaded successfully from: {path}")

        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            raise

    def save_project(self, file_path: str | Path | None = None) -> None:
        """Save project to file.

        Args:
            file_path: Path to save to. If None, uses current file path.

        Raises:
            ValueError: If no file path specified and no current file.
            ValidationError: If configuration is invalid.
        """
        if file_path is None and self._current_file is None:
            raise ValueError("No file path specified")

        path = Path(file_path) if file_path else self._current_file
        assert path is not None  # For type checker

        try:
            logger.info(f"Saving project to: {path}")

            if self._current_config is None:
                raise ValueError("No configuration to save")

            # Update model from views before saving
            self._update_model_from_views()

            # Save configuration
            self._config_service.save_to_file(self._current_config, path)
            self._current_file = path
            self._is_modified = False

            logger.info(f"Project saved successfully to: {path}")

        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            raise

    def validate_configuration(self) -> tuple[bool, list[str]]:
        """Validate current configuration.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        if self._current_config is None:
            return False, ["No configuration loaded"]

        try:
            is_valid = self._config_service.validate_config(self._current_config)
            return is_valid, []

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False, [str(e)]

    def run_model(self) -> None:
        """Run the RUBEM model.

        This delegates to the run controller which handles execution.
        """
        try:
            # Validate configuration first
            is_valid, errors = self.validate_configuration()
            if not is_valid:
                error_msg = "\n".join(errors)
                raise ValueError(f"Configuration validation failed:\n{error_msg}")

            # Trigger run controller
            self._run_controller._on_run_requested()

        except Exception as e:
            logger.error(f"Failed to run model: {e}")
            raise

    def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            logger.info("Cleaning up main controller")

            # Cleanup service
            if hasattr(self, "_config_service"):
                self._config_service.cleanup()

            logger.info("Main controller cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def _update_all_controllers(self) -> None:
        """Update all controllers with current configuration."""
        if self._current_config is None:
            return

        logger.debug("Updating all controllers with current configuration")

        # Update each controller's model
        self._config_controller.model = self._current_config
        self._climate_controller.model = self._current_config
        self._landuse_controller.model = self._current_config
        self._soil_controller.model = self._current_config
        self._parameters_controller.model = self._current_config
        self._results_controller.model = self._current_config
        self._run_controller.model = self._current_config

        # Trigger view updates
        self._config_controller.update_view_from_model()
        self._climate_controller.update_view_from_model()
        self._landuse_controller.update_view_from_model()
        self._soil_controller.update_view_from_model()
        self._parameters_controller.update_view_from_model()
        self._results_controller.update_view_from_model()
        self._run_controller.update_view_from_model()

    def _update_model_from_views(self) -> None:
        """Update model from all views."""
        logger.debug("Updating model from all views")

        # Update model from each controller's view
        self._config_controller.update_model_from_view()
        self._climate_controller.update_model_from_view()
        self._landuse_controller.update_model_from_view()
        self._soil_controller.update_model_from_view()
        self._parameters_controller.update_model_from_view()
        # Results and run are read-only from model perspective

    def _on_config_loaded(self, file_path: str) -> None:
        """Handle configuration loaded event.

        Args:
            file_path: Path to loaded file.
        """
        logger.info(f"Configuration loaded: {file_path}")
        self._current_file = Path(file_path)
        self._is_modified = False

    def _on_config_saved(self, file_path: str) -> None:
        """Handle configuration saved event.

        Args:
            file_path: Path to saved file.
        """
        logger.info(f"Configuration saved: {file_path}")
        self._current_file = Path(file_path)
        self._is_modified = False

    def _on_config_changed(self) -> None:
        """Handle configuration changed event."""
        logger.debug("Configuration changed")
        self._is_modified = True
