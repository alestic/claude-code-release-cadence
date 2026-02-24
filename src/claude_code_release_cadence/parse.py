"""Data loading and parsing from raw files."""
# [Created with AI: Claude Code with Opus 4.6]

import json
from pathlib import Path


def load_npm_times(path: Path) -> dict[str, str]:
    """Load npm publish timestamps.

    Args:
        path: Path to npm-times.json (from npm registry API).

    Returns:
        Dict mapping version string to ISO timestamp string.
    """
    with open(path) as f:
        raw: dict[str, str] = json.load(f)
    return raw


def load_npm_sizes(path: Path) -> dict[str, dict[str, int]]:
    """Load npm package size data.

    Args:
        path: Path to npm-sizes.json.

    Returns:
        Dict mapping version string to {unpackedSize, fileCount}.
        Returns empty dict if file does not exist (backward compat).
    """
    if not path.exists():
        return {}
    with open(path) as f:
        result: dict[str, dict[str, int]] = json.load(f)
    return result


def load_changelog(path: Path) -> dict[str, str]:
    """Parse CHANGELOG.md into a version-to-body mapping.

    Expects markdown sections like::

        ## 2.1.42
        - bullet one
        - bullet two

    Args:
        path: Path to CHANGELOG.md.

    Returns:
        Dict mapping version string to body text.
    """
    changelog: dict[str, str] = {}
    current_version: str | None = None
    current_lines: list[str] = []

    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("## "):
                if current_version:
                    changelog[current_version] = "\n".join(current_lines)
                current_version = line[3:].strip()
                current_lines = []
            elif current_version is not None:
                current_lines.append(line)

    if current_version:
        changelog[current_version] = "\n".join(current_lines)

    return changelog
