"""Tests for data export (JSON, CSV)."""
# [Created with AI: Claude Code with Opus 4.6]

import csv
import json
from pathlib import Path

from claude_code_release_cadence.compute import compute_all
from claude_code_release_cadence.export import (
    export_json,
    export_notes_json,
    export_releases_csv,
)
from claude_code_release_cadence.parse import (
    load_changelog,
    load_npm_sizes,
    load_npm_times,
)

FIXTURES: Path = Path(__file__).parent / "fixtures"


def _load_fixtures() -> tuple[
    dict[str, str], dict[str, str], dict[str, dict[str, int]]
]:
    npm_times = load_npm_times(FIXTURES / "sample-npm-times.json")
    changelog = load_changelog(FIXTURES / "sample-changelog.md")
    npm_sizes = load_npm_sizes(FIXTURES / "sample-npm-sizes.json")
    return npm_times, changelog, npm_sizes


def test_export_json_creates_file(tmp_path: Path) -> None:
    """export_json should write a valid JSON file."""
    npm_times, changelog, npm_sizes = _load_fixtures()
    data = compute_all(npm_times, changelog=changelog, npm_sizes=npm_sizes)
    out = tmp_path / "data.json"
    export_json(data, out)
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert loaded["total_count"] == 8


def test_export_json_has_all_keys(tmp_path: Path) -> None:
    """Exported JSON should contain all ComputedData keys."""
    npm_times, changelog, npm_sizes = _load_fixtures()
    data = compute_all(npm_times, changelog=changelog, npm_sizes=npm_sizes)
    out = tmp_path / "data.json"
    export_json(data, out)
    loaded = json.loads(out.read_text())
    assert set(loaded.keys()) == set(data.keys())


def test_export_releases_csv_columns(tmp_path: Path) -> None:
    """CSV should have the expected column headers."""
    npm_times, changelog, npm_sizes = _load_fixtures()
    data = compute_all(npm_times, changelog=changelog, npm_sizes=npm_sizes)
    out = tmp_path / "releases.csv"
    export_releases_csv(data["releases"], out, size_data=data["size_data"])
    with open(out) as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "version",
            "date",
            "timestamp",
            "major",
            "unpacked_size",
            "file_count",
        ]


def test_export_releases_csv_row_count(tmp_path: Path) -> None:
    """CSV should have one row per release."""
    npm_times, changelog, npm_sizes = _load_fixtures()
    data = compute_all(npm_times, changelog=changelog, npm_sizes=npm_sizes)
    out = tmp_path / "releases.csv"
    export_releases_csv(data["releases"], out, size_data=data["size_data"])
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 8


def test_export_releases_csv_without_sizes(tmp_path: Path) -> None:
    """CSV should work without size data, leaving size columns empty."""
    npm_times, changelog, _ = _load_fixtures()
    data = compute_all(npm_times, changelog=changelog)
    out = tmp_path / "releases.csv"
    export_releases_csv(data["releases"], out)
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["unpacked_size"] == ""
    assert rows[0]["file_count"] == ""


def test_export_notes_json_includes_body(tmp_path: Path) -> None:
    """Notes JSON should include full changelog body text."""
    npm_times, changelog, _ = _load_fixtures()
    data = compute_all(npm_times, changelog=changelog)
    out = tmp_path / "notes.json"
    export_notes_json(data["notes_data"], changelog, out)
    records = json.loads(out.read_text())
    versions = {r["version"] for r in records}
    assert "2.1.2" in versions
    record_2_1_2 = next(r for r in records if r["version"] == "2.1.2")
    assert "body" in record_2_1_2
    assert "Fixed a crash" in record_2_1_2["body"]


def test_export_notes_json_without_changelog(tmp_path: Path) -> None:
    """Notes JSON should work without changelog (no body fields)."""
    npm_times, changelog, _ = _load_fixtures()
    data = compute_all(npm_times, changelog=changelog)
    out = tmp_path / "notes.json"
    export_notes_json(data["notes_data"], None, out)
    records = json.loads(out.read_text())
    assert all("body" not in r for r in records)


def test_export_creates_parent_dirs(tmp_path: Path) -> None:
    """Export functions should create parent directories."""
    npm_times, changelog, _ = _load_fixtures()
    data = compute_all(npm_times, changelog=changelog)
    out = tmp_path / "sub" / "dir" / "data.json"
    export_json(data, out)
    assert out.exists()
