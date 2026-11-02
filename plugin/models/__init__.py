"""Configuration models for RUBEM Hydrological plugin.

This module provides modern configuration handling using Pydantic for validation
and type safety. It supports multiple formats (INI, JSON, TOML) and provides
comprehensive validation of all configuration parameters.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class RasterFileFormat(str, Enum):
    """Supported raster output file formats."""

    PCRASTER = "pcraster"
    GEOTIFF = "geotiff"
    HDF5 = "hdf5"


class SimulationTime(BaseModel):
    """Simulation time period configuration.

    Attributes:
        start: Start date of simulation (YYYY-MM-DD format).
        end: End date of simulation (YYYY-MM-DD format).
    """

    model_config = ConfigDict(frozen=True)

    start: datetime = Field(..., description="Simulation start date")
    end: datetime = Field(..., description="Simulation end date")

    @field_validator("end")
    @classmethod
    def validate_end_after_start(cls, end: datetime, info: Any) -> datetime:
        """Validate that end date is after start date."""
        start = info.data.get("start")
        if start and end <= start:
            raise ValueError("End date must be after start date")
        return end

    @property
    def duration_months(self) -> int:
        """Calculate duration in months."""
        return (self.end.year - self.start.year) * 12 + (
            self.end.month - self.start.month
        )


class DirectoryConfig(BaseModel):
    """Directory paths configuration.

    Attributes:
        input: Input data directory.
        output: Output results directory.
        project: Project files directory.
    """

    model_config = ConfigDict(frozen=True)

    input: Path = Field(..., description="Input data directory")
    output: Path = Field(..., description="Output results directory")
    project: Path | None = Field(None, description="Project files directory")

    @field_validator("input", "output", "project")
    @classmethod
    def validate_directory(cls, path: Path | None) -> Path | None:
        """Validate that directory paths are absolute."""
        if path is not None and not path.is_absolute():
            raise ValueError(f"Directory path must be absolute: {path}")
        return path


class FilenamePrefix(BaseModel):
    """Filename prefixes for input data files.

    All attributes represent prefixes used to identify specific input file types.
    """

    model_config = ConfigDict(frozen=True)

    dem: str = Field("dem", description="Digital Elevation Model prefix")
    clone: str = Field("clone", description="Clone map prefix")
    ndvi: str = Field("ndvi", description="NDVI maps prefix")
    landuse: str = Field("landuse", description="Land use maps prefix")
    soil: str = Field("soil", description="Soil map prefix")
    samples: str | None = Field(None, description="Sample locations prefix")


class RasterFiles(BaseModel):
    """Raster input files configuration.

    Attributes:
        dem: Digital Elevation Model file path.
        clone: Clone map file path.
        ndvi_dir: Directory containing NDVI time series.
        landuse_dir: Directory containing land use maps.
        soil: Soil map file path.
    """

    model_config = ConfigDict(frozen=True)

    dem: Path = Field(..., description="Digital Elevation Model raster")
    clone: Path = Field(..., description="Clone map raster")
    ndvi_dir: Path = Field(..., description="NDVI time series directory")
    landuse_dir: Path = Field(..., description="Land use maps directory")
    soil: Path = Field(..., description="Soil type raster")

    @field_validator("dem", "clone", "soil")
    @classmethod
    def validate_file_exists(cls, path: Path) -> Path:
        """Validate that raster files exist."""
        if not path.exists():
            raise FileNotFoundError(f"Raster file not found: {path}")
        return path

    @field_validator("ndvi_dir", "landuse_dir")
    @classmethod
    def validate_directory_exists(cls, path: Path) -> Path:
        """Validate that directories exist."""
        if not path.exists():
            raise NotADirectoryError(f"Directory not found: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")
        return path


class TableFiles(BaseModel):
    """Tabular input files configuration.

    Attributes:
        climate: Climate data table file.
        landuse: Land use parameters table file.
        soil: Soil parameters table file.
    """

    model_config = ConfigDict(frozen=True)

    climate: Path = Field(..., description="Climate data table")
    landuse: Path = Field(..., description="Land use parameters table")
    soil: Path = Field(..., description="Soil parameters table")

    @field_validator("climate", "landuse", "soil")
    @classmethod
    def validate_file_exists(cls, path: Path) -> Path:
        """Validate that table files exist."""
        if not path.exists():
            raise FileNotFoundError(f"Table file not found: {path}")
        return path


class CalibrationParameters(BaseModel):
    """Model calibration parameters.

    These parameters control the hydrological processes in RUBEM model.
    """

    model_config = ConfigDict(frozen=True)

    # Interception parameters
    alpha: float = Field(
        ..., ge=0.0, le=1.0, description="Interception parameter alpha"
    )
    
    # Runoff parameters
    beta: float = Field(..., ge=0.0, description="Runoff coefficient beta")
    
    # Baseflow parameters
    lambda_factor: float = Field(
        ..., ge=0.0, le=1.0, description="Baseflow recession coefficient"
    )
    
    # Evapotranspiration parameters
    kc: float = Field(..., ge=0.0, description="Crop coefficient")
    
    # Soil parameters
    field_capacity: float = Field(
        ..., ge=0.0, le=1.0, description="Soil field capacity"
    )
    wilting_point: float = Field(
        ..., ge=0.0, le=1.0, description="Soil wilting point"
    )
    
    @field_validator("wilting_point")
    @classmethod
    def validate_wilting_point(cls, wp: float, info: Any) -> float:
        """Validate that wilting point is less than field capacity."""
        fc = info.data.get("field_capacity")
        if fc and wp >= fc:
            raise ValueError("Wilting point must be less than field capacity")
        return wp


class OutputOptions(BaseModel):
    """Output file generation options.

    Attributes:
        generate_timeseries: Generate time series output files.
        generate_maps: Generate raster map output files.
        generate_stats: Generate statistical summary files.
    """

    model_config = ConfigDict(frozen=True)

    generate_timeseries: bool = Field(True, description="Generate time series")
    generate_maps: bool = Field(True, description="Generate output maps")
    generate_stats: bool = Field(True, description="Generate statistics")


class RasterFormatConfig(BaseModel):
    """Raster output format configuration.

    Attributes:
        format: Output raster format.
        compression: Enable compression for output files.
        compression_level: Compression level (1-9).
    """

    model_config = ConfigDict(frozen=True)

    format: RasterFileFormat = Field(
        RasterFileFormat.GEOTIFF, description="Output raster format"
    )
    compression: bool = Field(True, description="Enable compression")
    compression_level: int = Field(
        6, ge=1, le=9, description="Compression level (1-9)"
    )


class RUBEMConfig(BaseSettings):
    """Complete RUBEM model configuration.

    This is the main configuration class that combines all configuration sections.
    It can be loaded from various file formats and provides validation.

    Example:
        >>> config = RUBEMConfig.from_ini_file("config.ini")
        >>> config = RUBEMConfig.from_json_file("config.json")
        >>> config = RUBEMConfig.from_toml_file("config.toml")
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    sim_time: SimulationTime
    directories: DirectoryConfig
    filename_prefixes: FilenamePrefix = Field(default_factory=FilenamePrefix)
    raster_files: RasterFiles
    table_files: TableFiles
    calibration: CalibrationParameters
    output_options: OutputOptions = Field(default_factory=OutputOptions)
    raster_format: RasterFormatConfig = Field(default_factory=RasterFormatConfig)

    @classmethod
    def from_ini_file(cls, path: Path | str) -> RUBEMConfig:
        """Load configuration from INI file.

        Args:
            path: Path to INI configuration file.

        Returns:
            Loaded and validated configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            ValidationError: If configuration is invalid.
        """
        import configparser

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        config = configparser.ConfigParser()
        config.read(path, encoding="utf-8")

        # Convert INI sections to dict structure
        config_dict = {section: dict(config[section]) for section in config.sections()}

        return cls.model_validate(cls._transform_ini_dict(config_dict))

    @classmethod
    def from_json_file(cls, path: Path | str) -> RUBEMConfig:
        """Load configuration from JSON file.

        Args:
            path: Path to JSON configuration file.

        Returns:
            Loaded and validated configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            ValidationError: If configuration is invalid.
        """
        import json

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, encoding="utf-8") as f:
            config_dict = json.load(f)

        return cls.model_validate(config_dict)

    @classmethod
    def from_toml_file(cls, path: Path | str) -> RUBEMConfig:
        """Load configuration from TOML file.

        Args:
            path: Path to TOML configuration file.

        Returns:
            Loaded and validated configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            ValidationError: If configuration is invalid.
        """
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # fallback for Python < 3.11

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "rb") as f:
            config_dict = tomllib.load(f)

        return cls.model_validate(config_dict)

    @staticmethod
    def _transform_ini_dict(ini_dict: dict[str, Any]) -> dict[str, Any]:
        """Transform INI dict structure to match Pydantic model structure.

        Args:
            ini_dict: Dictionary from INI file sections.

        Returns:
            Transformed dictionary matching model structure.
        """
        # This would contain transformation logic from the old schema format
        # to the new Pydantic model structure
        # Implementation depends on actual INI file structure
        return ini_dict

    def to_ini_file(self, path: Path | str) -> None:
        """Save configuration to INI file.

        Args:
            path: Path where to save the configuration.
        """
        import configparser

        config = configparser.ConfigParser()
        
        # Convert model to INI sections
        # Implementation would transform Pydantic models back to INI format
        
        with open(path, "w", encoding="utf-8") as f:
            config.write(f)

    def to_json_file(self, path: Path | str, indent: int = 2) -> None:
        """Save configuration to JSON file.

        Args:
            path: Path where to save the configuration.
            indent: JSON indentation level.
        """
        import json

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=indent, default=str)

    def to_toml_file(self, path: Path | str) -> None:
        """Save configuration to TOML file.

        Args:
            path: Path where to save the configuration.
        """
        import tomli_w

        with open(path, "wb") as f:
            tomli_w.dump(self.model_dump(), f)
