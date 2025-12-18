"""henriqueslab-updater: Centralized update checking for HenriquesLab packages.

This package provides a unified update checking system that supports multiple
installation methods (Homebrew, pipx, uv, pip) and version sources (PyPI, Homebrew).

## Quick Start

```python
from henriqueslab_updater import UpdateChecker

# Simple usage
checker = UpdateChecker("my-package", "1.0.0")
checker.check_async()
# ... later
checker.show_notification()
```

## Convenience Functions

```python
from henriqueslab_updater import (
    check_for_updates_async_background,
    show_update_notification,
)

# Background check
check_for_updates_async_background("my-package", "1.0.0")

# Show notification
show_update_notification()
```
"""

from .__version__ import __version__
from .core.update_checker import UpdateChecker
from .notifiers.simple import SimpleNotifier
from .plugins.changelog import ChangelogPlugin

# Convenience functions (singleton pattern)
from .convenience import (
    check_for_updates_async_background,
    force_update_check,
    get_update_checker,
    show_update_notification,
)

# Try to import Rich notifier (optional dependency)
try:
    from .notifiers.rich import RichNotifier
except ImportError:
    RichNotifier = None  # type: ignore

# Version sources
from .sources.pypi import PyPISource
from .sources.homebrew import HomebrewSource

# Upgrade utilities
from .utils import execute_upgrade, execute_upgrade_raise, UpgradeError

__all__ = [
    # Version
    "__version__",
    # Main class
    "UpdateChecker",
    # Convenience functions
    "check_for_updates_async_background",
    "show_update_notification",
    "force_update_check",
    "get_update_checker",
    # Notifiers
    "SimpleNotifier",
    "RichNotifier",
    # Plugins
    "ChangelogPlugin",
    # Sources
    "PyPISource",
    "HomebrewSource",
    # Upgrade utilities
    "execute_upgrade",
    "execute_upgrade_raise",
    "UpgradeError",
]
