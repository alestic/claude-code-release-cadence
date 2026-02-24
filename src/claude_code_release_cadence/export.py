"""Export computed data to JSON and CSV."""
# [Created with AI: Claude Code with Opus 4.6]

import csv
import json
import logging
from pathlib import Path

from .compute import ComputedData, NotesRecord, Release, SizeRecord

log: logging.Logger = logging.getLogger(__name__)


def export_json(data: ComputedData, output_path: Path) -> None:
    """Export full computed data as JSON.

    Preserves all structured data including nested dicts and lists.

    Args:
        data: ComputedData from compute_all().
        output_path: Where to write the JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    log.info("Exported %s", output_path)


def export_releases_csv(
    releases: list[Release],
    output_path: Path,
    size_data: list[SizeRecord] | None = None,
) -> None:
    """Export release list as CSV with optional size columns.

    Columns: version, date, timestamp, major, unpacked_size, file_count.

    Args:
        releases: List of Release dicts from computed data.
        output_path: Where to write the CSV file.
        size_data: Optional list of SizeRecord dicts for version lookup.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = [
        "version",
        "date",
        "timestamp",
        "major",
        "unpacked_size",
        "file_count",
    ]
    size_lookup: dict[str, SizeRecord] = {}
    if size_data:
        size_lookup = {s["version"]: s for s in size_data}
    rows: list[dict] = []
    for r in releases:
        row: dict = dict(r)
        size_info = size_lookup.get(r["version"])
        row["unpacked_size"] = size_info["unpacked_size"] if size_info else ""
        row["file_count"] = size_info["file_count"] if size_info else ""
        rows.append(row)
    with open(output_path, "w", newline="") as f:
        writer: csv.DictWriter = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)
    log.info("Exported %s (%d releases)", output_path, len(releases))


def export_notes_json(
    notes_data: list[NotesRecord],
    changelog: dict[str, str] | None,
    output_path: Path,
) -> None:
    """Export release notes with full text as JSON.

    Each record includes version, timestamp, major, bullet counts,
    and the full changelog body text.

    Args:
        notes_data: List of NotesRecord dicts from computed data.
        changelog: version -> body text dict from CHANGELOG.md (optional).
        output_path: Where to write the JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    for note in notes_data:
        record: dict = dict(note)
        if changelog and note["version"] in changelog:
            record["body"] = changelog[note["version"]].strip()
        records.append(record)
    with open(output_path, "w") as f:
        json.dump(records, f, indent=2)
    log.info("Exported %s (%d releases with notes)", output_path, len(records))
