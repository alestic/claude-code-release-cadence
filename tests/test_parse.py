"""Tests for data loading and parsing."""
# [Created with AI: Claude Code with Opus 4.6]

from pathlib import Path

from claude_code_release_cadence.parse import (
    load_changelog,
    load_npm_sizes,
    load_npm_times,
)

FIXTURES: Path = Path(__file__).parent / "fixtures"


def test_load_npm_times_loads_versions() -> None:
    """Should load version timestamp entries."""
    result: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    assert "0.2.6" in result
    assert "2.1.2" in result


def test_load_npm_times_count() -> None:
    """Should have exactly the version entries."""
    result: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    assert len(result) == 7


def test_load_changelog_multi_section() -> None:
    """Should parse multiple ## sections."""
    result: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    assert "2.1.2" in result
    assert "2.1.1" in result
    assert "0.2.7" in result


def test_load_changelog_body_content() -> None:
    """Body text should contain the bullet points."""
    result: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    assert "Fixed a crash" in result["2.1.2"]
    assert "Added guard" in result["2.1.1"]


def test_load_changelog_empty_section() -> None:
    """Sections with no content should still be parsed."""
    result: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    # 0.2.6 has no bullets but is the last section
    assert "0.2.6" in result


def test_load_changelog_empty_body_is_string() -> None:
    """Empty sections should have a string body (possibly blank)."""
    result: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    assert isinstance(result["0.2.6"], str)


# --- load_npm_sizes ---


def test_load_npm_sizes_basic() -> None:
    """Should load size data for all versions."""
    result = load_npm_sizes(FIXTURES / "sample-npm-sizes.json")
    assert len(result) == 7
    assert "2.1.2" in result
    assert result["2.1.2"]["unpackedSize"] == 4520000
    assert result["2.1.2"]["fileCount"] == 328


def test_load_npm_sizes_missing_file() -> None:
    """Should return empty dict for non-existent file."""
    result = load_npm_sizes(FIXTURES / "nonexistent.json")
    assert result == {}


def test_load_npm_sizes_has_all_versions() -> None:
    """All versions from sample should be present."""
    result = load_npm_sizes(FIXTURES / "sample-npm-sizes.json")
    expected: set[str] = {"0.2.6", "0.2.7", "1.0.1", "1.0.2", "2.0.1", "2.1.1", "2.1.2"}
    assert set(result.keys()) == expected
