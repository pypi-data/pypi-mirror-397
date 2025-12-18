"""PyPI version source."""

import json
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .base import VersionSource

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class PyPISource(VersionSource):
    """Fetch latest version from PyPI JSON API."""

    def __init__(
        self,
        package_name: str,
        pypi_url: Optional[str] = None,
        timeout: int = 5,
        use_httpx: bool = True,
    ):
        """Initialize PyPI source.

        Args:
            package_name: Package name on PyPI
            pypi_url: Custom PyPI API URL (default: https://pypi.org/pypi/{package}/json)
            timeout: Request timeout in seconds (default: 5)
            use_httpx: Whether to use httpx if available (default: True)
        """
        self.package_name = package_name
        self.pypi_url = pypi_url or f"https://pypi.org/pypi/{package_name}/json"
        self.timeout = timeout
        self.use_httpx = use_httpx and HTTPX_AVAILABLE

    def fetch_latest_version(self) -> Optional[str]:
        """Fetch latest version from PyPI.

        Returns:
            Latest version string, or None if fetch failed
        """
        if self.use_httpx:
            return self._fetch_with_httpx()
        else:
            return self._fetch_with_urllib()

    def _fetch_with_httpx(self) -> Optional[str]:
        """Fetch using httpx (async-capable, more features)."""
        if not HTTPX_AVAILABLE:
            return self._fetch_with_urllib()

        try:
            import asyncio

            # Try to use existing event loop, create new if needed
            try:
                loop = asyncio.get_running_loop()
                # Can't use async in sync context, fall back to urllib
                return self._fetch_with_urllib()
            except RuntimeError:
                # No running loop, safe to create one
                return asyncio.run(self._fetch_async())
        except Exception:
            return None

    async def _fetch_async(self) -> Optional[str]:
        """Async fetch implementation using httpx."""
        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.get(self.pypi_url)
                response.raise_for_status()
                data = response.json()

                if (
                    isinstance(data, dict)
                    and "info" in data
                    and "version" in data["info"]
                ):
                    return str(data["info"]["version"])
        except Exception:
            pass

        return None

    def _fetch_with_urllib(self) -> Optional[str]:
        """Fetch using urllib (stdlib, no dependencies)."""
        try:
            request = Request(self.pypi_url)
            request.add_header("User-Agent", f"henriqueslab-updater/{self.package_name}")

            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))

                if (
                    isinstance(data, dict)
                    and "info" in data
                    and "version" in data["info"]
                ):
                    return str(data["info"]["version"])
        except (URLError, HTTPError, json.JSONDecodeError, KeyError, TimeoutError):
            pass

        return None

    def get_priority(self) -> int:
        """Get priority (100 = normal)."""
        return 100
