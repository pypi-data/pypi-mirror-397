"""Unit tests for version sources."""

from unittest.mock import Mock, patch, MagicMock
import json

import pytest
from henriqueslab_updater.sources.pypi import PyPISource, HTTPX_AVAILABLE
from henriqueslab_updater.sources.homebrew import HomebrewSource
from henriqueslab_updater.sources.github import parse_formula_version


class TestPyPISource:
    """Test PyPI version source."""

    def test_initialization(self):
        """Test PyPI source initialization."""
        source = PyPISource("test-package")

        assert source.package_name == "test-package"
        assert "test-package" in source.pypi_url
        assert source.timeout == 5
        assert source.get_priority() == 100

    def test_initialization_custom_url(self):
        """Test initialization with custom URL."""
        source = PyPISource("test-package", pypi_url="https://custom.pypi.org/json")

        assert source.pypi_url == "https://custom.pypi.org/json"

    def test_initialization_custom_timeout(self):
        """Test initialization with custom timeout."""
        source = PyPISource("test-package", timeout=10)

        assert source.timeout == 10

    @patch("henriqueslab_updater.sources.pypi.urlopen")
    def test_fetch_with_urllib_success(self, mock_urlopen):
        """Test successful fetch with urllib."""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "info": {"version": "1.2.3"}
        }).encode()
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        source = PyPISource("test-package", use_httpx=False)
        version = source.fetch_latest_version()

        assert version == "1.2.3"

    @patch("henriqueslab_updater.sources.pypi.urlopen")
    def test_fetch_with_urllib_failure(self, mock_urlopen):
        """Test fetch failure with urllib."""
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Network error")

        source = PyPISource("test-package", use_httpx=False)
        version = source.fetch_latest_version()

        assert version is None

    @patch("henriqueslab_updater.sources.pypi.urlopen")
    def test_fetch_with_urllib_invalid_json(self, mock_urlopen):
        """Test fetch with invalid JSON."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"invalid json"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        source = PyPISource("test-package", use_httpx=False)
        version = source.fetch_latest_version()

        assert version is None

    @patch("henriqueslab_updater.sources.pypi.urlopen")
    def test_fetch_with_urllib_missing_version(self, mock_urlopen):
        """Test fetch with missing version in response."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "info": {}
        }).encode()
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        source = PyPISource("test-package", use_httpx=False)
        version = source.fetch_latest_version()

        assert version is None

    def test_priority(self):
        """Test source priority."""
        source = PyPISource("test-package")
        assert source.get_priority() == 100

    def test_name_property(self):
        """Test source name property."""
        source = PyPISource("test-package")
        assert source.name == "pypi"


class TestHomebrewSource:
    """Test Homebrew version source."""

    def test_initialization(self):
        """Test Homebrew source initialization."""
        source = HomebrewSource("test-formula")

        assert source.formula_name == "test-formula"
        assert source.tap == "henriqueslab/formulas"
        assert source.timeout == 5
        assert source.get_priority() == 10

    def test_initialization_custom_tap(self):
        """Test initialization with custom tap."""
        source = HomebrewSource("test-formula", tap="custom/tap")

        assert source.tap == "custom/tap"

    def test_initialization_custom_timeout(self):
        """Test initialization with custom timeout."""
        source = HomebrewSource("test-formula", timeout=10)

        assert source.timeout == 10

    @patch("subprocess.run")
    def test_check_brew_outdated_success(self, mock_run):
        """Test successful brew outdated check."""
        # Mock brew outdated output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test-formula (1.0.0) < 1.1.0"
        mock_run.return_value = mock_result

        source = HomebrewSource("test-formula")
        version = source._check_brew_outdated()

        assert version == "1.1.0"

    @patch("subprocess.run")
    def test_check_brew_outdated_up_to_date(self, mock_run):
        """Test brew outdated when package is up to date."""
        mock_result = Mock()
        mock_result.returncode = 1  # Non-zero means up to date
        mock_run.return_value = mock_result

        source = HomebrewSource("test-formula")
        version = source._check_brew_outdated()

        assert version is None

    @patch("subprocess.run")
    def test_check_brew_outdated_not_installed(self, mock_run):
        """Test brew outdated when brew not installed."""
        mock_run.side_effect = FileNotFoundError()

        source = HomebrewSource("test-formula")
        version = source._check_brew_outdated()

        assert version is None

    @patch("subprocess.run")
    def test_check_brew_outdated_timeout(self, mock_run):
        """Test brew outdated timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="brew", timeout=5)

        source = HomebrewSource("test-formula")
        version = source._check_brew_outdated()

        assert version is None

    @patch("henriqueslab_updater.sources.homebrew.parse_formula_version")
    def test_check_formula_github(self, mock_parse):
        """Test GitHub formula check."""
        mock_parse.return_value = "1.2.3"

        source = HomebrewSource("test-formula")
        version = source._check_formula_github()

        assert version == "1.2.3"
        mock_parse.assert_called_once_with("test-formula", timeout=5)

    @patch("subprocess.run")
    @patch("henriqueslab_updater.sources.homebrew.parse_formula_version")
    def test_fetch_latest_version_brew_first(self, mock_parse, mock_run):
        """Test that brew outdated is tried first."""
        # Mock successful brew check
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test-formula (1.0.0) < 1.1.0"
        mock_run.return_value = mock_result

        source = HomebrewSource("test-formula")
        version = source.fetch_latest_version()

        assert version == "1.1.0"
        # Should not call GitHub parser
        mock_parse.assert_not_called()

    @patch("subprocess.run")
    @patch("henriqueslab_updater.sources.homebrew.parse_formula_version")
    def test_fetch_latest_version_fallback_to_github(self, mock_parse, mock_run):
        """Test fallback to GitHub when brew fails."""
        # Mock brew failure
        mock_run.side_effect = FileNotFoundError()
        # Mock GitHub success
        mock_parse.return_value = "1.2.3"

        source = HomebrewSource("test-formula")
        version = source.fetch_latest_version()

        assert version == "1.2.3"
        mock_parse.assert_called_once()

    def test_priority(self):
        """Test source priority."""
        source = HomebrewSource("test-formula")
        assert source.get_priority() == 10

    def test_name_property(self):
        """Test source name property."""
        source = HomebrewSource("test-formula")
        assert source.name == "homebrew"


class TestGitHubFormulaParser:
    """Test GitHub formula parsing."""

    @patch("henriqueslab_updater.sources.github.urlopen")
    def test_parse_formula_with_version_field(self, mock_urlopen):
        """Test parsing formula with explicit version field."""
        formula_content = '''
        class TestFormula < Formula
          desc "Test package"
          version "1.2.3"
          url "https://example.com/test-1.2.3.tar.gz"
        end
        '''

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = formula_content.encode()
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        version = parse_formula_version("test-package")

        assert version == "1.2.3"

    @patch("henriqueslab_updater.sources.github.urlopen")
    def test_parse_formula_from_url(self, mock_urlopen):
        """Test parsing version from URL when no version field."""
        formula_content = '''
        class TestFormula < Formula
          desc "Test package"
          url "https://files.pythonhosted.org/packages/test-package-1.4.5.tar.gz"
        end
        '''

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = formula_content.encode()
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        version = parse_formula_version("test-package")

        assert version == "1.4.5"

    @patch("henriqueslab_updater.sources.github.urlopen")
    def test_parse_formula_with_underscore(self, mock_urlopen):
        """Test parsing formula with underscore in URL."""
        formula_content = '''
        url "https://files.pythonhosted.org/packages/test_package-1.2.3.tar.gz"
        '''

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = formula_content.encode()
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        version = parse_formula_version("test-package")

        assert version == "1.2.3"

    @patch("henriqueslab_updater.sources.github.urlopen")
    def test_parse_formula_network_error(self, mock_urlopen):
        """Test parsing with network error."""
        mock_urlopen.side_effect = Exception("Network error")

        version = parse_formula_version("test-package")

        assert version is None

    @patch("henriqueslab_updater.sources.github.urlopen")
    def test_parse_formula_404(self, mock_urlopen):
        """Test parsing with 404 response."""
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        version = parse_formula_version("test-package")

        assert version is None

    def test_parse_formula_custom_url(self):
        """Test parsing with custom formula URL."""
        with patch("henriqueslab_updater.sources.github.urlopen") as mock_urlopen:
            formula_content = 'version "1.2.3"'

            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.read.return_value = formula_content.encode()
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            version = parse_formula_version(
                "test-package",
                formula_url="https://custom.url/formula.rb"
            )

            assert version == "1.2.3"
            # Verify custom URL was used
            call_args = mock_urlopen.call_args[0][0]
            assert call_args.full_url == "https://custom.url/formula.rb"
