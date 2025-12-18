"""Unit tests for UpdateChecker."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from henriqueslab_updater.core.update_checker import UpdateChecker
from henriqueslab_updater.sources.base import VersionSource
from henriqueslab_updater.notifiers.base import Notifier
from henriqueslab_updater.detectors.install_detector import InstallInfo


class MockVersionSource(VersionSource):
    """Mock version source for testing."""

    def __init__(self, version="1.1.0", priority=100, name="mock"):
        self._version = version
        self._priority = priority
        self._name = name

    def fetch_latest_version(self):
        return self._version

    def get_priority(self):
        return self._priority

    @property
    def name(self):
        return self._name


class MockNotifier(Notifier):
    """Mock notifier for testing."""

    def __init__(self):
        self.messages = []

    def format(self, update_info):
        return f"Update: {update_info.get('package_name')} {update_info.get('latest_version')}"

    def display(self, message):
        self.messages.append(message)

    def notify(self, update_info):
        message = self.format(update_info)
        self.display(message)


class TestUpdateChecker:
    """Test UpdateChecker functionality."""

    def test_initialization_basic(self):
        """Test basic initialization."""
        checker = UpdateChecker("test-package", "1.0.0")

        assert checker.package_name == "test-package"
        assert checker.current_version == "1.0.0"
        assert len(checker.sources) > 0

    def test_initialization_custom_cache_dir(self):
        """Test initialization with custom cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = UpdateChecker(
                "test-package", "1.0.0", cache_dir=Path(tmpdir)
            )

            assert checker.cache_manager.cache_dir == Path(tmpdir)

    def test_initialization_custom_sources(self):
        """Test initialization with custom sources."""
        source = MockVersionSource("1.2.0")
        checker = UpdateChecker("test-package", "1.0.0", sources=[source])

        assert len(checker.sources) == 1
        assert checker.sources[0] is source

    def test_initialization_custom_notifier(self):
        """Test initialization with custom notifier."""
        notifier = MockNotifier()
        checker = UpdateChecker("test-package", "1.0.0", notifier=notifier)

        assert checker.notifier is notifier

    def test_should_check_with_no_cache(self):
        """Test should_check when no cache exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = UpdateChecker(
                "test-package", "1.0.0", cache_dir=Path(tmpdir)
            )
            # No cache exists, should check
            assert checker.should_check() is True

    def test_should_check_env_var_disable(self):
        """Test should_check with environment variable."""
        with patch.dict("os.environ", {"NO_UPDATE_NOTIFIER": "1"}):
            checker = UpdateChecker("test-package", "1.0.0")
            assert checker.should_check() is False

    def test_should_check_with_fresh_cache(self):
        """Test should_check with fresh cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = UpdateChecker(
                "test-package", "1.0.0", cache_dir=Path(tmpdir)
            )

            # Save fresh cache
            recent_time = datetime.now() - timedelta(hours=1)
            checker.cache_manager.save({"last_check": recent_time.isoformat()})

            assert checker.should_check() is False

    def test_check_sync_update_available(self):
        """Test synchronous check with update available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = MockVersionSource("1.1.0")
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[source],
                cache_dir=Path(tmpdir),
            )

            result = checker.check_sync()

            assert result is not None
            assert result["update_available"] is True
            assert result["latest_version"] == "1.1.0"
            assert result["current_version"] == "1.0.0"

    def test_check_sync_no_update_available(self):
        """Test synchronous check with no update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = MockVersionSource("1.0.0")
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[source],
                cache_dir=Path(tmpdir),
            )

            result = checker.check_sync()

            # No update available, returns None
            assert result is None

    def test_check_sync_force_ignores_cache(self):
        """Test check_sync with force=True ignores cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = MockVersionSource("1.1.0")
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[source],
                cache_dir=Path(tmpdir),
            )

            # Save fresh cache
            recent_time = datetime.now() - timedelta(hours=1)
            checker.cache_manager.save({
                "last_check": recent_time.isoformat(),
                "latest_version": "0.9.0",
            })

            # Force should ignore cache
            result = checker.check_sync(force=True)

            assert result is not None
            assert result["latest_version"] == "1.1.0"  # From source, not cache

    def test_check_sync_source_priority(self):
        """Test that sources are checked in priority order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            high_priority = MockVersionSource("1.2.0", priority=10)
            low_priority = MockVersionSource("1.1.0", priority=100)

            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[low_priority, high_priority],  # Wrong order
                cache_dir=Path(tmpdir),
            )

            result = checker.check_sync()

            # Should use high priority source
            assert result["latest_version"] == "1.2.0"
            assert result["source"] == "mock"

    def test_check_sync_homebrew_first_for_brew_install(self):
        """Test Homebrew source prioritization for Homebrew installs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sources
            pypi_source = MockVersionSource("1.2.0", priority=100, name="pypi")
            brew_source = MockVersionSource("1.1.0", priority=10, name="homebrew")

            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[pypi_source, brew_source],
                cache_dir=Path(tmpdir),
            )

            # Mock install detector to return Homebrew
            with patch.object(
                checker.install_detector,
                "detect",
                return_value=InstallInfo(
                    method="homebrew",
                    friendly_name="Homebrew",
                    upgrade_command="brew upgrade test-package",
                    executable_path="/opt/homebrew/bin/python",
                ),
            ):
                result = checker.check_sync()

                # Should use Homebrew source first
                assert result["source"] == "homebrew"

    def test_check_sync_source_failure_fallback(self):
        """Test fallback to next source on failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            failing_source = MockVersionSource(None, priority=10)
            working_source = MockVersionSource("1.1.0", priority=100)

            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[failing_source, working_source],
                cache_dir=Path(tmpdir),
            )

            result = checker.check_sync()

            assert result is not None
            assert result["latest_version"] == "1.1.0"

    def test_check_async_background(self):
        """Test asynchronous background check."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            source = MockVersionSource("1.1.0")
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[source],
                cache_dir=Path(tmpdir),
            )

            # Should return immediately
            checker.check_async()

            # Check should complete in background
            time.sleep(0.5)

            # Cache should be updated
            cached = checker.cache_manager.load()
            assert cached is not None
            assert cached["latest_version"] == "1.1.0"

    def test_show_notification_no_update(self):
        """Test show_notification with no update."""
        notifier = MockNotifier()
        checker = UpdateChecker("test-package", "1.0.0", notifier=notifier)
        checker._cached_update_info = None

        checker.show_notification()

        # Should not display anything
        assert len(notifier.messages) == 0

    def test_show_notification_with_update(self):
        """Test show_notification with update available."""
        notifier = MockNotifier()
        checker = UpdateChecker("test-package", "1.0.0", notifier=notifier)
        checker._cached_update_info = {
            "package_name": "test-package",
            "update_available": True,
            "latest_version": "1.1.0",
            "current_version": "1.0.0",
        }

        checker.show_notification()

        # Should display notification
        assert len(notifier.messages) == 1
        assert "test-package" in notifier.messages[0]
        assert "1.1.0" in notifier.messages[0]

    def test_get_install_info(self):
        """Test get_install_info."""
        checker = UpdateChecker("test-package", "1.0.0")
        info = checker.get_install_info()

        assert isinstance(info, InstallInfo)
        assert info.method is not None

    def test_force_check(self):
        """Test force_check method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = MockVersionSource("1.1.0")
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[source],
                cache_dir=Path(tmpdir),
            )

            has_update, latest_version = checker.force_check()

            assert has_update is True
            assert latest_version == "1.1.0"

    def test_force_check_no_update(self):
        """Test force_check with no update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = MockVersionSource("1.0.0")
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[source],
                cache_dir=Path(tmpdir),
            )

            has_update, latest_version = checker.force_check()

            assert has_update is False
            assert latest_version is None

    def test_multiple_sources_all_fail(self):
        """Test when all sources fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            failing1 = MockVersionSource(None, priority=10)
            failing2 = MockVersionSource(None, priority=20)

            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[failing1, failing2],
                cache_dir=Path(tmpdir),
            )

            result = checker.check_sync()

            # Should return None when all sources fail
            assert result is None

    def test_check_interval_hours(self):
        """Test custom check interval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                check_interval_hours=48,
                cache_dir=Path(tmpdir),
            )

            # Save cache from 36 hours ago
            old_time = datetime.now() - timedelta(hours=36)
            checker.cache_manager.save({"last_check": old_time.isoformat()})

            # With 48h interval, should not check yet
            assert checker.should_check() is False

            # Save cache from 50 hours ago
            older_time = datetime.now() - timedelta(hours=50)
            checker.cache_manager.save({"last_check": older_time.isoformat()})

            # Now should check
            assert checker.should_check() is True

    def test_env_vars_custom(self):
        """Test custom environment variables."""
        with patch.dict("os.environ", {"MY_PKG_NO_UPDATE": "1"}):
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                env_vars=["MY_PKG_NO_UPDATE"],
            )

            assert checker.should_check() is False

    def test_cache_stores_update_info(self):
        """Test that update info is cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = MockVersionSource("1.1.0")
            checker = UpdateChecker(
                "test-package",
                "1.0.0",
                sources=[source],
                cache_dir=Path(tmpdir),
            )

            result = checker.check_sync()

            # Load from cache
            cached = checker.cache_manager.load()

            assert cached is not None
            assert cached["latest_version"] == "1.1.0"
            assert cached["update_available"] is True
