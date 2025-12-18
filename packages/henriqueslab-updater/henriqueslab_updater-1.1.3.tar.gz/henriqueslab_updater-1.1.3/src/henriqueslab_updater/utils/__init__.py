"""Utility functions for henriqueslab-updater."""

from .upgrade_executor import UpgradeError, execute_upgrade, execute_upgrade_raise

__all__ = [
    "execute_upgrade",
    "execute_upgrade_raise",
    "UpgradeError",
]
