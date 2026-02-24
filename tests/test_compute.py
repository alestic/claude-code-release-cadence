"""Tests for statistical computations."""
# [Created with AI: Claude Code with Opus 4.6]

from pathlib import Path

from claude_code_release_cadence.compute import (
    _merge_changelog_versions,
    classify_major,
    compute_all,
    parse_release_notes,
)
from claude_code_release_cadence.parse import (
    load_changelog,
    load_npm_sizes,
    load_npm_times,
)

FIXTURES: Path = Path(__file__).parent / "fixtures"


# --- classify_major ---


def test_classify_major_0x() -> None:
    """0.x versions get their actual minor."""
    assert classify_major("0.2.6") == "0.2.x"
    assert classify_major("0.2.45") == "0.2.x"


def test_classify_major_1x() -> None:
    """1.x versions get their actual minor."""
    assert classify_major("1.0.1") == "1.0.x"
    assert classify_major("1.0.99") == "1.0.x"


def test_classify_major_2x() -> None:
    """2.x versions get their actual minor."""
    assert classify_major("2.0.1") == "2.0.x"
    assert classify_major("2.1.42") == "2.1.x"


def test_classify_major_future() -> None:
    """Future version series should work dynamically."""
    assert classify_major("3.5.2") == "3.5.x"
    assert classify_major("10.2.7") == "10.2.x"


# --- parse_release_notes ---


def test_parse_notes_all_fixes() -> None:
    """Body where all bullets are fixes."""
    body: str = "- Fixed a crash\n- Fixed login error\n"
    result = parse_release_notes(body)
    assert result is not None
    total, fixes, non_fixes = result
    assert total == 2
    assert fixes == 2
    assert non_fixes == 0


def test_parse_notes_mixed() -> None:
    """Body with mix of fixes and non-fixes."""
    body: str = "- Added new feature\n- Fixed a bug\n- Improved performance\n"
    result = parse_release_notes(body)
    assert result is not None
    total, fixes, non_fixes = result
    assert total == 3
    assert fixes == 1
    assert non_fixes == 2


def test_parse_notes_no_fixes() -> None:
    """Body with no fixes at all."""
    body: str = "- Added streaming\n- Improved startup\n"
    result = parse_release_notes(body)
    assert result is not None
    total, fixes, non_fixes = result
    assert total == 2
    assert fixes == 0
    assert non_fixes == 2


def test_parse_notes_empty_body() -> None:
    """Empty body should return None."""
    assert parse_release_notes("") is None
    assert parse_release_notes("   \n  ") is None


def test_parse_notes_no_bullets() -> None:
    """Body with text but no bullet points."""
    assert parse_release_notes("Just some text\nwithout bullets") is None


def test_parse_notes_fix_variants() -> None:
    """Different forms of 'fix' should all match."""
    body: str = "- Fix the bug\n- Fixed another bug\n- Fixes edge case\n"
    result = parse_release_notes(body)
    assert result is not None
    _, fixes, _ = result
    assert fixes == 3


# --- compute_all ---


def test_compute_all_basic() -> None:
    """Integration test with sample fixtures."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    changelog: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")

    data = compute_all(npm_times, changelog=changelog)

    assert data["total_count"] == 8
    assert len(data["releases"]) == 8
    assert len(data["gaps"]) == 7


def test_compute_all_majors_order() -> None:
    """Majors should be in chronological order of first appearance."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    data = compute_all(npm_times)

    assert data["majors_order"] == ["0.2.x", "1.0.x", "2.0.x", "2.1.x"]


def test_compute_all_has_required_keys() -> None:
    """Output should contain all expected keys."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    data = compute_all(npm_times)

    expected_keys: set[str] = {
        "releases",
        "gaps",
        "week_labels",
        "week_stacked",
        "week_stacked_fixonly",
        "week_notes_stacked",
        "week_notes_stacked_fixes",
        "dow_stacked",
        "dow_stacked_fixonly",
        "hour_stacked",
        "hour_stacked_fixonly",
        "major_stats",
        "majors_order",
        "total_count",
        "first_date",
        "last_date",
        "notes_data",
        "notes_count",
        "heatmap_dow_hour",
        "heatmap_dow_hour_fixes",
        "size_data",
        "generated_at",
    }
    assert expected_keys == set(data.keys())


def test_compute_all_dow_stacked_length() -> None:
    """Day-of-week stacked arrays should have exactly 7 elements per major."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    data = compute_all(npm_times)
    for m in data["majors_order"]:
        assert len(data["dow_stacked"][m]) == 7
        assert len(data["dow_stacked_fixonly"][m]) == 7


def test_compute_all_hour_stacked_length() -> None:
    """Hour stacked arrays should have exactly 24 elements per major."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    data = compute_all(npm_times)
    for m in data["majors_order"]:
        assert len(data["hour_stacked"][m]) == 24
        assert len(data["hour_stacked_fixonly"][m]) == 24


def test_compute_all_fix_only_detection() -> None:
    """Versions where all bullets are fixes should be in fix-only set."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    changelog: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    data = compute_all(npm_times, changelog=changelog)

    # 1.0.1 has two "Fixed" bullets and nothing else — should be fix-only
    # Check that fix-only versions show up in week_stacked_fixonly
    # by verifying there's at least one non-zero value somewhere
    has_fixonly: bool = any(
        v > 0 for counts in data["week_stacked_fixonly"].values() for v in counts
    )
    assert has_fixonly


def test_compute_all_notes_data() -> None:
    """Notes data should include entries from changelog."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    changelog: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    data = compute_all(npm_times, changelog=changelog)

    versions_with_notes: set[str] = {n["version"] for n in data["notes_data"]}
    assert "2.1.2" in versions_with_notes
    assert "2.1.1" in versions_with_notes


# --- heatmap ---


def test_compute_all_heatmap_shape() -> None:
    """Heatmap should be 7 rows x 24 columns."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    changelog: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    data = compute_all(npm_times, changelog=changelog)

    assert len(data["heatmap_dow_hour"]) == 7
    assert len(data["heatmap_dow_hour_fixes"]) == 7
    for row in data["heatmap_dow_hour"]:
        assert len(row) == 24
    for row in data["heatmap_dow_hour_fixes"]:
        assert len(row) == 24


def test_compute_all_heatmap_has_entries() -> None:
    """Heatmap should have non-zero totals for versions with changelog."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    changelog: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    data = compute_all(npm_times, changelog=changelog)

    total: int = sum(cell for row in data["heatmap_dow_hour"] for cell in row)
    assert total > 0


def test_compute_all_heatmap_fixes_subset() -> None:
    """Fix counts should not exceed total counts in any cell."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    changelog: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    data = compute_all(npm_times, changelog=changelog)

    for dow in range(7):
        for hour in range(24):
            assert (
                data["heatmap_dow_hour_fixes"][dow][hour]
                <= data["heatmap_dow_hour"][dow][hour]
            )


# --- size_data ---


def test_compute_all_size_data() -> None:
    """Size data should be populated when npm_sizes is provided."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    npm_sizes: dict = load_npm_sizes(FIXTURES / "sample-npm-sizes.json")
    data = compute_all(npm_times, npm_sizes=npm_sizes)

    assert len(data["size_data"]) == 7
    versions: set[str] = {s["version"] for s in data["size_data"]}
    assert "2.1.2" in versions
    assert "0.2.6" in versions


def test_compute_all_size_data_empty() -> None:
    """Size data should be empty when no npm_sizes provided."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    data = compute_all(npm_times)

    assert data["size_data"] == []


def test_compute_all_size_data_sorted() -> None:
    """Size records should be in chronological order."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    npm_sizes: dict = load_npm_sizes(FIXTURES / "sample-npm-sizes.json")
    data = compute_all(npm_times, npm_sizes=npm_sizes)

    versions: list[str] = [s["version"] for s in data["size_data"]]
    assert versions[0] == "0.2.6"
    assert versions[-1] == "2.1.2"


# --- generated_at ---


def test_compute_all_generated_at() -> None:
    """generated_at should be a non-empty string."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    data = compute_all(npm_times)

    assert isinstance(data["generated_at"], str)
    assert len(data["generated_at"]) > 0


# --- _merge_changelog_versions ---


def test_merge_changelog_only_versions() -> None:
    """Changelog-only versions should appear in the output releases."""
    npm_times: dict[str, str] = load_npm_times(FIXTURES / "sample-npm-times.json")
    changelog: dict[str, str] = load_changelog(FIXTURES / "sample-changelog.md")
    data = compute_all(npm_times, changelog=changelog)

    versions: set[str] = {r["version"] for r in data["releases"]}
    assert "0.2.8" in versions


def test_merge_interpolated_timestamp() -> None:
    """Interpolated timestamp should fall between the two neighbors."""
    npm_times: dict[str, str] = {
        "1.0.1": "2025-04-01T00:00:00.000Z",
        "1.0.3": "2025-04-03T00:00:00.000Z",
    }
    changelog: dict[str, str] = {"1.0.2": "- Fixed a bug\n"}

    merged = _merge_changelog_versions(npm_times, changelog)

    assert "1.0.2" in merged
    assert merged["1.0.2"] > npm_times["1.0.1"]
    assert merged["1.0.2"] < npm_times["1.0.3"]


def test_merge_no_changelog() -> None:
    """Passing None changelog should return npm_times unchanged."""
    npm_times: dict[str, str] = {"1.0.1": "2025-04-01T00:00:00.000Z"}

    result = _merge_changelog_versions(npm_times, None)

    assert result is npm_times
