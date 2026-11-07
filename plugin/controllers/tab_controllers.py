"""Additional controllers for RUBEM Hydrological plugin tabs.

This module provides controller classes for specific functionality areas.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from plugin.controllers import BaseController
from plugin.logging import get_logger

if TYPE_CHECKING:
    from plugin.models import RUBEMConfig
    from plugin.views.tab_views import (
        ClimateView,
        LandUseView,
        ParametersView,
        ResultsView,
        RunView,
        SoilView,
    )

logger = get_logger(__name__)


class ClimateController(BaseController["RUBEMConfig", "ClimateView"]):
    """Controller for climate data management."""

    def __init__(self, model: RUBEMConfig, view: ClimateView) -> None:
        """Initialize climate controller.

        Args:
            model: Configuration model.
            view: Climate view.
        """
        super().__init__(model, view)

    def _setup_connections(self) -> None:
        """Setup signal/slot connections."""
        self.view.file_selected.connect(self._on_file_selected)
        self.view.series_loaded.connect(self._on_series_loaded)
        logger.debug("Climate controller connections established")

    def update_view_from_model(self) -> None:
        """Update view with model data."""
        # Update precipitation file
        if hasattr(self.model, "precipitation_file"):
            self.view.set_precipitation_file(self.model.precipitation_file)

        # Update temperature file
        if hasattr(self.model, "temperature_file"):
            self.view.set_temperature_file(self.model.temperature_file)

        # Update evapotranspiration file
        if hasattr(self.model, "evapotranspiration_file"):
            self.view.set_evapotranspiration_file(self.model.evapotranspiration_file)

        logger.debug("Climate view updated from model")

    def update_model_from_view(self) -> None:
        """Update model with view data."""
        # This would update the model with view values
        # For now, files are set individually via signals
        pass

    def _on_file_selected(self, file_type: str, path: str) -> None:
        """Handle file selection.

        Args:
            file_type: Type of climate file.
            path: File path.
        """
        try:
            logger.info(f"Climate file selected: {file_type} = {path}")
            # Validate file exists and is readable
            # Update model accordingly
        except Exception as e:
            self.handle_error(e, f"Failed to load climate file: {file_type}")

    def _on_series_loaded(self, path: str) -> None:
        """Handle time series loading.

        Args:
            path: Time series file path.
        """
        try:
            logger.info(f"Loading time series from: {path}")
            # Load and validate time series data
        except Exception as e:
            self.handle_error(e, "Failed to load time series")


class LandUseController(BaseController["RUBEMConfig", "LandUseView"]):
    """Controller for land use data management."""

    def __init__(self, model: RUBEMConfig, view: LandUseView) -> None:
        """Initialize land use controller.

        Args:
            model: Configuration model.
            view: Land use view.
        """
        super().__init__(model, view)

    def _setup_connections(self) -> None:
        """Setup signal/slot connections."""
        self.view.map_selected.connect(self._on_map_selected)
        self.view.preview_requested.connect(self._on_preview_requested)
        logger.debug("Land use controller connections established")

    def update_view_from_model(self) -> None:
        """Update view with model data."""
        # Clear existing maps
        self.view.clear()

        # Add land use maps from model
        # This would iterate through configured maps
        logger.debug("Land use view updated from model")

    def update_model_from_view(self) -> None:
        """Update model with view data."""
        # Get maps from view and update model
        maps = self.view.get_land_use_maps()
        # Update model with maps
        logger.debug("Land use model updated from view")

    def _on_map_selected(self, year: int, path: str) -> None:
        """Handle land use map selection.

        Args:
            year: Map year.
            path: File path.
        """
        try:
            logger.info(f"Land use map selected for {year}: {path}")
            # Validate raster file
            # Add to model
            self.view.add_land_use_map(year, path)
        except Exception as e:
            self.handle_error(e, f"Failed to load land use map for year {year}")

    def _on_preview_requested(self, path: str) -> None:
        """Handle map preview request.

        Args:
            path: Raster file path.
        """
        try:
            logger.info(f"Preview requested for: {path}")
            # Load and display raster preview
        except Exception as e:
            self.handle_error(e, "Failed to preview map")


class SoilController(BaseController["RUBEMConfig", "SoilView"]):
    """Controller for soil data management."""

    def __init__(self, model: RUBEMConfig, view: SoilView) -> None:
        """Initialize soil controller.

        Args:
            model: Configuration model.
            view: Soil view.
        """
        super().__init__(model, view)

    def _setup_connections(self) -> None:
        """Setup signal/slot connections."""
        self.view.layer_selected.connect(self._on_layer_selected)
        self.view.table_selected.connect(self._on_table_selected)
        logger.debug("Soil controller connections established")

    def update_view_from_model(self) -> None:
        """Update view with model data."""
        # Update soil map
        if hasattr(self.model, "soil_map"):
            self.view.set_soil_map(self.model.soil_map)

        # Update soil table
        if hasattr(self.model, "soil_table"):
            self.view.set_soil_table(self.model.soil_table)

        logger.debug("Soil view updated from model")

    def update_model_from_view(self) -> None:
        """Update model with view data."""
        # Get values from view and update model
        pass

    def _on_layer_selected(self, path: str) -> None:
        """Handle soil layer selection.

        Args:
            path: Layer file path.
        """
        try:
            logger.info(f"Soil layer selected: {path}")
            # Validate layer
            self.view.set_soil_map(path)
        except Exception as e:
            self.handle_error(e, "Failed to load soil layer")

    def _on_table_selected(self, path: str) -> None:
        """Handle soil table selection.

        Args:
            path: Table file path.
        """
        try:
            logger.info(f"Soil table selected: {path}")
            # Validate table
            self.view.set_soil_table(path)
        except Exception as e:
            self.handle_error(e, "Failed to load soil table")


class ParametersController(BaseController["RUBEMConfig", "ParametersView"]):
    """Controller for model parameters management."""

    def __init__(self, model: RUBEMConfig, view: ParametersView) -> None:
        """Initialize parameters controller.

        Args:
            model: Configuration model.
            view: Parameters view.
        """
        super().__init__(model, view)

    def _setup_connections(self) -> None:
        """Setup signal/slot connections."""
        self.view.parameter_changed.connect(self._on_parameter_changed)
        self.view.reset_requested.connect(self._on_reset_requested)
        logger.debug("Parameters controller connections established")

    def update_view_from_model(self) -> None:
        """Update view with model data."""
        # Update all parameters from calibration section
        if hasattr(self.model, "calibration"):
            calibration = self.model.calibration
            for param_name in dir(calibration):
                if not param_name.startswith("_"):
                    value = getattr(calibration, param_name)
                    if isinstance(value, (int, float)):
                        self.view.set_parameter(param_name, float(value))

        logger.debug("Parameters view updated from model")

    def update_model_from_view(self) -> None:
        """Update model with view data."""
        # Get all parameters from view
        params = self.view.get_all_parameters()

        # Update calibration model
        if hasattr(self.model, "calibration"):
            for name, value in params.items():
                if hasattr(self.model.calibration, name):
                    setattr(self.model.calibration, name, value)

        logger.debug("Parameters model updated from view")

    def _on_parameter_changed(self, name: str, value: float) -> None:
        """Handle parameter change.

        Args:
            name: Parameter name.
            value: New value.
        """
        try:
            logger.info(f"Parameter changed: {name} = {value}")
            # Validate value range
            # Update model
            if hasattr(self.model, "calibration") and hasattr(
                self.model.calibration, name
            ):
                setattr(self.model.calibration, name, value)
        except Exception as e:
            self.handle_error(e, f"Failed to update parameter: {name}")

    def _on_reset_requested(self) -> None:
        """Handle reset to defaults request."""
        try:
            logger.info("Resetting parameters to defaults")
            # Reset model to defaults
            # Update view
            self.update_view_from_model()
        except Exception as e:
            self.handle_error(e, "Failed to reset parameters")


class ResultsController(BaseController["RUBEMConfig", "ResultsView"]):
    """Controller for results visualization."""

    def __init__(self, model: RUBEMConfig, view: ResultsView) -> None:
        """Initialize results controller.

        Args:
            model: Configuration model.
            view: Results view.
        """
        super().__init__(model, view)

    def _setup_connections(self) -> None:
        """Setup signal/slot connections."""
        self.view.plot_requested.connect(self._on_plot_requested)
        self.view.export_requested.connect(self._on_export_requested)
        logger.debug("Results controller connections established")

    def update_view_from_model(self) -> None:
        """Update view with model data."""
        # This controller primarily displays computed results
        # Model updates trigger result loading
        pass

    def update_model_from_view(self) -> None:
        """Update model with view data."""
        # Results are read-only from model perspective
        pass

    def _on_plot_requested(self, variable: str) -> None:
        """Handle plot request.

        Args:
            variable: Variable to plot.
        """
        try:
            logger.info(f"Plot requested for: {variable}")
            # Load result data
            # Generate plot
            # Display in view
        except Exception as e:
            self.handle_error(e, f"Failed to plot variable: {variable}")

    def _on_export_requested(self, format: str) -> None:
        """Handle export request.

        Args:
            format: Export format.
        """
        try:
            logger.info(f"Export requested in format: {format}")
            # Export results
        except Exception as e:
            self.handle_error(e, "Failed to export results")


class RunController(BaseController["RUBEMConfig", "RunView"]):
    """Controller for model execution."""

    def __init__(self, model: RUBEMConfig, view: RunView) -> None:
        """Initialize run controller.

        Args:
            model: Configuration model.
            view: Run view.
        """
        super().__init__(model, view)
        self._is_running = False

    def _setup_connections(self) -> None:
        """Setup signal/slot connections."""
        self.view.run_requested.connect(self._on_run_requested)
        self.view.cancel_requested.connect(self._on_cancel_requested)
        logger.debug("Run controller connections established")

    def update_view_from_model(self) -> None:
        """Update view with model data."""
        # Update run configuration display
        pass

    def update_model_from_view(self) -> None:
        """Update model with view data."""
        # Model is not modified during execution
        pass

    def _on_run_requested(self) -> None:
        """Handle run request."""
        if self._is_running:
            logger.warning("Model is already running")
            return

        try:
            logger.info("Starting model execution")
            self._is_running = True
            self.view.set_running(True)
            self.view.clear_log()
            self.view.set_progress(0)

            # Start model execution via worker
            # Worker will emit progress signals

        except Exception as e:
            self._is_running = False
            self.view.set_running(False)
            self.handle_error(e, "Failed to start model execution")

    def _on_cancel_requested(self) -> None:
        """Handle cancellation request."""
        if not self._is_running:
            logger.warning("No model is running")
            return

        try:
            logger.info("Cancelling model execution")
            # Cancel worker
            self._is_running = False
            self.view.set_running(False)

        except Exception as e:
            self.handle_error(e, "Failed to cancel execution")

    def on_progress(self, value: int, message: str) -> None:
        """Handle progress update.

        Args:
            value: Progress percentage.
            message: Progress message.
        """
        self.view.set_progress(value)
        self.view.set_status(message)
        self.view.append_log(message)

    def on_finished(self, success: bool, message: str) -> None:
        """Handle execution finished.

        Args:
            success: Whether execution succeeded.
            message: Completion message.
        """
        self._is_running = False
        self.view.set_running(False)
        self.view.set_progress(100 if success else 0)
        self.view.append_log(message)

        if success:
            self.view.show_success_message("Model execution completed successfully!")
        else:
            self.view.show_error_message(f"Model execution failed: {message}")
