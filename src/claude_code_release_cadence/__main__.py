#!/usr/bin/env python3
"""CLI entry point for the Claude Code release cadence dashboard.

Usage::

    claude-code-release-cadence                 # build from existing data
    claude-code-release-cadence --fetch         # fetch fresh data, then build
    claude-code-release-cadence --fetch-only    # fetch data without building
"""
# [Created with AI: Claude Code with Opus 4.6]

import argparse
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

# Project paths (relative to repo root; src/claude_code_release_cadence/ → repo)
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
DATA_DIR: Path = BASE_DIR / "data" / "raw"
COOKED_DIR: Path = BASE_DIR / "data" / "cooked"
PUBLIC_DIR: Path = BASE_DIR / "public"
TEMPLATE_DIR: Path = BASE_DIR / "templates"

# Input files
NPM_TIMES: Path = DATA_DIR / "npm-times.json"
NPM_SIZES: Path = DATA_DIR / "npm-sizes.json"
CHANGELOG: Path = DATA_DIR / "CHANGELOG.md"
TEMPLATE: Path = TEMPLATE_DIR / "dashboard.template.html"

# Output files
OUTPUT_HTML: Path = PUBLIC_DIR / "index.html"
OUTPUT_DATA_JSON: Path = COOKED_DIR / "data.json"
OUTPUT_RELEASES_CSV: Path = COOKED_DIR / "releases.csv"
OUTPUT_NOTES_JSON: Path = COOKED_DIR / "notes.json"


log: logging.Logger = logging.getLogger(__name__)


def do_fetch() -> None:
    """Fetch all raw data sources."""
    fetch_npm_data(NPM_TIMES, NPM_SIZES)
    fetch_changelog(CHANGELOG)
    log.info("Fetch complete.")


def do_build() -> None:
    """Build dashboard HTML and exports from existing data."""
    missing: list[Path] = [
        p for p in [NPM_TIMES, CHANGELOG, TEMPLATE] if not p.exists()
    ]
    if missing:
        for p in missing:
            log.error("Missing required file: %s", p)
        log.error("Run with --fetch first.")
        sys.exit(1)

    log.info("Loading data...")
    npm_times: dict[str, str] = load_npm_times(NPM_TIMES)
    changelog: dict[str, str] = load_changelog(CHANGELOG)
    npm_sizes: dict[str, dict[str, int]] = load_npm_sizes(NPM_SIZES)

    log.info("Computing statistics (%d versions)...", len(npm_times))
    data: ComputedData = compute_all(
        npm_times, changelog=changelog, npm_sizes=npm_sizes
    )

    colors: dict[str, str] = assign_colors(data["majors_order"])

    ga_id: str = os.environ.get("GA_MEASUREMENT_ID", "")

    log.info("Rendering dashboard...")
    render(TEMPLATE, OUTPUT_HTML, data, colors, ga_measurement_id=ga_id)

    log.info("Exporting data...")
    export_json(data, OUTPUT_DATA_JSON)
    export_releases_csv(
        data["releases"], OUTPUT_RELEASES_CSV, size_data=data["size_data"]
    )
    export_notes_json(data["notes_data"], changelog, OUTPUT_NOTES_JSON)

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
        "--fetch",
        action="store_true",
        help="fetch fresh data before building",
    )
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        help="fetch data without building",
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
        if args.fetch or args.fetch_only:
            do_fetch()
        if not args.fetch_only:
            do_build()
    except Exception:
        log.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
