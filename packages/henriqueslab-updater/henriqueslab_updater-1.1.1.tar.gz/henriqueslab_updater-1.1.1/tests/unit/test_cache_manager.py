"""Unit tests for cache manager."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from henriqueslab_updater.core.cache_manager import CacheManager


class TestCacheManager:
    """Test cache manager functionality."""

    def test_initialization_default(self):
        """Test default initialization."""
        cache = CacheManager("test-package")
        assert cache.package_name == "test-package"
        assert "test-package" in str(cache.cache_dir)
        assert cache.ttl == timedelta(hours=24)

    def test_initialization_custom_dir(self):
        """Test initialization with custom directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir))
            assert cache.cache_dir == Path(tmpdir)

    def test_initialization_custom_ttl(self):
        """Test initialization with custom TTL."""
        cache = CacheManager("test-package", ttl_hours=48)
        assert cache.ttl == timedelta(hours=48)

    def test_should_check_no_cache(self):
        """Test should_check when no cache exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir))
            assert cache.should_check() is True

    def test_should_check_stale_cache(self):
        """Test should_check when cache is stale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir), ttl_hours=1)

            # Create old cache
            old_time = datetime.now() - timedelta(hours=2)
            cache.save({"last_check": old_time.isoformat()})

            assert cache.should_check() is True

    def test_should_check_fresh_cache(self):
        """Test should_check when cache is fresh."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir), ttl_hours=24)

            # Create recent cache
            recent_time = datetime.now() - timedelta(hours=1)
            cache.save({"last_check": recent_time.isoformat()})

            assert cache.should_check() is False

    def test_load_nonexistent(self):
        """Test loading when cache doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir))
            assert cache.load() is None

    def test_save_and_load(self):
        """Test saving and loading cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir))

            data = {
                "last_check": datetime.now().isoformat(),
                "latest_version": "1.0.0",
                "current_version": "0.9.0",
                "update_available": True,
            }

            cache.save(data)
            loaded = cache.load()

            assert loaded is not None
            assert loaded["latest_version"] == "1.0.0"
            assert loaded["update_available"] is True

    def test_save_creates_directory(self):
        """Test that save creates directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "nested" / "dir"
            cache = CacheManager("test-package", cache_dir=cache_dir)

            cache.save({"test": "data"})

            assert cache_dir.exists()
            assert cache.cache_file.exists()

    def test_load_invalid_json(self):
        """Test loading invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir))

            # Write invalid JSON
            cache.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache.cache_file.write_text("invalid json{")

            assert cache.load() is None

    def test_get_cached_update_info_fresh(self):
        """Test getting cached update info when cache is fresh."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir))

            recent_time = datetime.now() - timedelta(hours=1)
            data = {
                "last_check": recent_time.isoformat(),
                "latest_version": "1.0.0",
                "update_available": True,
            }
            cache.save(data)

            result = cache.get_cached_update_info()
            assert result is not None
            assert result["latest_version"] == "1.0.0"

    def test_get_cached_update_info_stale(self):
        """Test getting cached update info when cache is stale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir), ttl_hours=1)

            old_time = datetime.now() - timedelta(hours=2)
            data = {
                "last_check": old_time.isoformat(),
                "latest_version": "1.0.0",
            }
            cache.save(data)

            result = cache.get_cached_update_info()
            assert result is None

    def test_clear(self):
        """Test clearing cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir))

            cache.save({"test": "data"})
            assert cache.cache_file.exists()

            cache.clear()
            assert not cache.cache_file.exists()

    def test_clear_nonexistent(self):
        """Test clearing when cache doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager("test-package", cache_dir=Path(tmpdir))

            # Should not raise exception
            cache.clear()
