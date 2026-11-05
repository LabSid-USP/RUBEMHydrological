"""Unit tests for exception classes.

These tests verify that custom exceptions work correctly and provide
appropriate error information.
"""

from __future__ import annotations

import pytest

from plugin.exceptions import (
    RUBEMException,
    ConfigurationError,
    ValidationError,
    FileOperationError,
    RasterOperationError,
    ModelExecutionError,
    PluginInitializationError,
    WorkerError,
    UIError,
)


@pytest.mark.unit
class TestRUBEMException:
    """Test cases for the base RUBEMException class."""

    def test_basic_exception(self) -> None:
        """Test creating a basic exception with message only."""
        exc = RUBEMException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.details == {}

    def test_exception_with_details(self) -> None:
        """Test creating exception with additional details."""
        details = {"file": "test.txt", "line": 42}
        exc = RUBEMException("Test error", details=details)
        assert exc.message == "Test error"
        assert exc.details == details
        assert "file=test.txt" in str(exc)
        assert "line=42" in str(exc)

    def test_exception_inheritance(self) -> None:
        """Test that specific exceptions inherit from RUBEMException."""
        exceptions = [
            ConfigurationError,
            ValidationError,
            FileOperationError,
            RasterOperationError,
            ModelExecutionError,
            PluginInitializationError,
            WorkerError,
            UIError,
        ]

        for exc_class in exceptions:
            exc = exc_class("Test message")
            assert isinstance(exc, RUBEMException)
            assert isinstance(exc, Exception)

    def test_exception_catching(self) -> None:
        """Test that specific exceptions can be caught as RUBEMException."""
        try:
            raise ConfigurationError("Config error")
        except RUBEMException as e:
            assert isinstance(e, ConfigurationError)
            assert e.message == "Config error"


@pytest.mark.unit
class TestSpecificExceptions:
    """Test cases for specific exception types."""

    def test_configuration_error(self) -> None:
        """Test ConfigurationError exception."""
        exc = ConfigurationError("Invalid config", details={"parameter": "start_date"})
        assert "Invalid config" in str(exc)
        assert exc.details["parameter"] == "start_date"

    def test_validation_error(self) -> None:
        """Test ValidationError exception."""
        exc = ValidationError("Validation failed", details={"field": "alpha"})
        assert "Validation failed" in str(exc)
        assert exc.details["field"] == "alpha"

    def test_file_operation_error(self) -> None:
        """Test FileOperationError exception."""
        exc = FileOperationError("File not found", details={"path": "/test/file.txt"})
        assert "File not found" in str(exc)
        assert exc.details["path"] == "/test/file.txt"

    def test_raster_operation_error(self) -> None:
        """Test RasterOperationError exception."""
        exc = RasterOperationError(
            "Raster processing failed", details={"operation": "clip"}
        )
        assert "Raster processing failed" in str(exc)
        assert exc.details["operation"] == "clip"

    def test_model_execution_error(self) -> None:
        """Test ModelExecutionError exception."""
        exc = ModelExecutionError(
            "Model run failed", details={"step": 5, "month": "2020-05"}
        )
        assert "Model run failed" in str(exc)
        assert exc.details["step"] == 5
        assert exc.details["month"] == "2020-05"

    def test_plugin_initialization_error(self) -> None:
        """Test PluginInitializationError exception."""
        exc = PluginInitializationError(
            "Plugin init failed", details={"missing": "dependency"}
        )
        assert "Plugin init failed" in str(exc)
        assert exc.details["missing"] == "dependency"

    def test_worker_error(self) -> None:
        """Test WorkerError exception."""
        exc = WorkerError("Worker failed", details={"worker_id": "worker_1"})
        assert "Worker failed" in str(exc)
        assert exc.details["worker_id"] == "worker_1"

    def test_ui_error(self) -> None:
        """Test UIError exception."""
        exc = UIError("UI error", details={"widget": "button"})
        assert "UI error" in str(exc)
        assert exc.details["widget"] == "button"
