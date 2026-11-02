"""Service layer for RUBEM Hydrological plugin.

Services encapsulate business logic and operations that don't belong
in models or controllers. They provide reusable functionality across
the application.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from plugin.logging import get_logger

logger = get_logger(__name__)


class BaseService(ABC):
    """Abstract base class for services.

    Services handle business logic, data processing, and external operations.
    They should be stateless when possible and focus on specific domains.
    """

    def __init__(self) -> None:
        """Initialize the service."""
        logger.debug(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def validate(self) -> tuple[bool, list[str]]:
        """Validate service state or inputs.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        pass

    def cleanup(self) -> None:
        """Cleanup service resources."""
        logger.debug(f"{self.__class__.__name__} cleanup")
