"""Abstract base class for notifiers."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Notifier(ABC):
    """Abstract base class for update notifiers.

    Notifiers are responsible for formatting and displaying update notifications.
    """

    @abstractmethod
    def format(self, update_info: Dict[str, Any]) -> str:
        """Format update information as a string.

        Args:
            update_info: Dictionary containing update information

        Returns:
            Formatted notification string
        """
        pass

    @abstractmethod
    def display(self, message: str) -> None:
        """Display the formatted message.

        Args:
            message: The formatted message to display
        """
        pass

    def notify(self, update_info: Dict[str, Any]) -> None:
        """Format and display update information.

        Args:
            update_info: Dictionary containing update information
        """
        message = self.format(update_info)
        self.display(message)
