"""Base exceptions for RUBEM Hydrological plugin.

This module defines a hierarchy of custom exceptions used throughout the plugin.
All plugin exceptions inherit from RUBEMException for easier catching and handling.
"""

from typing import Any


class RUBEMException(Exception):
    """Base exception for all RUBEM Hydrological plugin errors.

    All custom exceptions in the plugin should inherit from this class.
    This allows for easy catching of any plugin-specific error.

    Attributes:
        message: Human-readable error message.
        details: Optional dictionary with additional error context.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error context.
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(RUBEMException):
    """Raised when there's an error in plugin configuration.

    Examples:
        - Invalid configuration file format
        - Missing required configuration parameters
        - Invalid parameter values
    """


class ValidationError(RUBEMException):
    """Raised when input validation fails.

    Examples:
        - Invalid file paths
        - Out-of-range parameter values
        - Incompatible data formats
    """


class FileOperationError(RUBEMException):
    """Raised when file operations fail.

    Examples:
        - File not found
        - Permission denied
        - Corrupt or unreadable file
    """


class RasterOperationError(RUBEMException):
    """Raised when raster processing operations fail.

    Examples:
        - Invalid raster format
        - Mismatched CRS or extents
        - Raster calculation errors
    """


class ModelExecutionError(RUBEMException):
    """Raised when RUBEM model execution fails.

    Examples:
        - Missing input data
        - Numerical errors during computation
        - PCRaster processing errors
    """


class PluginInitializationError(RUBEMException):
    """Raised when plugin initialization fails.

    Examples:
        - Missing dependencies
        - QGIS version incompatibility
        - Failed resource loading
    """


class WorkerError(RUBEMException):
    """Raised when background worker operations fail.

    Examples:
        - Thread execution errors
        - Cancelled operations
        - Timeout errors
    """


class UIError(RUBEMException):
    """Raised when UI-related operations fail.

    Examples:
        - Widget initialization errors
        - Signal/slot connection failures
        - Layout problems
    """
