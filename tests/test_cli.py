"""Tests for CLI entry point."""
# [Created with AI: Claude Code with Opus 4.6]

import subprocess
import sys


def test_cli_version() -> None:
    """--version should print version and exit 0."""
    result = subprocess.run(
        [sys.executable, "-m", "claude_code_release_cadence", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "claude-code-release-cadence" in result.stdout


def test_cli_help() -> None:
    """--help should print usage and exit 0."""
    result = subprocess.run(
        [sys.executable, "-m", "claude_code_release_cadence", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Generate Claude Code release cadence dashboard" in result.stdout


def test_cli_unknown_flag() -> None:
    """Unknown flags should exit non-zero."""
    result = subprocess.run(
        [sys.executable, "-m", "claude_code_release_cadence", "--no-such-flag"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
