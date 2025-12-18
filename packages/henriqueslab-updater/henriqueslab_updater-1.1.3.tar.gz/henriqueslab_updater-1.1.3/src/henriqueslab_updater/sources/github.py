"""GitHub formula parser for Homebrew formulas."""

import re
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def parse_formula_version(
    package_name: str,
    formula_url: Optional[str] = None,
    timeout: int = 5,
) -> Optional[str]:
    """Parse version from a GitHub Homebrew formula file.

    Args:
        package_name: Package name (e.g., "rxiv-maker")
        formula_url: URL to formula file (default: HenriquesLab tap)
        timeout: Request timeout in seconds

    Returns:
        Version string if found, None otherwise
    """
    if formula_url is None:
        formula_url = (
            f"https://raw.githubusercontent.com/HenriquesLab/homebrew-formulas/"
            f"main/Formula/{package_name}.rb"
        )

    try:
        req = Request(formula_url, headers={"User-Agent": "henriqueslab-updater"})
        with urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                return None

            content = response.read().decode("utf-8")

            # Method 1: Look for explicit version field
            #   version "1.0.0"
            version_match = re.search(r'version\s+"([\d.]+)"', content)
            if version_match:
                return version_match.group(1)

            # Method 2: Extract from URL
            #   url "https://files.pythonhosted.org/.../package-1.0.0.tar.gz"
            # Replace hyphens with both hyphen and underscore patterns
            package_pattern = re.escape(package_name).replace(r"\-", r"[_-]")
            url_pattern = rf'url\s+"[^"]*{package_pattern}[/-]([\d.]+)\.tar\.gz"'
            url_match = re.search(url_pattern, content)
            if url_match:
                return url_match.group(1)

            return None

    except (URLError, HTTPError, TimeoutError, Exception):
        return None
