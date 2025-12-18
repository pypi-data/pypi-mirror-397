"""Rich notifier with colored panels (optional dependency)."""

from typing import Any, Dict

from .base import Notifier

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class RichNotifier(Notifier):
    """Rich-formatted notifier with colors and panels.

    Falls back to plain text if rich is not available.
    """

    def __init__(
        self,
        title: str = "Update Available",
        color_scheme: str = "bright_blue",
    ):
        """Initialize rich notifier.

        Args:
            title: Title for the notification panel
            color_scheme: Color scheme for the panel border
        """
        self.title = title
        self.color_scheme = color_scheme
        self.console = Console() if RICH_AVAILABLE else None

    def format(self, update_info: Dict[str, Any]) -> str:
        """Format update information with rich markup.

        Args:
            update_info: Dictionary with update information

        Returns:
            Formatted message (with or without rich markup)
        """
        if not RICH_AVAILABLE:
            # Fallback to plain formatting
            return self._format_plain(update_info)

        lines = [
            f"[bold cyan]{update_info['package_name']}[/bold cyan] "
            f"[dim]v{update_info['current_version']}[/dim] "
            f"[bold yellow]→[/bold yellow] "
            f"[bold green]v{update_info['latest_version']}[/bold green]",
            "",
        ]

        # Add changelog if available
        if "changelog_summary" in update_info and update_info["changelog_summary"]:
            lines.append(update_info["changelog_summary"])
            lines.append("")

        # Add installation info
        lines.append(f"[bold]Installed via:[/bold] {update_info['install_method']}")
        lines.append(f"[bold]To upgrade:[/bold] [cyan]{update_info['upgrade_command']}[/cyan]")

        # Add release URL if available
        if "release_url" in update_info and update_info["release_url"]:
            lines.append("")
            lines.append(f"[dim]Full details:[/dim] {update_info['release_url']}")

        return "\n".join(lines)

    def _format_plain(self, update_info: Dict[str, Any]) -> str:
        """Plain text fallback formatting.

        Args:
            update_info: Dictionary with update information

        Returns:
            Plain text formatted message
        """
        lines = [
            f"{update_info['package_name']} "
            f"v{update_info['current_version']} → v{update_info['latest_version']}",
            "",
        ]

        if "changelog_summary" in update_info and update_info["changelog_summary"]:
            lines.append(update_info["changelog_summary"])
            lines.append("")

        lines.append(f"Installed via: {update_info['install_method']}")
        lines.append(f"To upgrade: {update_info['upgrade_command']}")

        if "release_url" in update_info and update_info["release_url"]:
            lines.append("")
            lines.append(f"Full details: {update_info['release_url']}")

        return "\n".join(lines)

    def display(self, message: str) -> None:
        """Display message using rich Panel or fallback to print.

        Args:
            message: Formatted message
        """
        if not RICH_AVAILABLE or not self.console:
            print(message, flush=True)
            return

        try:
            panel = Panel(
                message,
                title=f"[bold magenta]📦 {self.title}[/bold magenta]",
                title_align="left",
                border_style=self.color_scheme,
                padding=(1, 2),
                expand=False,
            )
            self.console.print()
            self.console.print(panel)
        except Exception:
            # Fallback to plain print for encoding issues
            print(message, flush=True)
