"""Cache management for update checks."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


class CacheManager:
    """Manages update check cache with TTL support."""

    def __init__(
        self,
        package_name: str,
        cache_dir: Optional[Path] = None,
        ttl_hours: int = 24,
    ):
        """Initialize the cache manager.

        Args:
            package_name: Name of the package (used for default cache dir)
            cache_dir: Custom cache directory (default: ~/.cache/{package}/updates)
            ttl_hours: Time-to-live for cache entries in hours (default: 24)
        """
        self.package_name = package_name
        self.ttl = timedelta(hours=ttl_hours)

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".cache" / package_name / "updates"

        self.cache_file = self.cache_dir / "update_check.json"

    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Silent failure - cache is optional
            pass

    def load(self) -> Optional[Dict[str, Any]]:
        """Load cached update check data.

        Returns:
            Cached data dict, or None if cache doesn't exist or is invalid
        """
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else None
        except (json.JSONDecodeError, OSError):
            return None

    def save(self, data: Dict[str, Any]) -> None:
        """Save update check data to cache.

        Args:
            data: Dictionary to cache
        """
        self._ensure_cache_dir()
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            # Silent failure - cache is optional
            pass

    def should_check(self) -> bool:
        """Determine if an update check should be performed based on cache TTL.

        Returns:
            True if cache is stale or doesn't exist, False if cache is fresh
        """
        cache_data = self.load()
        if not cache_data:
            return True

        last_check = cache_data.get("last_check")
        if not last_check:
            return True

        try:
            last_check_time = datetime.fromisoformat(last_check)
            time_since_check = datetime.now() - last_check_time
            return time_since_check > self.ttl
        except (ValueError, TypeError):
            # Invalid timestamp, should check
            return True

    def get_cached_update_info(self, current_version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached update information if available and valid.

        Args:
            current_version: Current package version to validate cache against

        Returns:
            Cached update info if available and valid, None otherwise
        """
        if not self.should_check():
            cached_data = self.load()

            # Invalidate cache if current version has changed
            if cached_data and current_version:
                cached_current = cached_data.get("current_version")
                if cached_current and cached_current != current_version:
                    # Version changed, cache is stale
                    return None

            return cached_data
        return None

    def clear(self) -> None:
        """Clear the cache file."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except OSError:
            # Silent failure
            pass
