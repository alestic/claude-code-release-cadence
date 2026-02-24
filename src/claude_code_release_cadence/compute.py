"""Statistical computations and release classification."""
# [Created with AI: Claude Code with Opus 4.6]

import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Sequence, TypedDict

from .tz import to_pacific

# --- Types ---


class Release(TypedDict):
    """Processed release record."""

    version: str
    timestamp: str  # ISO format in Pacific
    date: str  # YYYY-MM-DD in Pacific
    major: str  # e.g. "2.1.x"


class Gap(TypedDict):
    """Gap between consecutive releases."""

    version: str
    timestamp: str
    days: float
    major: str


class NotesRecord(TypedDict):
    """Release notes analysis for a single version."""

    version: str
    timestamp: str
    major: str
    total: int
    fixes: int
    non_fixes: int


class SizeRecord(TypedDict):
    """Package size data for a single version."""

    version: str
    timestamp: str
    major: str
    unpacked_size: int
    file_count: int


class MajorStats(TypedDict):
    """Per-major-version statistics."""

    count: int
    span_days: float
    first: str
    last: str


class ComputedData(TypedDict):
    """All computed statistics for rendering and export."""

    releases: list[Release]
    gaps: list[Gap]
    week_labels: list[str]
    week_stacked: dict[str, list[int]]
    week_stacked_fixonly: dict[str, list[int]]
    week_notes_stacked: dict[str, list[int]]
    week_notes_stacked_fixes: dict[str, list[int]]
    dow_stacked: dict[str, list[int]]
    dow_stacked_fixonly: dict[str, list[int]]
    hour_stacked: dict[str, list[int]]
    hour_stacked_fixonly: dict[str, list[int]]
    major_stats: dict[str, MajorStats]
    majors_order: list[str]
    total_count: int
    first_date: str
    last_date: str
    notes_data: list[NotesRecord]
    notes_count: int
    heatmap_dow_hour: list[list[int]]
    heatmap_dow_hour_fixes: list[list[int]]
    size_data: list[SizeRecord]
    generated_at: str


# --- Constants ---

log: logging.Logger = logging.getLogger(__name__)

FIX_PATTERN: re.Pattern[str] = re.compile(
    r"\bbugfix(?:es)?\b|\bfix(?:e[ds])?\b|\bresolv(?:e[ds]?|ing)\b|\baddress(?:ed|es|ing)\b|\brevert(?:ed|s|ing)?\b",
    re.IGNORECASE,
)


# --- Helpers ---


def _version_tuple(version: str) -> tuple[int, ...]:
    """Convert "1.2.3" to (1, 2, 3) for numeric comparison."""
    return tuple(int(p) for p in version.split("."))


def _merge_changelog_versions(
    npm_times: dict[str, str],
    changelog: dict[str, str] | None,
) -> dict[str, str]:
    """Add changelog-only versions to npm_times with interpolated timestamps.

    For each version present in the changelog but missing from npm, find the
    nearest lower and upper npm versions by numeric version tuple and set the
    timestamp to the midpoint of those two neighbors.

    Returns a new dict; does not mutate *npm_times*.
    """
    if not changelog:
        return npm_times

    changelog_only: set[str] = set(changelog.keys()) - set(npm_times.keys())
    if not changelog_only:
        return npm_times

    merged: dict[str, str] = dict(npm_times)
    sorted_npm: list[tuple[tuple[int, ...], str, str]] = sorted(
        (_version_tuple(v), v, ts) for v, ts in npm_times.items()
    )

    for version in sorted(changelog_only):
        vt: tuple[int, ...] = _version_tuple(version)
        lower_ts: str | None = None
        upper_ts: str | None = None
        for nvt, _, ts in sorted_npm:
            if nvt < vt:
                lower_ts = ts
            elif nvt > vt:
                upper_ts = ts
                break

        if lower_ts and upper_ts:
            lo = datetime.fromisoformat(lower_ts.replace("Z", "+00:00"))
            hi = datetime.fromisoformat(upper_ts.replace("Z", "+00:00"))
            mid = lo + (hi - lo) / 2
            merged[version] = mid.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        elif lower_ts:
            merged[version] = lower_ts
        elif upper_ts:
            merged[version] = upper_ts
        else:
            continue

        log.info("Interpolated timestamp for changelog-only version %s", version)

    return merged


def classify_major(version: str) -> str:
    """Classify a version string into its major.minor.x series.

    Examples:
        "0.2.45" -> "0.2.x"
        "2.1.3"  -> "2.1.x"
    """
    parts: list[str] = version.split(".")
    if len(parts) < 2:
        return f"{parts[0]}.x"
    return f"{parts[0]}.{parts[1]}.x"


def parse_release_notes(body: str) -> tuple[int, int, int] | None:
    """Parse a release body into (total, fixes, non_fixes) or None."""
    if not body or not body.strip():
        return None
    bullets: list[str] = [
        line.strip() for line in body.splitlines() if line.strip().startswith("- ")
    ]
    if not bullets:
        return None
    fixes: int = sum(1 for b in bullets if FIX_PATTERN.search(b))
    return (len(bullets), fixes, len(bullets) - fixes)


def _stacked_by_major(
    releases: list[dict],
    majors_order: list[str],
    fix_only: set[str],
    key_fn: Callable[[dict], Any],
    buckets: Sequence,
) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    """Build (stacked, stacked_fixonly) dicts for a bucketing function.

    Counts releases per major per bucket, splitting fix-only vs other.
    Returns two dicts mapping major -> list of counts aligned to buckets.
    """
    counts: defaultdict[str, defaultdict[Any, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    fixonly: defaultdict[str, defaultdict[Any, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    for r in releases:
        b = key_fn(r)
        counts[r["major"]][b] += 1
        if r["version"] in fix_only:
            fixonly[r["major"]][b] += 1
    return (
        {
            m: [counts[m].get(b, 0) - fixonly[m].get(b, 0) for b in buckets]
            for m in majors_order
        },
        {m: [fixonly[m].get(b, 0) for b in buckets] for m in majors_order},
    )


# --- Sub-computations ---


def _build_releases(npm_times: dict[str, str]) -> list[dict]:
    """Build sorted release list with Pacific datetimes."""
    releases: list[dict] = []
    for version, timestamp in sorted(npm_times.items(), key=lambda x: x[1]):
        dt_utc: datetime = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        dt_pac: datetime = to_pacific(dt_utc)
        releases.append(
            {
                "version": version,
                "timestamp": dt_pac.strftime("%Y-%m-%dT%H:%M:%S"),
                "date": dt_pac.strftime("%Y-%m-%d"),
                "dt_pac": dt_pac,
                "major": classify_major(version),
            }
        )
    return releases


def _extract_majors_order(releases: list[dict]) -> list[str]:
    """Derive majors_order from chronological first appearance."""
    seen: set[str] = set()
    order: list[str] = []
    for r in releases:
        if r["major"] not in seen:
            order.append(r["major"])
            seen.add(r["major"])
    return order


def _compute_gaps(releases: list[dict]) -> list[Gap]:
    """Compute day gaps between consecutive releases."""
    return [
        {
            "version": releases[i]["version"],
            "timestamp": releases[i]["timestamp"],
            "days": round(
                (releases[i]["dt_pac"] - releases[i - 1]["dt_pac"]).total_seconds()
                / 86400,
                2,
            ),
            "major": releases[i]["major"],
        }
        for i in range(1, len(releases))
    ]


def _build_notes_lookup(
    changelog: dict[str, str] | None,
) -> tuple[dict[str, tuple[int, int, int]], set[str]]:
    """Parse changelog into notes lookup and fix-only version set."""
    notes: dict[str, tuple[int, int, int]] = {}
    fix_only: set[str] = set()
    if changelog:
        for version, body in changelog.items():
            parsed = parse_release_notes(body)
            if parsed:
                notes[version] = parsed
                if parsed[2] == 0 and parsed[0] > 0:  # non_fixes == 0
                    fix_only.add(version)
    return notes, fix_only


def _compute_weekly(
    releases: list[dict],
    majors_order: list[str],
    fix_only: set[str],
    notes_by_version: dict[str, tuple[int, int, int]],
) -> tuple[
    list[str],
    dict[str, list[int]],
    dict[str, list[int]],
    dict[str, list[int]],
    dict[str, list[int]],
]:
    """Compute weekly release counts and notes counts.

    Returns (week_labels, stacked, stacked_fixonly,
             notes_stacked, notes_stacked_fixes).
    """
    week_counts: defaultdict[str, defaultdict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    week_fixonly: defaultdict[str, defaultdict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    week_notes_nf: defaultdict[str, defaultdict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    week_notes_fx: defaultdict[str, defaultdict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )

    for r in releases:
        d: datetime = r["dt_pac"]
        week: str = (d - timedelta(days=d.weekday())).strftime("%Y-%m-%d")
        week_counts[week][r["major"]] += 1
        if r["version"] in fix_only:
            week_fixonly[week][r["major"]] += 1
        notes = notes_by_version.get(r["version"])
        if notes:
            total, fixes, non_fixes = notes
            week_notes_nf[week][r["major"]] += non_fixes
            week_notes_fx[week][r["major"]] += fixes

    weeks: list[str] = sorted(week_counts.keys())

    def to_lists(
        src: defaultdict[str, defaultdict[str, int]],
        subtrahend: defaultdict[str, defaultdict[str, int]] | None = None,
    ) -> dict[str, list[int]]:
        if subtrahend:
            return {
                m: [src[w].get(m, 0) - subtrahend[w].get(m, 0) for w in weeks]
                for m in majors_order
            }
        return {m: [src[w].get(m, 0) for w in weeks] for m in majors_order}

    return (
        weeks,
        to_lists(week_counts, week_fixonly),
        to_lists(week_fixonly),
        to_lists(week_notes_nf),
        to_lists(week_notes_fx),
    )


def _compute_major_stats(
    releases: list[dict],
    majors_order: list[str],
) -> dict[str, MajorStats]:
    """Compute per-major-version statistics."""
    by_major: defaultdict[str, list[dict]] = defaultdict(list)
    for r in releases:
        by_major[r["major"]].append(r)

    stats: dict[str, MajorStats] = {}
    for major in majors_order:
        mrs = by_major[major]
        if len(mrs) > 1:
            span = (mrs[-1]["dt_pac"] - mrs[0]["dt_pac"]).total_seconds() / 86400
        else:
            span = 0
        stats[major] = {
            "count": len(mrs),
            "span_days": round(span, 1),
            "first": mrs[0]["date"],
            "last": mrs[-1]["date"],
        }
    return stats


def _compute_notes_data(
    releases: list[dict],
    notes_by_version: dict[str, tuple[int, int, int]],
) -> list[NotesRecord]:
    """Build release notes records for versions with changelog entries."""
    result: list[NotesRecord] = []
    for r in releases:
        notes = notes_by_version.get(r["version"])
        if notes:
            t, f, nf = notes
            result.append(
                {
                    "version": r["version"],
                    "timestamp": r["timestamp"],
                    "major": r["major"],
                    "total": t,
                    "fixes": f,
                    "non_fixes": nf,
                }
            )
    return result


def _compute_heatmap_dow_hour(
    releases: list[dict],
    notes_by_version: dict[str, tuple[int, int, int]],
) -> tuple[list[list[int]], list[list[int]]]:
    """Build DOW x Hour heatmaps from changelog entry counts.

    Returns (totals_7x24, fixes_7x24) where rows are Mon=0..Sun=6
    and columns are hours 0..23.
    """
    totals: list[list[int]] = [[0] * 24 for _ in range(7)]
    fixes: list[list[int]] = [[0] * 24 for _ in range(7)]
    for r in releases:
        notes = notes_by_version.get(r["version"])
        if not notes:
            continue
        total, fix_count, _ = notes
        dow: int = r["dt_pac"].weekday()
        hour: int = r["dt_pac"].hour
        totals[dow][hour] += total
        fixes[dow][hour] += fix_count
    return totals, fixes


def _compute_size_data(
    releases: list[dict],
    npm_sizes: dict[str, dict[str, int]],
) -> list[SizeRecord]:
    """Build size records for versions that have npm dist size info."""
    result: list[SizeRecord] = []
    for r in releases:
        size_info = npm_sizes.get(r["version"])
        if size_info and size_info.get("unpackedSize"):
            result.append(
                {
                    "version": r["version"],
                    "timestamp": r["timestamp"],
                    "major": r["major"],
                    "unpacked_size": size_info["unpackedSize"],
                    "file_count": size_info.get("fileCount", 0),
                }
            )
    return result


# --- Main entry point ---


def compute_all(
    npm_times: dict[str, str],
    changelog: dict[str, str] | None = None,
    npm_sizes: dict[str, dict[str, int]] | None = None,
) -> ComputedData:
    """Compute all derived statistics from raw npm timestamps and changelog."""
    merged_times = _merge_changelog_versions(npm_times, changelog)
    _releases = _build_releases(merged_times)
    majors_order = _extract_majors_order(_releases)
    notes_by_version, fix_only = _build_notes_lookup(changelog)

    # Weekly aggregations (releases + notes counts, single pass)
    (
        week_labels,
        week_stacked,
        week_stacked_fixonly,
        week_notes_stacked,
        week_notes_stacked_fixes,
    ) = _compute_weekly(_releases, majors_order, fix_only, notes_by_version)

    # DOW and hour stacking via shared helper
    dow_stacked, dow_stacked_fixonly = _stacked_by_major(
        _releases, majors_order, fix_only, lambda r: r["dt_pac"].weekday(), range(7)
    )

    hour_stacked, hour_stacked_fixonly = _stacked_by_major(
        _releases, majors_order, fix_only, lambda r: r["dt_pac"].hour, range(24)
    )

    # Heatmap: DOW x Hour from changelog entry counts
    heatmap_totals, heatmap_fixes = _compute_heatmap_dow_hour(
        _releases, notes_by_version
    )

    # Package size data
    size_data: list[SizeRecord] = _compute_size_data(_releases, npm_sizes or {})

    # Generated timestamp
    generated_at: str = to_pacific(datetime.now(timezone.utc)).strftime(
        "%Y-%m-%d %H:%M %Z"
    )

    releases: list[Release] = [
        {
            "version": r["version"],
            "timestamp": r["timestamp"],
            "date": r["date"],
            "major": r["major"],
        }
        for r in _releases
    ]

    return {
        "releases": releases,
        "gaps": _compute_gaps(_releases),
        "week_labels": week_labels,
        "week_stacked": week_stacked,
        "week_stacked_fixonly": week_stacked_fixonly,
        "week_notes_stacked": week_notes_stacked,
        "week_notes_stacked_fixes": week_notes_stacked_fixes,
        "dow_stacked": dow_stacked,
        "dow_stacked_fixonly": dow_stacked_fixonly,
        "hour_stacked": hour_stacked,
        "hour_stacked_fixonly": hour_stacked_fixonly,
        "major_stats": _compute_major_stats(_releases, majors_order),
        "majors_order": majors_order,
        "total_count": len(releases),
        "first_date": releases[0]["date"] if releases else "",
        "last_date": releases[-1]["date"] if releases else "",
        "notes_data": _compute_notes_data(_releases, notes_by_version),
        "notes_count": len(notes_by_version),
        "heatmap_dow_hour": heatmap_totals,
        "heatmap_dow_hour_fixes": heatmap_fixes,
        "size_data": size_data,
        "generated_at": generated_at,
    }
