"""Logging configuration for RUBEM Hydrological plugin.

This module provides a centralized logging system with:
- File rotation to prevent excessive log file growth
- Configurable log levels
- Structured formatting for better debugging
- Separate handlers for file and console output
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

from qgis.core import QgsMessageLog, Qgis

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class QGISLogHandler(logging.Handler):
    """Custom handler that forwards Python logs to QGIS message log.

    This handler integrates Python logging with QGIS's native logging system,
    making logs visible in the QGIS Log Messages panel.
    """

    # Map Python log levels to QGIS log levels
    LEVEL_MAP = {
        logging.DEBUG: Qgis.Info,
        logging.INFO: Qgis.Info,
        logging.WARNING: Qgis.Warning,
        logging.ERROR: Qgis.Critical,
        logging.CRITICAL: Qgis.Critical,
    }

    def __init__(self, tag: str = "RUBEM Hydrological") -> None:
        """Initialize the QGIS log handler.

        Args:
            tag: Tag to use in QGIS log messages for filtering.
        """
        super().__init__()
        self.tag = tag

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to QGIS message log.

        Args:
            record: The log record to emit.
        """
        try:
            msg = self.format(record)
            level = self.LEVEL_MAP.get(record.levelno, Qgis.Info)
            QgsMessageLog.logMessage(msg, self.tag, level)
        except Exception:
            self.handleError(record)


class PluginLogger:
    """Centralized logger for the RUBEM Hydrological plugin.

    This class provides a singleton logger instance with both file and QGIS handlers.
    It supports configuration of log level and automatic log rotation.

    Example:
        >>> logger = PluginLogger.get_logger("plugin.core")
        >>> logger.info("Plugin initialized")
        >>> logger.error("Configuration error", exc_info=True)
    """

    _loggers: dict[str, logging.Logger] = {}
    _configured: bool = False
    _log_dir: Path | None = None
    _log_level: int = logging.INFO

    @classmethod
    def setup(
        cls,
        log_dir: Path | str | None = None,
        level: LogLevel = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
    ) -> None:
        """Configure the plugin logging system.

        This should be called once during plugin initialization.

        Args:
            log_dir: Directory to store log files. If None, logs only to QGIS.
            level: Minimum log level to record.
            max_bytes: Maximum size of each log file before rotation.
            backup_count: Number of backup log files to keep.
        """
        if cls._configured:
            return

        cls._log_level = getattr(logging, level)

        if log_dir is not None:
            cls._log_dir = Path(log_dir)
            cls._log_dir.mkdir(parents=True, exist_ok=True)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger with the given name.

        Args:
            name: Name of the logger, typically the module name.

        Returns:
            Configured logger instance.

        Example:
            >>> logger = PluginLogger.get_logger(__name__)
        """
        if name in cls._loggers:
            return cls._loggers[name]

        # Create logger
        logger = logging.getLogger(f"rubem.{name}")
        logger.setLevel(cls._log_level)
        logger.propagate = False

        # Remove any existing handlers
        logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Add QGIS handler
        qgis_handler = QGISLogHandler()
        qgis_handler.setLevel(cls._log_level)
        qgis_handler.setFormatter(formatter)
        logger.addHandler(qgis_handler)

        # Add file handler if log directory is configured
        if cls._log_dir is not None:
            log_file = cls._log_dir / f"rubem_{name.replace('.', '_')}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(cls._log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Add console handler for development
        if "--debug" in sys.argv or "--verbose" in sys.argv:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def set_level(cls, level: LogLevel) -> None:
        """Change the log level for all existing loggers.

        Args:
            level: New minimum log level.
        """
        cls._log_level = getattr(logging, level)
        for logger in cls._loggers.values():
            logger.setLevel(cls._log_level)
            for handler in logger.handlers:
                handler.setLevel(cls._log_level)

    @classmethod
    def reset(cls) -> None:
        """Reset the logging configuration.

        This is primarily useful for testing.
        """
        for logger in cls._loggers.values():
            logger.handlers.clear()
        cls._loggers.clear()
        cls._configured = False
        cls._log_dir = None
        cls._log_level = logging.INFO


# Convenience function for getting loggers
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    This is a convenience function that wraps PluginLogger.get_logger().

    Args:
        name: Name of the logger, typically __name__.

    Returns:
        Configured logger instance.

    Example:
        >>> from plugin.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Module loaded")
    """
    return PluginLogger.get_logger(name)
