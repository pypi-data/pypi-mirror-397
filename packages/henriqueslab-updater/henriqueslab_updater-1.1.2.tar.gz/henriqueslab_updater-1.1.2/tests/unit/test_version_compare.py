"""Unit tests for version comparison utilities."""

import pytest
from henriqueslab_updater.core.version_compare import (
    normalize_version,
    is_newer_version,
    format_version_comparison,
)


class TestNormalizeVersion:
    """Test version normalization."""

    def test_simple_version(self):
        """Test simple version string."""
        assert normalize_version("1.2.3") == (1, 2, 3)

    def test_version_with_dev_suffix(self):
        """Test version with .dev suffix."""
        result = normalize_version("1.2.3.dev4")
        assert result == (1, 2, 3)

    def test_version_with_build_suffix(self):
        """Test version with +build suffix."""
        result = normalize_version("1.2.3+g909680c")
        assert result == (1, 2, 3)

    def test_version_with_multiple_suffixes(self):
        """Test version with multiple suffixes."""
        result = normalize_version("1.2.3.dev4+g909680c.d20250716")
        assert result == (1, 2, 3)

    def test_version_with_rc(self):
        """Test version with -rc suffix."""
        result = normalize_version("1.2.3-rc1")
        assert result == (1, 2, 3)

    def test_version_with_alpha(self):
        """Test version with -alpha suffix."""
        result = normalize_version("1.2.3-alpha")
        assert result == (1, 2, 3)

    def test_invalid_version(self):
        """Test invalid version string."""
        result = normalize_version("invalid")
        assert result == ("invalid",)


class TestIsNewerVersion:
    """Test version comparison logic."""

    def test_patch_update(self):
        """Test patch version update."""
        assert is_newer_version("1.0.0", "1.0.1") is True

    def test_minor_update(self):
        """Test minor version update."""
        assert is_newer_version("1.0.0", "1.1.0") is True

    def test_major_update(self):
        """Test major version update."""
        assert is_newer_version("1.0.0", "2.0.0") is True

    def test_same_version(self):
        """Test same version."""
        assert is_newer_version("1.0.0", "1.0.0") is False

    def test_downgrade(self):
        """Test downgrade detection."""
        assert is_newer_version("2.0.0", "1.0.0") is False

    def test_unknown_current(self):
        """Test with unknown current version."""
        assert is_newer_version("unknown", "1.0.0") is False

    def test_unknown_latest(self):
        """Test with unknown latest version."""
        assert is_newer_version("1.0.0", "unknown") is False

    def test_dev_to_release_is_update(self):
        """Test that dev to release is considered an update."""
        assert is_newer_version("1.0.0.dev1", "1.0.0") is True

    def test_dev_not_newer_than_release(self):
        """Test that dev version is not newer than release."""
        assert is_newer_version("1.0.0", "1.0.1.dev1") is False

    def test_rc_not_newer(self):
        """Test that RC version is not newer."""
        assert is_newer_version("1.0.0", "1.0.1-rc1") is False

    def test_alpha_not_newer(self):
        """Test that alpha version is not newer."""
        assert is_newer_version("1.0.0", "1.0.1-alpha") is False

    def test_beta_not_newer(self):
        """Test that beta version is not newer."""
        assert is_newer_version("1.0.0", "1.0.1-beta") is False

    def test_complex_version(self):
        """Test complex version strings."""
        assert is_newer_version("1.0.0", "1.0.10") is True
        assert is_newer_version("1.0.10", "1.0.2") is False


class TestFormatVersionComparison:
    """Test version comparison formatting."""

    def test_format_simple(self):
        """Test simple version comparison format."""
        result = format_version_comparison("1.0.0", "1.1.0")
        assert result == "v1.0.0 → v1.1.0"

    def test_format_with_dev(self):
        """Test formatting with dev versions."""
        result = format_version_comparison("1.0.0.dev1", "1.0.0")
        assert result == "v1.0.0.dev1 → v1.0.0"
