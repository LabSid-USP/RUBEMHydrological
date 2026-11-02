"""Base view classes for RUBEM Hydrological plugin.

This module provides abstract base classes for views following MVC pattern.
Views handle UI presentation and emit signals for user interactions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

try:
    from qgis.PyQt.QtCore import pyqtSignal, QObject
    from qgis.PyQt.QtWidgets import QWidget
except ImportError:
    from PyQt5.QtCore import pyqtSignal, QObject
    from PyQt5.QtWidgets import QWidget

from plugin.logging import get_logger

logger = get_logger(__name__)


class BaseView(QObject, ABC):
    """Abstract base view for UI components.

    Views are responsible for:
    - Displaying data to the user
    - Capturing user input
    - Emitting signals for user actions
    - NOT containing business logic

    Views should be as passive as possible, with controllers handling
    all logic.

    Signals:
        value_changed: Emitted when a value changes (field: str, value: Any).
    """

    value_changed = pyqtSignal(str, object)

    def __init__(self) -> None:
        """Initialize the view."""
        super().__init__()
        logger.debug(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def setup_ui(self) -> None:
        """Setup the user interface.

        This method should initialize all UI components and layout.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all values in the view.

        This method should reset all input widgets to their default state.
        """
        pass

    def show_message(self, message: str, message_type: str = "info") -> None:
        """Show a message to the user.

        Args:
            message: Message to display.
            message_type: Type of message ('info', 'warning', 'error', 'success').
        """
        try:
            from qgis.PyQt.QtWidgets import QMessageBox

            if message_type == "error":
                QMessageBox.critical(None, "Error", message)
            elif message_type == "warning":
                QMessageBox.warning(None, "Warning", message)
            elif message_type == "success":
                QMessageBox.information(None, "Success", message)
            else:  # info
                QMessageBox.information(None, "Information", message)

        except Exception as e:
            logger.error(f"Failed to show message: {e}")

    def show_error_message(self, message: str) -> None:
        """Show error message to user.

        Args:
            message: Error message to display.
        """
        self.show_message(message, "error")

    def show_warning_message(self, message: str) -> None:
        """Show warning message to user.

        Args:
            message: Warning message to display.
        """
        self.show_message(message, "warning")

    def show_success_message(self, message: str) -> None:
        """Show success message to user.

        Args:
            message: Success message to display.
        """
        self.show_message(message, "success")

    def show_info_message(self, message: str) -> None:
        """Show info message to user.

        Args:
            message: Info message to display.
        """
        self.show_message(message, "info")


class DialogView(BaseView):
    """Base view for dialog windows.

    This extends BaseView with dialog-specific functionality.

    Signals:
        accepted: Emitted when dialog is accepted (OK clicked).
        rejected: Emitted when dialog is rejected (Cancel clicked).
    """

    accepted = pyqtSignal()
    rejected = pyqtSignal()

    def __init__(self) -> None:
        """Initialize the dialog view."""
        super().__init__()

    @abstractmethod
    def show(self) -> None:
        """Show the dialog."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the dialog."""
        pass

    @abstractmethod
    def set_title(self, title: str) -> None:
        """Set dialog title.

        Args:
            title: Dialog title.
        """
        pass
