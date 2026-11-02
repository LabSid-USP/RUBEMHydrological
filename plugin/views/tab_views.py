"""Tab-specific views for RUBEM Hydrological plugin.

This module provides view classes for each tab in the main dialog.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from qgis.PyQt.QtCore import pyqtSignal
except ImportError:
    from PyQt5.QtCore import pyqtSignal

from plugin.logging import get_logger
from plugin.views import BaseView

logger = get_logger(__name__)


class ClimateView(BaseView):
    """View for climate data configuration.

    Signals:
        file_selected: Emitted when a climate file is selected (file_type: str, path: str).
        series_loaded: Emitted when time series needs to be loaded (path: str).
    """

    file_selected = pyqtSignal(str, str)
    series_loaded = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize climate view."""
        super().__init__()

    def setup_ui(self) -> None:
        """Setup the user interface."""
        pass

    def clear(self) -> None:
        """Clear all climate data."""
        logger.debug("Clearing climate view")

    def set_precipitation_file(self, path: str) -> None:
        """Set precipitation file path.

        Args:
            path: File path.
        """
        logger.debug(f"Setting precipitation file: {path}")

    def set_temperature_file(self, path: str) -> None:
        """Set temperature file path.

        Args:
            path: File path.
        """
        logger.debug(f"Setting temperature file: {path}")

    def set_evapotranspiration_file(self, path: str) -> None:
        """Set evapotranspiration file path.

        Args:
            path: File path.
        """
        logger.debug(f"Setting evapotranspiration file: {path}")

    def get_precipitation_file(self) -> str:
        """Get precipitation file path.

        Returns:
            File path.
        """
        return ""

    def get_temperature_file(self) -> str:
        """Get temperature file path.

        Returns:
            File path.
        """
        return ""

    def get_evapotranspiration_file(self) -> str:
        """Get evapotranspiration file path.

        Returns:
            File path.
        """
        return ""


class LandUseView(BaseView):
    """View for land use data configuration.

    Signals:
        map_selected: Emitted when land use map is selected (year: int, path: str).
        preview_requested: Emitted when map preview is requested (path: str).
    """

    map_selected = pyqtSignal(int, str)
    preview_requested = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize land use view."""
        super().__init__()

    def setup_ui(self) -> None:
        """Setup the user interface."""
        pass

    def clear(self) -> None:
        """Clear all land use data."""
        logger.debug("Clearing land use view")

    def add_land_use_map(self, year: int, path: str) -> None:
        """Add land use map to view.

        Args:
            year: Year of the map.
            path: File path.
        """
        logger.debug(f"Adding land use map for year {year}: {path}")

    def remove_land_use_map(self, year: int) -> None:
        """Remove land use map from view.

        Args:
            year: Year of the map to remove.
        """
        logger.debug(f"Removing land use map for year {year}")

    def get_land_use_maps(self) -> dict[int, str]:
        """Get all land use maps.

        Returns:
            Dictionary mapping years to file paths.
        """
        return {}

    def set_land_use_table(self, path: str) -> None:
        """Set land use parameter table path.

        Args:
            path: File path.
        """
        logger.debug(f"Setting land use table: {path}")

    def get_land_use_table(self) -> str:
        """Get land use parameter table path.

        Returns:
            File path.
        """
        return ""


class SoilView(BaseView):
    """View for soil data configuration.

    Signals:
        layer_selected: Emitted when soil layer is selected (path: str).
        table_selected: Emitted when soil table is selected (path: str).
    """

    layer_selected = pyqtSignal(str)
    table_selected = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize soil view."""
        super().__init__()

    def setup_ui(self) -> None:
        """Setup the user interface."""
        pass

    def clear(self) -> None:
        """Clear all soil data."""
        logger.debug("Clearing soil view")

    def set_soil_map(self, path: str) -> None:
        """Set soil map path.

        Args:
            path: File path.
        """
        logger.debug(f"Setting soil map: {path}")

    def set_soil_table(self, path: str) -> None:
        """Set soil parameter table path.

        Args:
            path: File path.
        """
        logger.debug(f"Setting soil table: {path}")

    def get_soil_map(self) -> str:
        """Get soil map path.

        Returns:
            File path.
        """
        return ""

    def get_soil_table(self) -> str:
        """Get soil parameter table path.

        Returns:
            File path.
        """
        return ""


class ParametersView(BaseView):
    """View for model parameters configuration.

    Signals:
        parameter_changed: Emitted when parameter changes (name: str, value: float).
        reset_requested: Emitted when reset to defaults is requested.
    """

    parameter_changed = pyqtSignal(str, float)
    reset_requested = pyqtSignal()

    def __init__(self) -> None:
        """Initialize parameters view."""
        super().__init__()

    def setup_ui(self) -> None:
        """Setup the user interface."""
        pass

    def clear(self) -> None:
        """Clear all parameters."""
        logger.debug("Clearing parameters view")

    def set_parameter(self, name: str, value: float) -> None:
        """Set parameter value.

        Args:
            name: Parameter name.
            value: Parameter value.
        """
        logger.debug(f"Setting parameter {name}: {value}")

    def get_parameter(self, name: str) -> float | None:
        """Get parameter value.

        Args:
            name: Parameter name.

        Returns:
            Parameter value or None if not found.
        """
        return None

    def get_all_parameters(self) -> dict[str, float]:
        """Get all parameters.

        Returns:
            Dictionary mapping parameter names to values.
        """
        return {}

    def set_defaults(self) -> None:
        """Set all parameters to default values."""
        logger.debug("Setting default parameters")


class ResultsView(BaseView):
    """View for model results visualization.

    Signals:
        plot_requested: Emitted when plot is requested (variable: str).
        export_requested: Emitted when export is requested (format: str).
    """

    plot_requested = pyqtSignal(str)
    export_requested = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize results view."""
        super().__init__()

    def setup_ui(self) -> None:
        """Setup the user interface."""
        pass

    def clear(self) -> None:
        """Clear all results."""
        logger.debug("Clearing results view")

    def show_timeseries(self, variable: str, data: dict) -> None:
        """Show time series plot.

        Args:
            variable: Variable name.
            data: Time series data.
        """
        logger.debug(f"Showing timeseries for {variable}")

    def show_map(self, variable: str, path: str) -> None:
        """Show result map.

        Args:
            variable: Variable name.
            path: Raster file path.
        """
        logger.debug(f"Showing map for {variable}: {path}")

    def show_statistics(self, stats: dict) -> None:
        """Show statistics table.

        Args:
            stats: Statistics dictionary.
        """
        logger.debug("Showing statistics")


class RunView(BaseView):
    """View for model execution.

    Signals:
        run_requested: Emitted when run is requested.
        cancel_requested: Emitted when cancellation is requested.
    """

    run_requested = pyqtSignal()
    cancel_requested = pyqtSignal()

    def __init__(self) -> None:
        """Initialize run view."""
        super().__init__()

    def setup_ui(self) -> None:
        """Setup the user interface."""
        pass

    def clear(self) -> None:
        """Clear run view."""
        logger.debug("Clearing run view")

    def set_progress(self, value: int) -> None:
        """Set progress bar value.

        Args:
            value: Progress percentage (0-100).
        """
        logger.debug(f"Setting progress: {value}%")

    def set_status(self, message: str) -> None:
        """Set status message.

        Args:
            message: Status message.
        """
        logger.debug(f"Status: {message}")

    def append_log(self, message: str) -> None:
        """Append message to execution log.

        Args:
            message: Log message.
        """
        logger.debug(f"Log: {message}")

    def set_running(self, running: bool) -> None:
        """Set running state.

        Args:
            running: Whether model is running.
        """
        logger.debug(f"Setting running state: {running}")

    def clear_log(self) -> None:
        """Clear execution log."""
        logger.debug("Clearing execution log")
