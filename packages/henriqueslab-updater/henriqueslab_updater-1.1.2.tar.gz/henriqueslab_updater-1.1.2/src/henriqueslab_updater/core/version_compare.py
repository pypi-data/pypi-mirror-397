"""Version comparison utilities using semantic versioning."""

from typing import Optional

try:
    from packaging.version import Version, parse
    PACKAGING_AVAILABLE = True
except ImportError:
    PACKAGING_AVAILABLE = False


def normalize_version(version: str) -> tuple:
    """Normalize a version string for comparison.

    Strips development/build suffixes and converts to comparable tuple.

    Args:
        version: Version string like "1.2.3" or "1.2.3.dev4+g909680c"

    Returns:
        Tuple of version parts for comparison
    """
    # Remove common suffixes
    clean_version = (
        version.split(".dev")[0]
        .split("+")[0]
        .split("-dev")[0]
        .split("-rc")[0]
        .split("-alpha")[0]
        .split("-beta")[0]
    )

    try:
        parts: list[int | str] = []
        for part in clean_version.split("."):
            try:
                parts.append(int(part))
            except ValueError:
                # Handle non-numeric parts
                parts.append(part)
        return tuple(parts)
    except Exception:
        # Fallback to string comparison
        return (clean_version,)


def is_newer_version(current: str, latest: str) -> bool:
    """Check if latest version is newer than current version.

    Uses packaging.version if available, falls back to custom comparison.
    Dev versions are NOT considered newer than release versions.

    Args:
        current: Current version string
        latest: Latest version string to compare against

    Returns:
        True if latest is newer than current, False otherwise
    """
    # Handle unknown versions
    if current == "unknown" or latest == "unknown":
        return False

    # Don't consider dev/pre-release versions as "newer"
    if any(x in latest.lower() for x in ['.dev', '-dev', '-rc', '-alpha', '-beta', '+g']):
        return False

    if PACKAGING_AVAILABLE:
        try:
            from packaging.version import InvalidVersion

            try:
                current_parsed = parse(current)
                latest_parsed = parse(latest)
                # Only consider it newer if latest is not a pre-release
                if latest_parsed.is_prerelease or latest_parsed.is_devrelease:
                    return False
                return latest_parsed > current_parsed
            except InvalidVersion:
                # Fall through to manual comparison
                pass
        except Exception:
            pass  # Fall through to manual comparison

    # Manual comparison using normalization
    try:
        current_normalized = normalize_version(current)
        latest_normalized = normalize_version(latest)

        # Check if versions have numeric parts
        current_has_numbers = any(isinstance(part, int) for part in current_normalized)
        latest_has_numbers = any(isinstance(part, int) for part in latest_normalized)

        # If latest has no numbers but current does, invalid
        if current_has_numbers and not latest_has_numbers:
            return False

        # If current has no numbers but latest does, latest is newer
        if not current_has_numbers and latest_has_numbers:
            return True

        # Element-wise comparison
        max_length = max(len(current_normalized), len(latest_normalized))

        for i in range(max_length):
            current_part = current_normalized[i] if i < len(current_normalized) else 0
            latest_part = latest_normalized[i] if i < len(latest_normalized) else 0

            # Compare same types
            if isinstance(current_part, int) and isinstance(latest_part, int):
                if latest_part > current_part:
                    return True
                if latest_part < current_part:
                    return False
            else:
                # Convert to string for comparison
                current_str = str(current_part)
                latest_str = str(latest_part)
                if latest_str > current_str:
                    return True
                if latest_str < current_str:
                    return False

        # All equal, not newer
        return False
    except Exception:
        # If comparison fails, assume not newer
        return False


def format_version_comparison(current: str, latest: str) -> str:
    """Format a version comparison string.

    Args:
        current: Current version
        latest: Latest version

    Returns:
        Formatted string like "v1.0.0 → v1.1.0"
    """
    return f"v{current} → v{latest}"
