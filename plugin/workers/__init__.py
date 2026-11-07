"""Modern QThread workers for RUBEM Hydrological plugin.

This module provides type-safe, signal-based workers for asynchronous
operations following PyQt6 best practices.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from qgis.PyQt.QtCore import QThread, pyqtSignal

from plugin.exceptions import ModelExecutionError, WorkerError
from plugin.logging import get_logger
from plugin.models import RUBEMConfig
from plugin.services.model_execution_service import ModelExecutionService

logger = get_logger(__name__)


class BaseWorker(QThread):
    """Abstract base worker for asynchronous operations.

    All workers should inherit from this class and implement the run() method.

    Signals:
        error: Emitted when an error occurs (error_message: str).
        finished: Emitted when work completes (success: bool, message: str).
        progress: Emitted to report progress (percent: int, message: str).
    """

    error = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int, str)

    def __init__(self) -> None:
        """Initialize the worker."""
        super().__init__()
        self._is_cancelled = False
        logger.debug(f"{self.__class__.__name__} initialized")

    def run(self) -> None:
        """Execute the worker's task.

        This method must be implemented by subclasses.
        It should emit appropriate signals and check _is_cancelled periodically.
        """
        raise NotImplementedError("Subclasses must implement run()")

    def cancel(self) -> None:
        """Request cancellation of the worker."""
        logger.info(f"Cancelling {self.__class__.__name__}")
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """Check if worker has been cancelled.

        Returns:
            True if cancellation was requested.
        """
        return self._is_cancelled


class ModelExecutionWorker(BaseWorker):
    """Worker for executing RUBEM model in background.

    This worker handles model execution asynchronously, emitting signals
    for progress updates and output capture.

    Signals:
        output: Emitted for each output line (line: str).
        error: Emitted when an error occurs (error_message: str).
        finished: Emitted when execution completes (success: bool, message: str).
        progress: Emitted to report progress (percent: int, message: str).

    Attributes:
        config: Model configuration.
        config_file: Path to configuration file.
        model_executable: Path to model executable.
    """

    output = pyqtSignal(str)

    def __init__(
        self,
        config: RUBEMConfig,
        config_file: Path | str,
        model_executable: Path | str,
    ) -> None:
        """Initialize model execution worker.

        Args:
            config: Model configuration.
            config_file: Path to configuration file.
            model_executable: Path to model executable.
        """
        super().__init__()
        self.config = config
        self.config_file = Path(config_file)
        self.model_executable = Path(model_executable)

        # Initialize service
        try:
            self.service = ModelExecutionService(self.model_executable)
        except ModelExecutionError as e:
            logger.error(f"Failed to initialize execution service: {e}")
            raise WorkerError(
                "Cannot initialize model execution worker",
                details={"error": str(e)},
            ) from e

    def run(self) -> None:
        """Execute the model in background thread."""
        logger.info("Starting model execution worker")

        try:
            # Define callbacks
            def progress_callback(percent: int, message: str) -> None:
                """Handle progress updates."""
                if not self._is_cancelled:
                    self.progress.emit(percent, message)

            def output_callback(line: str) -> None:
                """Handle output lines."""
                if not self._is_cancelled:
                    self.output.emit(line)

            # Execute model
            success, message = self.service.execute(
                config=self.config,
                config_file=self.config_file,
                progress_callback=progress_callback,
                output_callback=output_callback,
            )

            if self._is_cancelled:
                logger.info("Model execution was cancelled")
                self.finished.emit(False, "Execution cancelled by user")
            else:
                logger.info("Model execution completed")
                self.finished.emit(success, message)

        except ModelExecutionError as e:
            logger.error(f"Model execution error: {e}", exc_info=True)
            error_msg = f"{e.message}\n\nDetails: {e.details}"
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg)

        except Exception as e:
            logger.error(f"Unexpected error in worker: {e}", exc_info=True)
            error_msg = f"Unexpected error: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg)

    def cancel(self) -> None:
        """Cancel the model execution."""
        super().cancel()
        if hasattr(self, "service"):
            self.service.cancel()


class FileOperationWorker(BaseWorker):
    """Worker for file operations in background.

    Use this for heavy file I/O operations like loading large rasters,
    processing multiple files, etc.

    Attributes:
        operation: Callable that performs the file operation.
        operation_args: Arguments to pass to the operation.
    """

    def __init__(
        self,
        operation: Callable[..., Any],
        *operation_args: Any,
        **operation_kwargs: Any,
    ) -> None:
        """Initialize file operation worker.

        Args:
            operation: Function to execute.
            *operation_args: Positional arguments for operation.
            **operation_kwargs: Keyword arguments for operation.
        """
        super().__init__()
        self.operation = operation
        self.operation_args = operation_args
        self.operation_kwargs = operation_kwargs

    def run(self) -> None:
        """Execute the file operation."""
        logger.info(f"Starting file operation: {self.operation.__name__}")

        try:
            result = self.operation(*self.operation_args, **self.operation_kwargs)

            if self._is_cancelled:
                logger.info("File operation was cancelled")
                self.finished.emit(False, "Operation cancelled by user")
            else:
                logger.info("File operation completed")
                self.finished.emit(True, str(result))

        except Exception as e:
            logger.error(f"File operation error: {e}", exc_info=True)
            error_msg = f"File operation failed: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg)


class ValidationWorker(BaseWorker):
    """Worker for validation operations in background.

    Use this for potentially slow validation operations like checking
    many files, validating raster properties, etc.

    Attributes:
        config: Configuration to validate.
    """

    def __init__(self, config: RUBEMConfig) -> None:
        """Initialize validation worker.

        Args:
            config: Configuration to validate.
        """
        super().__init__()
        self.config = config

    def run(self) -> None:
        """Execute validation."""
        logger.info("Starting configuration validation")

        try:
            from plugin.services.config_service import ConfigService

            service = ConfigService()

            # Emit progress
            self.progress.emit(10, "Validating simulation time...")

            if self._is_cancelled:
                self.finished.emit(False, "Validation cancelled")
                return

            self.progress.emit(30, "Validating directories...")

            if self._is_cancelled:
                self.finished.emit(False, "Validation cancelled")
                return

            self.progress.emit(50, "Validating raster files...")

            if self._is_cancelled:
                self.finished.emit(False, "Validation cancelled")
                return

            self.progress.emit(70, "Validating table files...")

            if self._is_cancelled:
                self.finished.emit(False, "Validation cancelled")
                return

            self.progress.emit(90, "Validating parameters...")

            # Perform actual validation
            is_valid, errors = service.validate_config(self.config)

            self.progress.emit(100, "Validation complete")

            if is_valid:
                logger.info("Configuration is valid")
                self.finished.emit(True, "Configuration is valid")
            else:
                error_msg = "Configuration validation failed:\n" + "\n".join(errors)
                logger.warning(error_msg)
                self.error.emit(error_msg)
                self.finished.emit(False, error_msg)

        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            error_msg = f"Validation failed: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg)
