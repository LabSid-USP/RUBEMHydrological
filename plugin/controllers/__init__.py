"""Base controller class for RUBEM Hydrological plugin.

This module defines the abstract base controller following MVC pattern.
All specific controllers should inherit from this class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from plugin.logging import get_logger

if TYPE_CHECKING:
    from qgis.gui import QgisInterface

logger = get_logger(__name__)

# Type variables for generic controller
TModel = TypeVar("TModel")
TView = TypeVar("TView")


class BaseController(ABC, Generic[TModel, TView]):
    """Abstract base controller following MVC pattern.

    Controllers mediate between models and views, handling user interactions
    and updating the UI based on model changes.

    Type Parameters:
        TModel: Type of the model managed by this controller.
        TView: Type of the view managed by this controller.

    Attributes:
        model: The model instance managed by this controller.
        view: The view instance managed by this controller.
        iface: Reference to QGIS interface.
    """

    def __init__(
        self,
        model: TModel,
        view: TView,
        iface: QgisInterface | None = None,
    ) -> None:
        """Initialize the controller.

        Args:
            model: The data model.
            view: The view instance.
            iface: QGIS interface (optional).
        """
        self.model = model
        self.view = view
        self.iface = iface
        self._setup_connections()
        logger.debug(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def _setup_connections(self) -> None:
        """Setup signal-slot connections between view and model.

        This method should connect all Qt signals from the view to
        appropriate controller methods, which will then update the model.
        """
        pass

    @abstractmethod
    def update_view_from_model(self) -> None:
        """Update view to reflect current model state.

        This method should read values from the model and update
        all relevant view widgets.
        """
        pass

    @abstractmethod
    def update_model_from_view(self) -> None:
        """Update model with current view state.

        This method should read values from view widgets and update
        the model accordingly.
        """
        pass

    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle errors consistently across controllers.

        Args:
            error: The exception that occurred.
            context: Additional context about where error occurred.
        """
        from plugin.exceptions import RUBEMException

        logger.error(f"Error in {self.__class__.__name__}: {error}", exc_info=True)

        if isinstance(error, RUBEMException):
            error_msg = f"{error.message}\n\nDetails: {error.details}"
        else:
            error_msg = str(error)

        if context:
            error_msg = f"{context}\n\n{error_msg}"

        # Show error to user via QGIS message bar or dialog
        self._show_error_message(error_msg)

    def _show_error_message(self, message: str) -> None:
        """Show error message to user.

        Args:
            message: Error message to display.
        """
        try:
            from qgis.PyQt.QtWidgets import QMessageBox

            QMessageBox.critical(
                None,  # or self.view if it's a QWidget
                "RUBEM Hydrological Error",
                message,
            )
        except Exception as e:
            logger.error(f"Failed to show error message: {e}")

    def cleanup(self) -> None:
        """Cleanup controller resources.

        Override this method to perform cleanup tasks when controller
        is no longer needed.
        """
        logger.debug(f"{self.__class__.__name__} cleanup")
