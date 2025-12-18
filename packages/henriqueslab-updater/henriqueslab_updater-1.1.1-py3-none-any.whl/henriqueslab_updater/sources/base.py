"""Abstract base class for version sources."""

from abc import ABC, abstractmethod
from typing import Optional


class VersionSource(ABC):
    """Abstract base class for version sources.

    Version sources are responsible for fetching the latest version from
    a specific source (PyPI, Homebrew, etc.). They have a priority that
    determines the order in which they are tried.
    """

    @abstractmethod
    def fetch_latest_version(self) -> Optional[str]:
        """Fetch the latest version from this source.

        Returns:
            Latest version string, or None if fetch failed
        """
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """Get the priority of this source.

        Lower numbers = higher priority (checked first).

        Returns:
            Priority integer (e.g., 10 for high priority, 100 for normal)
        """
        pass

    @property
    def name(self) -> str:
        """Get the name of this source for logging/display."""
        return self.__class__.__name__.replace("Source", "").lower()
