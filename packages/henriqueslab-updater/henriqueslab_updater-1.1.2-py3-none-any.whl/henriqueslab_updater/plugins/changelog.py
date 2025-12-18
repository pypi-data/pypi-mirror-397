"""Changelog parsing plugin for update notifications."""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class ChangelogEntry:
    """Represents a changelog entry for a version."""

    version: str
    date: Optional[str]
    sections: Dict[str, List[str]]
    raw_content: str


class ChangelogPlugin:
    """Plugin to fetch and display changelog information."""

    # Regex patterns
    VERSION_HEADER = re.compile(r"^## \[v?([\d.]+)\](?:\s*-\s*(\d{4}-\d{2}-\d{2}))?", re.MULTILINE)
    SECTION_HEADER = re.compile(
        r"^### (Added|Changed|Fixed|Removed|Documentation|Deprecated|Security)",
        re.MULTILINE,
    )
    BREAKING_PATTERNS = [
        re.compile(r"\*\*BREAKING", re.IGNORECASE),
        re.compile(r"breaking change", re.IGNORECASE),
        re.compile(r"⚠️", re.MULTILINE),
    ]

    def __init__(
        self,
        changelog_url: str,
        highlights_per_version: int = 3,
        show_breaking_changes: bool = True,
        timeout: int = 5,
    ):
        """Initialize changelog plugin.

        Args:
            changelog_url: URL to CHANGELOG.md file
            highlights_per_version: Number of highlights per version (default: 3)
            show_breaking_changes: Whether to prominently show breaking changes
            timeout: Request timeout in seconds
        """
        self.changelog_url = changelog_url
        self.highlights_per_version = highlights_per_version
        self.show_breaking_changes = show_breaking_changes
        self.timeout = timeout
        self._cached_content: Optional[str] = None

    def enhance(self, update_info: Dict[str, Any]) -> Dict[str, Any]:
        """Add changelog information to update info.

        Args:
            update_info: Dictionary with update information

        Returns:
            Enhanced update_info with changelog_summary added
        """
        current_version = update_info.get("current_version")
        latest_version = update_info.get("latest_version")

        if not current_version or not latest_version:
            return update_info

        try:
            summary = self.get_changelog_summary(current_version, latest_version)
            if summary:
                update_info["changelog_summary"] = summary
        except Exception:
            # Silent failure - don't disrupt update notification
            pass

        return update_info

    def get_changelog_summary(self, current: str, latest: str) -> Optional[str]:
        """Get formatted changelog summary between versions.

        Args:
            current: Current version
            latest: Latest version

        Returns:
            Formatted changelog summary, or None if fetch fails
        """
        content = self._fetch_changelog()
        if not content:
            return None

        # Get versions between current and latest
        versions = self._get_versions_between(content, current, latest)
        if not versions:
            return None

        # Parse entries for each version
        entries = []
        for version in versions:
            entry = self._parse_version_entry(content, version)
            if entry:
                entries.append(entry)

        if not entries:
            return None

        # Format summary
        return self._format_summary(entries)

    def _fetch_changelog(self) -> Optional[str]:
        """Fetch changelog content from URL.

        Returns:
            Changelog content, or None if fetch fails
        """
        if self._cached_content:
            return self._cached_content

        try:
            req = Request(self.changelog_url, headers={"User-Agent": "henriqueslab-updater"})
            with urlopen(req, timeout=self.timeout) as response:
                self._cached_content = response.read().decode("utf-8")
                return self._cached_content
        except (URLError, HTTPError, TimeoutError, Exception):
            return None

    def _parse_version_entry(self, content: str, version: str) -> Optional[ChangelogEntry]:
        """Parse a specific version's changelog entry.

        Args:
            content: Full changelog content
            version: Version to extract

        Returns:
            ChangelogEntry if found, None otherwise
        """
        version = version.lstrip("v")

        # Find all version headers
        version_matches = list(self.VERSION_HEADER.finditer(content))

        # Find target version
        target_match = None
        next_match = None

        for i, match in enumerate(version_matches):
            if match.group(1) == version:
                target_match = match
                if i + 1 < len(version_matches):
                    next_match = version_matches[i + 1]
                break

        if not target_match:
            return None

        # Extract content between versions
        start_pos = target_match.end()
        end_pos = next_match.start() if next_match else len(content)
        entry_content = content[start_pos:end_pos].strip()

        # Parse sections
        sections = self._parse_sections(entry_content)

        return ChangelogEntry(
            version=version,
            date=target_match.group(2),
            sections=sections,
            raw_content=entry_content,
        )

    def _parse_sections(self, content: str) -> Dict[str, List[str]]:
        """Parse changelog sections.

        Args:
            content: Changelog entry content

        Returns:
            Dictionary mapping section names to lists of changes
        """
        sections = {}
        current_section = None
        current_items = []

        for line in content.split("\n"):
            # Check for section header
            section_match = self.SECTION_HEADER.match(line)
            if section_match:
                # Save previous section
                if current_section:
                    sections[current_section] = current_items

                # Start new section
                current_section = section_match.group(1)
                current_items = []
                continue

            # Check for list item
            if current_section and line.strip().startswith("-"):
                item = line.strip().lstrip("-").lstrip("*").strip()
                if item:
                    current_items.append(item)

        # Save last section
        if current_section:
            sections[current_section] = current_items

        return sections

    def _extract_highlights(self, entry: ChangelogEntry) -> List[Tuple[str, str]]:
        """Extract highlights from changelog entry.

        Args:
            entry: Changelog entry

        Returns:
            List of (emoji, description) tuples
        """
        highlights = []
        priority_sections = [
            ("Added", "✨"),
            ("Changed", "🔄"),
            ("Fixed", "🐛"),
            ("Removed", "🗑️"),
            ("Security", "🔒"),
        ]

        for section_name, emoji in priority_sections:
            if section_name in entry.sections:
                items = entry.sections[section_name]
                for item in items:
                    if len(highlights) >= self.highlights_per_version:
                        break

                    # Get first line
                    first_line = item.split("\n")[0].strip().replace("**", "")

                    # Truncate if too long
                    if len(first_line) > 80:
                        first_line = first_line[:77] + "..."

                    highlights.append((emoji, first_line))

                if len(highlights) >= self.highlights_per_version:
                    break

        return highlights[: self.highlights_per_version]

    def _detect_breaking_changes(self, entry: ChangelogEntry) -> List[str]:
        """Detect breaking changes in entry.

        Args:
            entry: Changelog entry

        Returns:
            List of breaking change descriptions
        """
        breaking_changes = []

        for _section_name, items in entry.sections.items():
            for item in items:
                for pattern in self.BREAKING_PATTERNS:
                    if pattern.search(item):
                        first_line = item.split("\n")[0].strip().replace("**", "")
                        first_line = re.sub(
                            r"^\*\*BREAKING:?\*\*\s*", "", first_line, flags=re.IGNORECASE
                        )
                        first_line = re.sub(r"^BREAKING:?\s*", "", first_line, flags=re.IGNORECASE)
                        breaking_changes.append(first_line)
                        break

        return breaking_changes

    def _get_versions_between(self, content: str, current: str, latest: str) -> List[str]:
        """Get versions between current and latest.

        Args:
            content: Full changelog content
            current: Current version
            latest: Latest version

        Returns:
            List of version strings in chronological order
        """
        current = current.lstrip("v")
        latest = latest.lstrip("v")

        # Find all versions
        version_matches = self.VERSION_HEADER.findall(content)
        all_versions = [v[0] for v in version_matches]

        try:
            current_idx = all_versions.index(current)
            latest_idx = all_versions.index(latest)
        except ValueError:
            return []

        # Extract versions between
        if latest_idx < current_idx:
            between_versions = all_versions[latest_idx:current_idx]
            return list(reversed(between_versions))
        else:
            return []

    def _format_summary(self, entries: List[ChangelogEntry]) -> str:
        """Format changelog entries for display.

        Args:
            entries: List of changelog entries

        Returns:
            Formatted summary string
        """
        lines = []

        # Collect breaking changes
        all_breaking = []
        for entry in entries:
            breaking = self._detect_breaking_changes(entry)
            if breaking:
                all_breaking.extend([(entry.version, b) for b in breaking])

        # Show breaking changes first
        if self.show_breaking_changes and all_breaking:
            lines.append("⚠️  BREAKING CHANGES:")
            for version, change in all_breaking:
                lines.append(f"  • {change} (v{version})")
            lines.append("")

        # Show highlights per version
        lines.append("✨ What's New:")
        for entry in entries:
            lines.append(f"  v{entry.version}" + (f" ({entry.date})" if entry.date else "") + ":")
            highlights = self._extract_highlights(entry)
            for emoji, description in highlights:
                lines.append(f"    {emoji} {description}")
            if not highlights:
                lines.append("    No highlights available")

        return "\n".join(lines)
