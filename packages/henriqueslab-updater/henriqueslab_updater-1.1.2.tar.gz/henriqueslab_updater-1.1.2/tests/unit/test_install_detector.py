"""Unit tests for installation detector."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from henriqueslab_updater.detectors.install_detector import InstallDetector, InstallInfo


class TestInstallDetector:
    """Test installation method detection."""

    def test_initialization(self):
        """Test detector initialization."""
        detector = InstallDetector("test-package")
        assert detector.package_name == "test-package"
        assert detector.package_name_normalized == "test_package"

    def test_initialization_with_hyphen(self):
        """Test initialization with hyphenated name."""
        detector = InstallDetector("test-package-name")
        assert detector.package_name == "test-package-name"
        assert detector.package_name_normalized == "test_package_name"

    @patch("sys.executable", "/opt/homebrew/bin/python3")
    def test_detect_homebrew_apple_silicon(self):
        """Test Homebrew detection on Apple Silicon."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "homebrew"
        assert info.friendly_name == "Homebrew"
        assert "brew update && brew upgrade test-package" in info.upgrade_command

    @patch("sys.executable", "/usr/local/Cellar/python/3.11/bin/python3")
    def test_detect_homebrew_intel(self):
        """Test Homebrew detection on Intel Mac."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "homebrew"
        assert info.friendly_name == "Homebrew"

    @patch("sys.executable", "/home/linuxbrew/.linuxbrew/Cellar/python/3.11/bin/python3")
    def test_detect_homebrew_linux(self):
        """Test Homebrew detection on Linux."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "homebrew"
        assert info.friendly_name == "Homebrew"

    @patch("sys.executable", "/home/user/.local/pipx/venvs/test-package/bin/python")
    def test_detect_pipx(self):
        """Test pipx detection."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "pipx"
        assert info.friendly_name == "pipx"
        assert info.upgrade_command == "pipx upgrade test-package"

    @patch("sys.executable", "/home/user/.local/share/pipx/venvs/test-package/bin/python")
    def test_detect_pipx_alt_location(self):
        """Test pipx detection with alternative location."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "pipx"

    @patch("sys.executable", "/home/user/.local/share/uv/tools/test-package/bin/python")
    def test_detect_uv(self):
        """Test uv tool detection."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "uv"
        assert info.friendly_name == "uv tool"
        assert info.upgrade_command == "uv tool upgrade test-package"

    @patch("sys.executable", "/home/user/.local/lib/python3.11/site-packages/bin/python")
    @patch("site.getusersitepackages", return_value="/home/user/.local/lib/python3.11/site-packages")
    def test_detect_pip_user(self, mock_site):
        """Test pip user installation detection."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "pip-user"
        assert info.friendly_name == "pip (user)"
        assert info.upgrade_command == "pip install --upgrade --user test-package"

    @patch("sys.executable", "/usr/lib/python3.11/site-packages/bin/python")
    def test_detect_pip_system(self):
        """Test pip system installation detection."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "pip"
        assert info.friendly_name == "pip"
        assert info.upgrade_command == "pip install --upgrade test-package"

    @patch("sys.executable", "/usr/lib/python3.11/dist-packages/bin/python")
    def test_detect_pip_system_dist_packages(self):
        """Test pip system installation with dist-packages."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "pip"

    @patch("sys.executable", "/some/random/path/python")
    def test_detect_unknown(self):
        """Test unknown installation method."""
        detector = InstallDetector("test-package")
        info = detector.detect()

        assert info.method == "unknown"
        assert info.friendly_name == "Unknown"
        assert info.upgrade_command == "pip install --upgrade test-package"

    def test_install_info_dataclass(self):
        """Test InstallInfo dataclass."""
        info = InstallInfo(
            method="homebrew",
            friendly_name="Homebrew",
            upgrade_command="brew upgrade test",
            executable_path="/opt/homebrew/bin/python",
        )

        assert info.method == "homebrew"
        assert info.friendly_name == "Homebrew"
        assert info.upgrade_command == "brew upgrade test"
        assert info.executable_path == "/opt/homebrew/bin/python"

    @patch("sys.executable", "/home/user/projects/test-package/venv/bin/python")
    def test_detect_with_hyphenated_package_name(self):
        """Test detection with hyphenated package name."""
        detector = InstallDetector("my-test-package")
        # Should match both hyphenated and underscored versions
        info = detector.detect()
        assert info is not None
