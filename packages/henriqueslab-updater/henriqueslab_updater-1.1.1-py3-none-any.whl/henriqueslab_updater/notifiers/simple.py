"""Simple text notifier (stdlib only)."""

from typing import Any, Dict

from .base import Notifier


class SimpleNotifier(Notifier):
    """Plain text notifier using only stdlib."""

    def __init__(self, title: str = "Update Available"):
        """Initialize simple notifier.

        Args:
            title: Title for the notification (default: "Update Available")
        """
        self.title = title

    def format(self, update_info: Dict[str, Any]) -> str:
        """Format update information as plain text.

        Args:
            update_info: Dictionary with keys:
                - package_name: Package name
                - current_version: Current version
                - latest_version: Latest version
                - install_method: Installation method name
                - upgrade_command: Upgrade command
                - release_url: URL to release notes (optional)
                - changelog_summary: Changelog text (optional)

        Returns:
            Formatted plain text message
        """
        lines = [
            "",
            "─" * 64,
            f"📦 {self.title}: {update_info['package_name']} "
            f"v{update_info['current_version']} → v{update_info['latest_version']}",
            "",
        ]

        # Add changelog if available
        if "changelog_summary" in update_info and update_info["changelog_summary"]:
            lines.append(update_info["changelog_summary"])
            lines.append("")

        # Add installation info
        lines.append(f"   Installed via: {update_info['install_method']}")
        lines.append(f"   To upgrade: {update_info['upgrade_command']}")

        # Add release URL if available
        if "release_url" in update_info and update_info["release_url"]:
            lines.append("")
            lines.append(f"   Release notes: {update_info['release_url']}")

        lines.append("─" * 64)
        lines.append("")

        return "\n".join(lines)

    def display(self, message: str) -> None:
        """Display message using print.

        Args:
            message: Formatted message
        """
        print(message, flush=True)
