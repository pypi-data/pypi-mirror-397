"""Environment variable handling utilities."""

import os
from typing import List, Optional


def should_skip_update_check(package_specific_vars: Optional[List[str]] = None) -> bool:
    """Check if update checking should be skipped based on environment variables.

    Args:
        package_specific_vars: List of package-specific environment variable names
                              (e.g., ["RXIV_NO_UPDATE_CHECK", "TASKREPO_NO_UPDATE_CHECK"])

    Returns:
        True if update checking should be skipped, False otherwise
    """
    # Check global opt-out
    if os.getenv("NO_UPDATE_NOTIFIER", ""):
        return True

    # Check package-specific opt-outs
    if package_specific_vars:
        for var in package_specific_vars:
            if os.getenv(var, "").lower() in ("1", "true", "yes"):
                return True

    return False


def is_ci_environment() -> bool:
    """Check if running in a CI environment.

    Returns:
        True if running in CI, False otherwise
    """
    ci_vars = ["CI", "CONTINUOUS_INTEGRATION", "GITHUB_ACTIONS", "TRAVIS", "CIRCLECI"]
    return any(os.getenv(var) for var in ci_vars)
