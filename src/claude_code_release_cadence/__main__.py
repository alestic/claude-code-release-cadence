#!/usr/bin/env python3
"""CLI entry point for the Claude Code release cadence dashboard.

Usage::

    claude-code-release-cadence                 # fetch fresh data and build
    claude-code-release-cadence --build-only    # build from existing data
    claude-code-release-cadence --fetch-only    # fetch data without building
"""
# [Created with AI: Claude Code with Opus 4.6]

import argparse
import importlib.resources
import logging
import os
import sys
from importlib.metadata import version as pkg_version
from pathlib import Path

from .compute import ComputedData, compute_all
from .config import assign_colors
from .export import export_json, export_notes_json, export_releases_csv
from .fetch import fetch_changelog, fetch_npm_data
from .parse import load_changelog, load_npm_sizes, load_npm_times
from .render import render

PROGRAM_NAME: str = "claude-code-release-cadence"
LOG_FORMAT: str = f"%(asctime)s [{PROGRAM_NAME}] [%(levelname)s] %(message)s"
LOG_FORMAT_DATE: str = "%Y-%m-%d %H:%M:%S"

# Template is bundled inside the package
TEMPLATE: Path = Path(
    str(
        importlib.resources.files(__package__).joinpath(
            "templates/dashboard.template.html"
        )
    )
)


def _cwd_paths() -> tuple[Path, Path, Path, Path, Path, Path, Path, Path]:
    """Resolve data/output paths relative to CWD at call time.

    Returns (npm_times, npm_sizes, changelog, output_html,
             output_data_json, output_releases_csv, output_notes_json, template).
    """
    cwd: Path = Path.cwd()
    data_dir: Path = cwd / "data" / "raw"
    cooked_dir: Path = cwd / "data" / "cooked"
    public_dir: Path = cwd / "public"
    return (
        data_dir / "npm-times.json",
        data_dir / "npm-sizes.json",
        data_dir / "CHANGELOG.md",
        public_dir / "index.html",
        cooked_dir / "data.json",
        cooked_dir / "releases.csv",
        cooked_dir / "notes.json",
        TEMPLATE,
    )


log: logging.Logger = logging.getLogger(__name__)


def do_fetch() -> None:
    """Fetch all raw data sources."""
    npm_times_path, npm_sizes_path, changelog_path, *_ = _cwd_paths()
    fetch_npm_data(npm_times_path, npm_sizes_path)
    fetch_changelog(changelog_path)
    log.info("Fetch complete.")


def do_build() -> None:
    """Build dashboard HTML and exports from existing data."""
    (
        npm_times_path,
        npm_sizes_path,
        changelog_path,
        output_html,
        output_data_json,
        output_releases_csv,
        output_notes_json,
        template,
    ) = _cwd_paths()

    missing: list[Path] = [
        p for p in [npm_times_path, changelog_path, template] if not p.exists()
    ]
    if missing:
        for p in missing:
            log.error("Missing required file: %s", p)
        log.error("Run without --build-only to fetch data first.")
        sys.exit(1)

    log.info("Loading data...")
    npm_times: dict[str, str] = load_npm_times(npm_times_path)
    changelog: dict[str, str] = load_changelog(changelog_path)
    npm_sizes: dict[str, dict[str, int]] = load_npm_sizes(npm_sizes_path)

    log.info("Computing statistics (%d versions)...", len(npm_times))
    data: ComputedData = compute_all(
        npm_times, changelog=changelog, npm_sizes=npm_sizes
    )

    colors: dict[str, str] = assign_colors(data["majors_order"])

    ga_id: str = os.environ.get("GA_MEASUREMENT_ID", "")

    log.info("Exporting data...")
    export_json(data, output_data_json)
    export_releases_csv(
        data["releases"], output_releases_csv, size_data=data["size_data"]
    )
    export_notes_json(data["notes_data"], changelog, output_notes_json)

    log.info("Rendering dashboard...")
    render(template, output_html, data, colors, ga_measurement_id=ga_id)

    log.info("Build complete.")


def main() -> None:
    """Main CLI entry point."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description="Generate Claude Code release cadence dashboard.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {pkg_version('claude-code-release-cadence')}",
    )
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        help="fetch data without building",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="build from existing data without fetching",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug logging",
    )
    args: argparse.Namespace = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_FORMAT_DATE,
    )

    try:
        if not args.build_only:
            do_fetch()
        if not args.fetch_only:
            do_build()
    except Exception:
        log.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
