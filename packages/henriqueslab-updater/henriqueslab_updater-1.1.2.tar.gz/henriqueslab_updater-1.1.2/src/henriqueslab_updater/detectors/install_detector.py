"""Installation method detection."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

InstallMethod = Literal["homebrew", "pipx", "uv", "pip-user", "pip", "dev", "unknown"]


@dataclass
class InstallInfo:
    """Installation information."""

    method: InstallMethod
    friendly_name: str
    upgrade_command: str
    executable_path: str


class InstallDetector:
    """Detect installation method for a package."""

    # Common Homebrew prefixes
    HOMEBREW_PREFIXES = [
        "/opt/homebrew",  # Apple Silicon Macs
        "/usr/local",  # Intel Macs and some Linux
        "/home/linuxbrew/.linuxbrew",  # Linux Homebrew
    ]

    def __init__(self, package_name: str):
        """Initialize detector for a specific package.

        Args:
            package_name: Name of the package (e.g., "rxiv-maker")
        """
        self.package_name = package_name
        # Normalize package name for path checking (replace - with _)
        self.package_name_normalized = package_name.replace("-", "_")

    def detect(self) -> InstallInfo:
        """Detect installation method and return information.

        Returns:
            InstallInfo with method, friendly name, and upgrade command
        """
        executable = Path(sys.executable).resolve()
        executable_str = str(executable)

        method = self._detect_method(executable, executable_str)

        return InstallInfo(
            method=method,
            friendly_name=self._get_friendly_name(method),
            upgrade_command=self._get_upgrade_command(method),
            executable_path=executable_str,
        )

    def _detect_method(self, executable: Path, executable_str: str) -> InstallMethod:
        """Detect the installation method.

        Args:
            executable: Path object of Python executable
            executable_str: String representation of executable path

        Returns:
            Detected installation method
        """
        # 1. Check for Homebrew
        # Check for Homebrew by looking for key path components
        # (resolve() might prepend /System/Volumes/Data on macOS)
        for prefix in self.HOMEBREW_PREFIXES:
            if prefix in executable_str:
                if "/Cellar/" in executable_str or "/opt/" in executable_str:
                    return "homebrew"

        # 2. Check for pipx
        if (
            f".local/pipx/venvs/{self.package_name}" in executable_str
            or f".local/share/pipx/venvs/{self.package_name}" in executable_str
            or f".local/pipx/venvs/{self.package_name_normalized}" in executable_str
            or f".local/share/pipx/venvs/{self.package_name_normalized}" in executable_str
        ):
            return "pipx"

        # 3. Check for uv tools
        if (
            f".local/share/uv/tools/{self.package_name}" in executable_str
            or f".local/share/uv/tools/{self.package_name_normalized}" in executable_str
        ):
            return "uv"

        # 4. Check for development installation
        if self._is_dev_install():
            return "dev"

        # 5. Check for pip user installation
        try:
            import site

            user_site = site.getusersitepackages()
            if user_site and user_site in executable_str:
                return "pip-user"
        except Exception:
            pass

        # 6. Check for system pip installation
        if "/site-packages/" in executable_str or "/dist-packages/" in executable_str:
            return "pip"

        # 7. Unknown
        return "unknown"

    def _is_dev_install(self) -> bool:
        """Check if this is a development installation.

        Returns:
            True if dev install, False otherwise
        """
        try:
            # Try to import the package
            package_module = __import__(self.package_name_normalized)
            package_path = Path(package_module.__file__).resolve().parent.parent.parent

            # Check for .git directory
            if (package_path / ".git").exists():
                return True

            # Check for .egg-info directories
            if any(package_path.glob("*.egg-info")):
                return True

        except (ImportError, AttributeError, Exception):
            pass

        return False

    def _get_friendly_name(self, method: InstallMethod) -> str:
        """Get friendly name for installation method.

        Args:
            method: Installation method

        Returns:
            User-friendly name
        """
        names = {
            "homebrew": "Homebrew",
            "pipx": "pipx",
            "uv": "uv tool",
            "pip-user": "pip (user)",
            "pip": "pip",
            "dev": "Development mode",
            "unknown": "Unknown",
        }
        return names[method]

    def _get_upgrade_command(self, method: InstallMethod) -> str:
        """Get upgrade command for installation method.

        Args:
            method: Installation method

        Returns:
            Upgrade command string
        """
        commands = {
            "homebrew": f"brew update && brew upgrade {self.package_name}",
            "pipx": f"pipx upgrade {self.package_name}",
            "uv": f"uv tool upgrade {self.package_name}",
            "pip-user": f"pip install --upgrade --user {self.package_name}",
            "pip": f"pip install --upgrade {self.package_name}",
            "dev": "cd <repo> && git pull && uv sync",
            "unknown": f"pip install --upgrade {self.package_name}",
        }
        return commands[method]
