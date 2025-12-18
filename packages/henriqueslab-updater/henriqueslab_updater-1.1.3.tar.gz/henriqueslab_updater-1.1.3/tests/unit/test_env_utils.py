"""Unit tests for environment utilities."""

import os
from unittest.mock import patch

import pytest
from henriqueslab_updater.utils.env_utils import (
    should_skip_update_check,
    is_ci_environment,
)


class TestEnvUtils:
    """Test environment variable utilities."""

    def test_should_skip_default(self):
        """Test default behavior when no env vars set."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove any existing env vars
            for key in ["NO_UPDATE_NOTIFIER", "CI"]:
                os.environ.pop(key, None)

            assert should_skip_update_check() is False

    def test_should_skip_no_update_notifier(self):
        """Test NO_UPDATE_NOTIFIER set."""
        with patch.dict(os.environ, {"NO_UPDATE_NOTIFIER": "1"}):
            assert should_skip_update_check() is True

    def test_should_skip_no_update_notifier_empty(self):
        """Test NO_UPDATE_NOTIFIER empty."""
        with patch.dict(os.environ, {"NO_UPDATE_NOTIFIER": ""}):
            assert should_skip_update_check() is False

    def test_should_skip_with_package_vars_1(self):
        """Test with package-specific var set to 1."""
        with patch.dict(os.environ, {"RXIV_NO_UPDATE_CHECK": "1"}):
            assert (
                should_skip_update_check(
                    package_specific_vars=["RXIV_NO_UPDATE_CHECK"]
                )
                is True
            )

    def test_should_skip_with_package_vars_true(self):
        """Test with package-specific var set to true."""
        with patch.dict(os.environ, {"TASKREPO_NO_UPDATE_CHECK": "true"}):
            assert (
                should_skip_update_check(
                    package_specific_vars=["TASKREPO_NO_UPDATE_CHECK"]
                )
                is True
            )

    def test_should_skip_with_package_vars_yes(self):
        """Test with package-specific var set to yes."""
        with patch.dict(os.environ, {"MY_PKG_NO_UPDATE": "yes"}):
            assert (
                should_skip_update_check(
                    package_specific_vars=["MY_PKG_NO_UPDATE"]
                )
                is True
            )

    def test_should_skip_with_package_vars_false(self):
        """Test with package-specific var set to false."""
        with patch.dict(os.environ, {"PKG_VAR": "false"}):
            assert (
                should_skip_update_check(package_specific_vars=["PKG_VAR"])
                is False
            )

    def test_should_skip_with_multiple_package_vars(self):
        """Test with multiple package-specific vars."""
        with patch.dict(os.environ, {"VAR1": "0", "VAR2": "1"}):
            # VAR2 is set, so should skip
            assert (
                should_skip_update_check(package_specific_vars=["VAR1", "VAR2"])
                is True
            )

    def test_should_skip_with_package_vars_none_set(self):
        """Test with package vars when none are set."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MY_VAR", None)
            assert (
                should_skip_update_check(package_specific_vars=["MY_VAR"])
                is False
            )

    def test_should_skip_case_insensitive(self):
        """Test that checks are case-insensitive."""
        with patch.dict(os.environ, {"PKG_VAR": "True"}):
            assert (
                should_skip_update_check(package_specific_vars=["PKG_VAR"])
                is True
            )

        with patch.dict(os.environ, {"PKG_VAR": "TRUE"}):
            assert (
                should_skip_update_check(package_specific_vars=["PKG_VAR"])
                is True
            )

        with patch.dict(os.environ, {"PKG_VAR": "YES"}):
            assert (
                should_skip_update_check(package_specific_vars=["PKG_VAR"])
                is True
            )

    def test_is_ci_environment_not_ci(self):
        """Test is_ci_environment when not in CI."""
        with patch.dict(os.environ, {}, clear=False):
            for var in ["CI", "CONTINUOUS_INTEGRATION", "GITHUB_ACTIONS", "TRAVIS", "CIRCLECI"]:
                os.environ.pop(var, None)
            assert is_ci_environment() is False

    def test_is_ci_environment_ci(self):
        """Test is_ci_environment with CI=true."""
        with patch.dict(os.environ, {"CI": "true"}):
            assert is_ci_environment() is True

    def test_is_ci_environment_github_actions(self):
        """Test is_ci_environment with GITHUB_ACTIONS."""
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            assert is_ci_environment() is True

    def test_is_ci_environment_travis(self):
        """Test is_ci_environment with TRAVIS."""
        with patch.dict(os.environ, {"TRAVIS": "true"}):
            assert is_ci_environment() is True

    def test_is_ci_environment_circleci(self):
        """Test is_ci_environment with CIRCLECI."""
        with patch.dict(os.environ, {"CIRCLECI": "true"}):
            assert is_ci_environment() is True
