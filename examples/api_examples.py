"""Examples of using RUBEM Hydrological v2.0 API.

This module demonstrates the new features and APIs introduced in v2.0.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

# Example 1: Configuration Management
# ====================================

def example_load_config() -> None:
    """Example: Load and validate configuration."""
    from plugin.models import RUBEMConfig
    from plugin.exceptions import ConfigurationError

    # Load from different formats
    try:
        # From TOML (recommended)
        config = RUBEMConfig.from_toml_file("config.toml")

        # From JSON
        config = RUBEMConfig.from_json_file("config.json")

        # From INI (legacy support)
        config = RUBEMConfig.from_ini_file("config.ini")

        # Access configuration with type safety
        start_date: datetime = config.sim_time.start
        end_date: datetime = config.sim_time.end
        input_dir: Path = config.directories.input

        # Configuration is immutable (frozen)
        # config.sim_time.start = "2021-01-01"  # Would raise error

        print(f"Simulation period: {start_date} to {end_date}")
        print(f"Duration: {config.sim_time.duration_months} months")

    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        print(f"Details: {e.details}")


def example_create_config() -> None:
    """Example: Create configuration programmatically."""
    from plugin.models import (
        RUBEMConfig,
        SimulationTime,
        DirectoryConfig,
        RasterFiles,
        TableFiles,
        CalibrationParameters,
    )

    config = RUBEMConfig(
        sim_time=SimulationTime(
            start=datetime(2020, 1, 1),
            end=datetime(2020, 12, 31),
        ),
        directories=DirectoryConfig(
            input=Path("/path/to/input"),
            output=Path("/path/to/output"),
        ),
        raster_files=RasterFiles(
            dem=Path("/path/to/dem.tif"),
            clone=Path("/path/to/clone.map"),
            ndvi_dir=Path("/path/to/ndvi/"),
            landuse_dir=Path("/path/to/landuse/"),
            soil=Path("/path/to/soil.tif"),
        ),
        table_files=TableFiles(
            climate=Path("/path/to/climate.csv"),
            landuse=Path("/path/to/landuse_params.csv"),
            soil=Path("/path/to/soil_params.csv"),
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

    # Save to different formats
    config.to_toml_file("config.toml")
    config.to_json_file("config.json", indent=2)
    config.to_ini_file("config.ini")


# Example 2: Logging System
# ==========================

def example_logging() -> None:
    """Example: Use the logging system."""
    from plugin.logging import get_logger, PluginLogger

    # Get logger for current module
    logger = get_logger(__name__)

    # Different log levels
    logger.debug("Detailed debug information")
    logger.info("General information")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical error")

    # Log with exception info
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero", exc_info=True)

    # Change log level at runtime
    PluginLogger.set_level("DEBUG")

    # Logs go to:
    # 1. QGIS Log Messages Panel
    # 2. File: ~/.local/share/QGIS/QGIS3/profiles/default/logs/rubem_hydrological/
    # 3. Console (if --debug flag used)


# Example 3: Exception Handling
# ==============================

def example_exceptions() -> None:
    """Example: Use custom exceptions."""
    from plugin.exceptions import (
        ValidationError,
        FileOperationError,
        RasterOperationError,
    )
    from plugin.logging import get_logger

    logger = get_logger(__name__)

    # Raise specific exceptions with context
    def validate_file(file_path: Path) -> None:
        if not file_path.exists():
            raise FileOperationError(
                f"File not found: {file_path}",
                details={"file": str(file_path), "operation": "validate"},
            )

    # Catch specific exceptions
    try:
        validate_file(Path("/nonexistent/file.txt"))
    except FileOperationError as e:
        logger.error(f"File operation failed: {e}")
        logger.debug(f"Error details: {e.details}")

    # Catch all plugin exceptions
    try:
        # Some operation
        raise ValidationError("Invalid parameter value")
    except RUBEMException as e:
        # Handle any plugin exception
        logger.error(f"Plugin error: {e}", exc_info=True)


# Example 4: Type Hints and IDE Support
# ======================================

def example_type_hints() -> None:
    """Example: How type hints improve development."""
    from pathlib import Path
    from plugin.models import RUBEMConfig

    def process_raster(
        raster_path: Path,
        output_dir: Path,
        config: RUBEMConfig,
    ) -> tuple[bool, str]:
        """Process a raster file.

        Args:
            raster_path: Path to input raster.
            output_dir: Directory for output files.
            config: Model configuration.

        Returns:
            Tuple of (success, message).
        """
        # IDE provides autocomplete for config attributes
        start = config.sim_time.start  # IDE knows this is datetime
        alpha = config.calibration.alpha  # IDE knows this is float

        # Type checker ensures correct types
        # result = start + alpha  # MyPy would catch this error

        return True, "Success"

    # Type hints enable:
    # 1. IDE autocomplete
    # 2. Type checking with MyPy
    # 3. Better documentation
    # 4. Refactoring support


# Example 5: Plugin Initialization
# =================================

def example_plugin_init() -> None:
    """Example: Initialize plugin with proper error handling."""
    from qgis.gui import QgisInterface
    from plugin.core_refactored import RUBEMHydrological
    from plugin.exceptions import PluginInitializationError
    from plugin.logging import get_logger

    logger = get_logger(__name__)

    try:
        # This is called by QGIS
        iface: QgisInterface = ...  # Provided by QGIS
        plugin = RUBEMHydrological(iface)

        # Plugin automatically:
        # - Sets up logging
        # - Loads translations
        # - Initializes resources
        # - Registers actions

        logger.info("Plugin initialized successfully")

    except PluginInitializationError as e:
        logger.error(f"Failed to initialize plugin: {e}")
        logger.debug(f"Error details: {e.details}")


# Example 6: Testing
# ==================

def example_testing() -> None:
    """Example: Write tests for plugin code."""
    import pytest
    from plugin.models import SimulationTime

    @pytest.mark.unit
    def test_simulation_time_validation():
        """Test simulation time validation."""
        from datetime import datetime
        from pydantic import ValidationError

        # Valid case
        sim_time = SimulationTime(
            start=datetime(2020, 1, 1),
            end=datetime(2020, 12, 31),
        )
        assert sim_time.duration_months == 11

        # Invalid case (end before start)
        with pytest.raises(ValidationError):
            SimulationTime(
                start=datetime(2020, 12, 31),
                end=datetime(2020, 1, 1),
            )

    # Run tests with:
    # pytest test/unit -m unit -v


# Example 7: Async Operations
# ============================

def example_async_operations() -> None:
    """Example: Run long operations in background."""
    from qgis.PyQt.QtCore import QThread, pyqtSignal
    from plugin.logging import get_logger

    logger = get_logger(__name__)

    class ProcessingWorker(QThread):
        """Worker thread for long operations."""

        progress = pyqtSignal(int)
        finished = pyqtSignal(bool, str)

        def __init__(self, config: RUBEMConfig) -> None:
            super().__init__()
            self.config = config

        def run(self) -> None:
            """Run the processing."""
            try:
                # Long operation
                for i in range(100):
                    # Do work
                    self.progress.emit(i)

                self.finished.emit(True, "Success")

            except Exception as e:
                logger.error(f"Processing failed: {e}", exc_info=True)
                self.finished.emit(False, str(e))

    # In dialog:
    # worker = ProcessingWorker(config)
    # worker.progress.connect(self.update_progress)
    # worker.finished.connect(self.on_finished)
    # worker.start()


# Example 8: Custom Validators
# =============================

def example_custom_validators() -> None:
    """Example: Create custom validation logic."""
    from pydantic import BaseModel, field_validator, Field

    class CustomConfig(BaseModel):
        """Configuration with custom validation."""

        value: float = Field(..., description="Some value")

        @field_validator("value")
        @classmethod
        def validate_value(cls, v: float) -> float:
            """Validate value is positive."""
            if v <= 0:
                raise ValueError("Value must be positive")
            return v

    # Validation happens automatically
    try:
        config = CustomConfig(value=-1)
    except ValueError as e:
        print(f"Validation failed: {e}")


if __name__ == "__main__":
    # Run examples
    print("RUBEM Hydrological v2.0 Examples")
    print("=" * 50)

    print("\n1. Configuration Management")
    # example_load_config()
    # example_create_config()

    print("\n2. Logging System")
    # example_logging()

    print("\n3. Exception Handling")
    # example_exceptions()

    print("\nSee source code for more examples!")
