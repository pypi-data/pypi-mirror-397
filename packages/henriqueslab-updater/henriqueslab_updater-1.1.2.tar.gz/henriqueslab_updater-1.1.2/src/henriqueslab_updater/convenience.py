"""Convenience functions for easy integration.

These functions provide a simple API similar to the original implementations
in folder2md4llms, taskrepo, and rxiv-maker.
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from .core.update_checker import UpdateChecker
from .notifiers.base import Notifier
from .sources.base import VersionSource


# Global singleton instance
_update_checker: Optional[UpdateChecker] = None


def get_update_checker(
    package_name: Optional[str] = None,
    current_version: Optional[str] = None,
    **kwargs: Any,
) -> UpdateChecker:
    """Get the global update checker instance (singleton pattern).

    Args:
        package_name: Package name (required on first call)
        current_version: Current version (required on first call)
        **kwargs: Additional arguments passed to UpdateChecker

    Returns:
        UpdateChecker instance

    Raises:
        ValueError: If package_name or current_version not provided on first call
    """
    global _update_checker

    if _update_checker is None:
        if package_name is None or current_version is None:
            raise ValueError(
                "package_name and current_version required on first call to get_update_checker()"
            )
        _update_checker = UpdateChecker(package_name, current_version, **kwargs)

    return _update_checker


def check_for_updates_async_background(
    package_name: Optional[str] = None,
    current_version: Optional[str] = None,
    enabled: bool = True,
    force: bool = False,
    **kwargs: Any,
) -> None:
    """Start async update check in background (non-blocking).

    This is the recommended way to check for updates without blocking the CLI.
    Results are cached and can be displayed later with show_update_notification().

    Args:
        package_name: Package name (required if not already initialized)
        current_version: Current version (required if not already initialized)
        enabled: Whether update checking is enabled
        force: Force check even if cache is fresh
        **kwargs: Additional arguments for UpdateChecker initialization
    """
    if not enabled:
        return

    try:
        checker = get_update_checker(package_name, current_version, **kwargs)
        checker.check_async(force=force)
    except ValueError:
        # Not initialized and no package info provided
        pass


def show_update_notification() -> None:
    """Display cached update notification if available.

    Shows notification from cache without re-checking.
    Safe to call even if checker not initialized.
    """
    global _update_checker
    if _update_checker is not None:
        _update_checker.show_notification()


def force_update_check(
    package_name: Optional[str] = None,
    current_version: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[bool, Optional[str]]:
    """Force an immediate update check (synchronous).

    Args:
        package_name: Package name (required if not already initialized)
        current_version: Current version (required if not already initialized)
        **kwargs: Additional arguments for UpdateChecker initialization

    Returns:
        Tuple of (has_update, latest_version)
    """
    try:
        checker = get_update_checker(package_name, current_version, **kwargs)
        return checker.force_check()
    except ValueError:
        return (False, None)


def reset_update_checker() -> None:
    """Reset the global update checker instance.

    Useful for testing or when switching between different packages.
    """
    global _update_checker
    _update_checker = None
