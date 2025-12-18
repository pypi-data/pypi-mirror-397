"""Main update checker orchestrator."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..detectors.install_detector import InstallDetector
from ..notifiers.base import Notifier
from ..notifiers.simple import SimpleNotifier
from ..sources.base import VersionSource
from ..sources.pypi import PyPISource
from ..utils.async_utils import create_async_task
from ..utils.env_utils import should_skip_update_check
from .cache_manager import CacheManager
from .version_compare import is_newer_version

try:
    from ..notifiers.rich import RichNotifier, RICH_AVAILABLE
except ImportError:
    RICH_AVAILABLE = False


class UpdateChecker:
    """Main update checker orchestrator.

    Coordinates version sources, cache, installation detection,
    and notifications to provide a complete update checking system.
    """

    def __init__(
        self,
        package_name: str,
        current_version: str,
        sources: Optional[List[VersionSource]] = None,
        cache_dir: Optional[Path] = None,
        check_interval_hours: int = 24,
        notifier: Optional[Notifier] = None,
        plugins: Optional[List[Any]] = None,
        env_vars: Optional[List[str]] = None,
    ):
        """Initialize update checker.

        Args:
            package_name: Name of the package
            current_version: Current installed version
            sources: List of version sources (default: PyPI only)
            cache_dir: Custom cache directory (default: ~/.cache/{package}/updates)
            check_interval_hours: Hours between checks (default: 24)
            notifier: Custom notifier (default: RichNotifier or SimpleNotifier)
            plugins: List of plugins (e.g., ChangelogPlugin)
            env_vars: Package-specific env vars to check for opt-out
        """
        self.package_name = package_name
        self.current_version = current_version

        # Setup sources (default to PyPI)
        if sources is None:
            self.sources = [PyPISource(package_name)]
        else:
            self.sources = sorted(sources, key=lambda s: s.get_priority())

        # Setup cache
        self.cache_manager = CacheManager(
            package_name=package_name,
            cache_dir=cache_dir,
            ttl_hours=check_interval_hours,
        )

        # Setup notifier (prefer Rich if available)
        if notifier is None:
            if RICH_AVAILABLE:
                try:
                    self.notifier = RichNotifier()
                except Exception:
                    self.notifier = SimpleNotifier()
            else:
                self.notifier = SimpleNotifier()
        else:
            self.notifier = notifier

        # Setup plugins
        self.plugins = plugins or []

        # Environment variables for opt-out
        if env_vars is None:
            # Default: {PACKAGE}_NO_UPDATE_CHECK
            normalized_name = package_name.replace("-", "_").upper()
            self.env_vars = [f"{normalized_name}_NO_UPDATE_CHECK"]
        else:
            self.env_vars = env_vars

        # Installation detector
        self.install_detector = InstallDetector(package_name)

        # Cached update info
        self._cached_update_info: Optional[Dict[str, Any]] = None

    def should_check(self) -> bool:
        """Determine if an update check should be performed.

        Checks environment variables and cache TTL.

        Returns:
            True if check should be performed, False otherwise
        """
        # Check environment variables
        if should_skip_update_check(self.env_vars):
            return False

        # Check cache TTL
        return self.cache_manager.should_check()

    def check_async(self, force: bool = False) -> None:
        """Check for updates in background thread (non-blocking).

        Args:
            force: Force check even if cache is fresh
        """
        if not force and not self.should_check():
            return

        # Run check in background thread
        create_async_task(lambda: self._perform_check_async(), timeout=30.0)

    async def _perform_check_async(self) -> None:
        """Async implementation of update check."""
        self._perform_check()

    def check_sync(self, force: bool = False) -> Optional[Dict[str, Any]]:
        """Check for updates synchronously (blocking).

        Args:
            force: Force check even if cache is fresh

        Returns:
            Update info dict if update available, None otherwise
        """
        if not force and not self.should_check():
            cached = self.cache_manager.get_cached_update_info()
            if cached and cached.get("update_available"):
                return cached
            return None

        return self._perform_check()

    def _perform_check(self) -> Optional[Dict[str, Any]]:
        """Perform the actual update check.

        Implements Homebrew-first strategy: if installed via Homebrew,
        check Homebrew source first before falling back to other sources.

        Returns:
            Update info dict if update available, None otherwise
        """
        # Get installation info for smart source prioritization
        install_info = self.install_detector.detect()

        # Smart source ordering: if Homebrew install, prioritize Homebrew source
        sources = self.sources[:]
        if install_info.method == "homebrew":
            # Move Homebrew sources to front
            homebrew_sources = [s for s in sources if s.name == "homebrew"]
            other_sources = [s for s in sources if s.name != "homebrew"]
            sources = homebrew_sources + other_sources
        else:
            # Standard priority order
            sources = sorted(sources, key=lambda s: s.get_priority())

        # Try each source in priority order
        latest_version = None
        source_name = None

        for source in sources:
            try:
                version = source.fetch_latest_version()
                if version:
                    latest_version = version
                    source_name = source.name
                    break
            except Exception:
                # Silent failure, try next source
                continue

        if not latest_version:
            # No version found, cache negative result
            self._cache_result(None, None, False)
            return None

        # Check if newer
        update_available = is_newer_version(self.current_version, latest_version)

        # Get installation info
        install_info = self.install_detector.detect()

        # Build update info
        update_info = {
            "package_name": self.package_name,
            "current_version": self.current_version,
            "latest_version": latest_version,
            "update_available": update_available,
            "source": source_name,
            "install_method": install_info.friendly_name,
            "upgrade_command": install_info.upgrade_command,
            "release_url": self._get_release_url(latest_version),
        }

        # Apply plugins
        for plugin in self.plugins:
            try:
                update_info = plugin.enhance(update_info)
            except Exception:
                # Silent failure - plugins shouldn't break update checking
                pass

        # Cache result
        self._cache_result(latest_version, source_name, update_available, update_info)

        # Store for show_notification
        if update_available:
            self._cached_update_info = update_info
            return update_info
        else:
            self._cached_update_info = None
            return None

    def _cache_result(
        self,
        latest_version: Optional[str],
        source: Optional[str],
        update_available: bool,
        update_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Cache the check result.

        Args:
            latest_version: Latest version found
            source: Source name that provided the version
            update_available: Whether an update is available
            update_info: Full update info dict (optional)
        """
        cache_data = {
            "last_check": datetime.now().isoformat(),
            "current_version": self.current_version,
            "latest_version": latest_version,
            "update_available": update_available,
            "source": source,
        }

        # Add additional info if available
        if update_info:
            cache_data.update(update_info)

        self.cache_manager.save(cache_data)

    def _get_release_url(self, version: str) -> str:
        """Get GitHub release URL for version.

        Args:
            version: Version string

        Returns:
            GitHub release URL
        """
        # Normalize package name for GitHub (replace _ with -)
        github_name = self.package_name.replace("_", "-")
        return f"https://github.com/HenriquesLab/{github_name}/releases/tag/v{version}"

    def show_notification(self) -> None:
        """Display update notification if available.

        Shows cached notification without re-checking.
        """
        # Check if we have cached update info
        if self._cached_update_info:
            update_info = self._cached_update_info
        else:
            # Try to load from cache
            cached = self.cache_manager.get_cached_update_info()
            if cached and cached.get("update_available"):
                update_info = cached
            else:
                # No update available
                return

        # Display notification
        try:
            self.notifier.notify(update_info)
        except Exception:
            # Silent failure - notification errors shouldn't disrupt the app
            pass

    def force_check(self) -> tuple[bool, Optional[str]]:
        """Force an immediate update check.

        Returns:
            Tuple of (has_update, latest_version)
        """
        update_info = self.check_sync(force=True)
        if update_info:
            return (True, update_info.get("latest_version"))
        else:
            return (False, None)

    def get_install_info(self):
        """Get installation information.

        Returns:
            InstallInfo object with method, friendly name, and upgrade command
        """
        return self.install_detector.detect()
