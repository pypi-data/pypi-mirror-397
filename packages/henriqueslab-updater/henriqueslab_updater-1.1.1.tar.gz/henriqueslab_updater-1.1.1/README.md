# henriqueslab-updater

Centralized update checking library for HenriquesLab Python packages.

## Features

- **Multi-source version checking**: PyPI, Homebrew, GitHub formulas
- **Installation method detection**: Automatically detects Homebrew, pipx, uv, pip (user/system), and development installations
- **Smart caching**: 24-hour TTL to avoid excessive network requests
- **Non-blocking**: Background checks that don't disrupt CLI execution
- **Pluggable architecture**: Customizable version sources, notifiers, and plugins
- **Optional changelog integration**: Display changelog highlights in update notifications
- **Minimal dependencies**: Only `packaging` required, optional `rich` and `httpx` for enhanced features

## Installation

```bash
pip install henriqueslab-updater
```

With optional dependencies:
```bash
pip install henriqueslab-updater[all]  # includes rich and httpx
pip install henriqueslab-updater[rich]  # just rich formatting
```

## Quick Start

```python
from henriqueslab_updater import UpdateChecker

# Simple usage
checker = UpdateChecker(
    package_name="your-package",
    current_version="1.0.0",
)

# Start background check (non-blocking)
checker.check_async()

# Later, show notification if available
checker.show_notification()
```

## Advanced Usage

```python
from henriqueslab_updater import (
    UpdateChecker,
    ChangelogPlugin,
    RichNotifier,
)

checker = UpdateChecker(
    package_name="your-package",
    current_version="1.0.0",
    notifier=RichNotifier(title="Update Available"),
    plugins=[
        ChangelogPlugin(
            changelog_url="https://raw.githubusercontent.com/org/repo/main/CHANGELOG.md",
            highlights_per_version=3,
        ),
    ],
)

checker.check_async()
checker.show_notification()
```

## Supported Installation Methods

- **Homebrew** (`brew`)
- **pipx**
- **uv tools**
- **pip** (user and system installs)
- **Development** (git clone + editable install)

## Configuration

Environment variables:
- `NO_UPDATE_NOTIFIER=1` - Disable all update checks
- `{PACKAGE}_NO_UPDATE_CHECK=1` - Disable for specific package

## License

MIT License - see LICENSE file for details.

## Development

```bash
git clone https://github.com/HenriquesLab/henriqueslab-updater.git
cd henriqueslab-updater
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all,dev]"
pytest
```
