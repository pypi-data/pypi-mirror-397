"""Homebrew version source."""

import re
import subprocess
from typing import Optional

from .base import VersionSource
from .github import parse_formula_version


class HomebrewSource(VersionSource):
    """Fetch latest version from Homebrew (brew outdated + GitHub fallback)."""

    def __init__(
        self,
        formula_name: str,
        tap: str = "henriqueslab/formulas",
        timeout: int = 5,
    ):
        """Initialize Homebrew source.

        Args:
            formula_name: Formula name (e.g., "rxiv-maker")
            tap: Homebrew tap (default: "henriqueslab/formulas")
            timeout: Command/request timeout in seconds
        """
        self.formula_name = formula_name
        self.tap = tap
        self.timeout = timeout

    def fetch_latest_version(self) -> Optional[str]:
        """Fetch latest version from Homebrew.

        Tries brew outdated first, falls back to GitHub formula parsing.

        Returns:
            Latest version string, or None if fetch failed
        """
        # Method 1: brew outdated (most reliable)
        version = self._check_brew_outdated()
        if version:
            return version

        # Method 2: GitHub formula (fallback)
        return self._check_formula_github()

    def _check_brew_outdated(self) -> Optional[str]:
        """Check if package is outdated using brew command.

        Returns:
            Latest version if outdated, None otherwise
        """
        try:
            # Run: brew outdated --verbose <package>
            # Output format: "package (1.0.0) < 1.1.0"
            result = subprocess.run(
                ["brew", "outdated", "--verbose", self.formula_name],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )

            if result.returncode != 0:
                # Package is up to date or not installed
                return None

            # Parse output: "package (1.0.0) < 1.1.0"
            output = result.stdout.strip()
            match = re.search(r"\(([\d.]+)\)\s*<\s*([\d.]+)", output)
            if match:
                return match.group(2)  # latest version

            return None

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return None

    def _check_formula_github(self) -> Optional[str]:
        """Check latest version from GitHub formula file.

        Returns:
            Latest version if found, None otherwise
        """
        return parse_formula_version(self.formula_name, timeout=self.timeout)

    def get_priority(self) -> int:
        """Get priority (10 = high - use Homebrew if installed via Homebrew)."""
        return 10
