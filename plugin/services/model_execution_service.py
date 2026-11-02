"""Model execution service for RUBEM Hydrological plugin.

This service handles the execution of the RUBEM hydrological model,
including process management, progress monitoring, and result handling.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

from plugin.exceptions import ModelExecutionError
from plugin.logging import get_logger
from plugin.models import RUBEMConfig
from plugin.services import BaseService

logger = get_logger(__name__)


class ModelExecutionService(BaseService):
    """Service for executing RUBEM hydrological model.

    This service manages:
    - Model process execution
    - Progress monitoring
    - Output capturing and parsing
    - Error handling and recovery
    """

    def __init__(self, model_executable: Path | str) -> None:
        """Initialize model execution service.

        Args:
            model_executable: Path to RUBEM executable.

        Raises:
            ModelExecutionError: If executable not found.
        """
        super().__init__()
        self.model_executable = Path(model_executable)

        if not self.model_executable.exists():
            raise ModelExecutionError(
                f"Model executable not found: {self.model_executable}",
                details={"executable": str(self.model_executable)},
            )

        if not self.model_executable.is_file():
            raise ModelExecutionError(
                f"Model executable is not a file: {self.model_executable}",
                details={"executable": str(self.model_executable)},
            )

        self._process: subprocess.Popen | None = None
        self._is_running: bool = False

    def validate(self) -> tuple[bool, list[str]]:
        """Validate service state.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors: list[str] = []

        if not self.model_executable.exists():
            errors.append(f"Executable not found: {self.model_executable}")

        if self._is_running:
            errors.append("A model execution is already running")

        return len(errors) == 0, errors

    def execute(
        self,
        config: RUBEMConfig,
        config_file: Path | str,
        progress_callback: Callable[[int, str], None] | None = None,
        output_callback: Callable[[str], None] | None = None,
    ) -> tuple[bool, str]:
        """Execute RUBEM model with given configuration.

        Args:
            config: Configuration for model execution.
            config_file: Path to configuration file.
            progress_callback: Optional callback for progress updates (percent, message).
            output_callback: Optional callback for output lines.

        Returns:
            Tuple of (success, output_message).

        Raises:
            ModelExecutionError: If execution fails.
        """
        if self._is_running:
            raise ModelExecutionError(
                "Cannot start execution: model is already running",
                details={"state": "running"},
            )

        logger.info("Starting RUBEM model execution")
        logger.debug(f"Executable: {self.model_executable}")
        logger.debug(f"Config file: {config_file}")

        try:
            # Validate configuration
            if not Path(config_file).exists():
                raise ModelExecutionError(
                    f"Configuration file not found: {config_file}",
                    details={"config_file": str(config_file)},
                )

            # Validate output directory is writable
            output_dir = config.directories.output
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            if not output_dir.is_dir():
                raise ModelExecutionError(
                    f"Output path is not a directory: {output_dir}",
                    details={"output_dir": str(output_dir)},
                )

            # Build command
            command = [
                str(self.model_executable),
                "--configfile",
                str(config_file),
            ]

            logger.info(f"Executing command: {' '.join(command)}")

            # Execute process
            self._is_running = True
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Capture output
            output_lines: list[str] = []

            if self._process.stdout:
                for line in self._process.stdout:
                    line = line.strip()
                    if line:
                        output_lines.append(line)
                        logger.debug(f"Model output: {line}")

                        if output_callback:
                            output_callback(line)

                        # Parse progress if possible
                        progress = self._parse_progress(line)
                        if progress is not None and progress_callback:
                            progress_callback(progress, line)

            # Wait for completion
            return_code = self._process.wait()
            self._is_running = False

            # Check for errors
            if return_code != 0:
                error_output = ""
                if self._process.stderr:
                    error_output = self._process.stderr.read()

                raise ModelExecutionError(
                    f"Model execution failed with code {return_code}",
                    details={
                        "return_code": return_code,
                        "error_output": error_output,
                        "config_file": str(config_file),
                    },
                )

            output = "\n".join(output_lines)
            logger.info("Model execution completed successfully")

            return True, output

        except subprocess.TimeoutExpired as e:
            self._is_running = False
            raise ModelExecutionError(
                "Model execution timed out",
                details={"timeout": str(e), "config_file": str(config_file)},
            ) from e

        except Exception as e:
            self._is_running = False
            if isinstance(e, ModelExecutionError):
                raise
            raise ModelExecutionError(
                f"Model execution failed: {e}",
                details={"error": str(e), "config_file": str(config_file)},
            ) from e

    def _parse_progress(self, line: str) -> int | None:
        """Parse progress percentage from output line.

        Args:
            line: Output line from model.

        Returns:
            Progress percentage (0-100) or None if not parseable.
        """
        # This is a placeholder - actual implementation depends on
        # the format of RUBEM model output
        # Example patterns to look for:
        # - "Progress: 45%"
        # - "Processing month 5 of 12"
        # - etc.

        import re

        # Try to find percentage pattern
        match = re.search(r"(\d+)%", line)
        if match:
            return int(match.group(1))

        # Try to find "X of Y" pattern
        match = re.search(r"(\d+)\s+of\s+(\d+)", line)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            if total > 0:
                return int((current / total) * 100)

        return None

    def cancel(self) -> None:
        """Cancel running model execution."""
        if self._process and self._is_running:
            logger.info("Cancelling model execution")
            self._process.terminate()

            # Wait a bit for graceful termination
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate, killing...")
                self._process.kill()

            self._is_running = False
            logger.info("Model execution cancelled")

    def is_running(self) -> bool:
        """Check if model is currently executing.

        Returns:
            True if model is running.
        """
        return self._is_running

    def cleanup(self) -> None:
        """Cleanup service resources."""
        if self._is_running:
            self.cancel()
        super().cleanup()
