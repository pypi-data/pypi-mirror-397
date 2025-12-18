"""Unit tests for notifiers."""

from unittest.mock import patch, MagicMock

import pytest
from henriqueslab_updater.notifiers.simple import SimpleNotifier
from henriqueslab_updater.notifiers.rich import RichNotifier, RICH_AVAILABLE


class TestSimpleNotifier:
    """Test simple text notifier."""

    def test_initialization(self):
        """Test notifier initialization."""
        notifier = SimpleNotifier()
        assert notifier.title == "Update Available"

    def test_initialization_custom_title(self):
        """Test initialization with custom title."""
        notifier = SimpleNotifier(title="New Version")
        assert notifier.title == "New Version"

    def test_format_basic(self):
        """Test basic message formatting."""
        notifier = SimpleNotifier()
        update_info = {
            "package_name": "test-package",
            "current_version": "1.0.0",
            "latest_version": "1.1.0",
            "install_method": "pip",
            "upgrade_command": "pip install --upgrade test-package",
        }

        message = notifier.format(update_info)

        assert "test-package" in message
        assert "v1.0.0 → v1.1.0" in message
        assert "pip" in message
        assert "pip install --upgrade test-package" in message

    def test_format_with_release_url(self):
        """Test formatting with release URL."""
        notifier = SimpleNotifier()
        update_info = {
            "package_name": "test-package",
            "current_version": "1.0.0",
            "latest_version": "1.1.0",
            "install_method": "Homebrew",
            "upgrade_command": "brew upgrade test-package",
            "release_url": "https://github.com/test/repo/releases/tag/v1.1.0",
        }

        message = notifier.format(update_info)

        assert "https://github.com/test/repo/releases/tag/v1.1.0" in message
        assert "Release notes" in message

    def test_format_with_changelog(self):
        """Test formatting with changelog summary."""
        notifier = SimpleNotifier()
        update_info = {
            "package_name": "test-package",
            "current_version": "1.0.0",
            "latest_version": "1.1.0",
            "install_method": "pip",
            "upgrade_command": "pip install --upgrade test-package",
            "changelog_summary": "✨ New features:\n  - Feature 1\n  - Feature 2",
        }

        message = notifier.format(update_info)

        assert "✨ New features" in message
        assert "Feature 1" in message

    @patch("builtins.print")
    def test_display(self, mock_print):
        """Test message display."""
        notifier = SimpleNotifier()
        notifier.display("Test message")

        mock_print.assert_called_once_with("Test message", flush=True)

    @patch("builtins.print")
    def test_notify(self, mock_print):
        """Test complete notify flow."""
        notifier = SimpleNotifier()
        update_info = {
            "package_name": "test-package",
            "current_version": "1.0.0",
            "latest_version": "1.1.0",
            "install_method": "pip",
            "upgrade_command": "pip install --upgrade test-package",
        }

        notifier.notify(update_info)

        # Should have called print with formatted message
        assert mock_print.called
        call_args = mock_print.call_args[0][0]
        assert "test-package" in call_args


class TestRichNotifier:
    """Test Rich notifier."""

    def test_initialization(self):
        """Test notifier initialization."""
        notifier = RichNotifier()
        assert notifier.title == "Update Available"
        assert notifier.color_scheme == "bright_blue"

    def test_initialization_custom(self):
        """Test initialization with custom settings."""
        notifier = RichNotifier(title="New Version", color_scheme="green")
        assert notifier.title == "New Version"
        assert notifier.color_scheme == "green"

    def test_format_basic(self):
        """Test basic message formatting."""
        notifier = RichNotifier()
        update_info = {
            "package_name": "test-package",
            "current_version": "1.0.0",
            "latest_version": "1.1.0",
            "install_method": "Homebrew",
            "upgrade_command": "brew upgrade test-package",
        }

        message = notifier.format(update_info)

        # Should contain package name
        assert "test-package" in message

    def test_format_with_changelog(self):
        """Test formatting with changelog."""
        notifier = RichNotifier()
        update_info = {
            "package_name": "test-package",
            "current_version": "1.0.0",
            "latest_version": "1.1.0",
            "install_method": "pip",
            "upgrade_command": "pip install --upgrade test-package",
            "changelog_summary": "✨ What's New:\n  - Feature 1",
        }

        message = notifier.format(update_info)

        assert "What's New" in message
        assert "Feature 1" in message

    @pytest.mark.skipif(not RICH_AVAILABLE, reason="Rich not installed")
    def test_display_with_rich(self):
        """Test display with Rich available."""
        notifier = RichNotifier()

        # Mock the console
        with patch.object(notifier, "console") as mock_console:
            notifier.display("Test message")

            # Should call console.print twice (blank line + panel)
            assert mock_console.print.call_count == 2

    @patch("henriqueslab_updater.notifiers.rich.RICH_AVAILABLE", False)
    @patch("builtins.print")
    def test_display_without_rich(self, mock_print):
        """Test display fallback when Rich not available."""
        notifier = RichNotifier()
        notifier.console = None  # Simulate Rich not available

        notifier.display("Test message")

        mock_print.assert_called_once_with("Test message", flush=True)

    def test_format_plain_fallback(self):
        """Test plain text formatting fallback."""
        notifier = RichNotifier()
        update_info = {
            "package_name": "test-package",
            "current_version": "1.0.0",
            "latest_version": "1.1.0",
            "install_method": "pip",
            "upgrade_command": "pip install --upgrade test-package",
        }

        # Call the private fallback method
        message = notifier._format_plain(update_info)

        assert "test-package" in message
        assert "v1.0.0 → v1.1.0" in message
        assert "pip" in message

    @patch("henriqueslab_updater.notifiers.rich.Panel")
    def test_display_exception_fallback(self, mock_panel):
        """Test display falls back to print on exception."""
        mock_panel.side_effect = Exception("Panel creation failed")

        notifier = RichNotifier()

        with patch("builtins.print") as mock_print:
            if notifier.console is not None:
                notifier.display("Test message")
                # Should fall back to print on exception
                mock_print.assert_called_once()
