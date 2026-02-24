# CLAUDE.md

<!-- [Created with AI: Claude Code with Opus 4.6] -->

Analyzes and visualizes the npm release cadence of `@anthropic-ai/claude-code`.

## Prerequisites

Requires Python 3.12 and [`uv`](https://docs.astral.sh/uv/).

## Build & Development

Package manager is `uv`. All commands go through the Makefile:

```
make install-dev    # create venv and install dev dependencies (one-time)
make fetch          # download fresh data from npm registry and GitHub
make build          # generate dashboard and exports from existing data
make all            # fetch + build in one step
make open           # open dashboard in browser
make clean          # remove build output (public/, data/cooked/)
make purge          # clean + remove venv, raw data, and caches
make help           # show all targets
```

CLI flags (via `uv run python -m claude_code_release_cadence`):
- `--fetch` — fetch fresh data, then build
- `--fetch-only` — fetch data without building
- `-v` / `--verbose` — enable debug logging

### Testing

```
make test           # mypy type checking + pytest
make test-typing    # mypy only
make test-unit      # pytest only
```

Run a single test:
```
uv run pytest tests/test_compute.py::test_classify_major_0x -v
```

### Linting & Formatting

```
make lint           # ruff check + format check (no changes)
make format         # ruff auto-fix + format
```

Ruff rules: E, F, W, I (errors, pyflakes, warnings, import sorting). Target: Python 3.12.

## Architecture

Source lives in `src/claude_code_release_cadence/`. Five-stage pipeline orchestrated by `__main__.py`:

1. **Fetch** (`fetch.py`) — downloads npm registry metadata and CHANGELOG.md via urllib; 30s timeout, 50MB response limit
2. **Parse** (`parse.py`) — loads JSON timestamps, package sizes, and markdown changelog sections into dicts
3. **Compute** (`compute.py`) — the core engine; classifies versions into major series, detects fix-only releases via `FIX_PATTERN` regex, computes gaps/distributions/heatmaps; returns a `ComputedData` TypedDict (defined at top of file with all sub-TypedDicts)
4. **Render** (`render.py`) — injects computed data into `templates/dashboard.template.html` via `{{PLACEHOLDER}}` substitution with HTML-safe JSON escaping
5. **Export** (`export.py`) — writes `data.json`, `releases.csv`, `notes.json` to `data/cooked/`

Supporting modules:
- `config.py` — color palette assignment for major version series
- `tz.py` — UTC to US Pacific timezone conversion

## Key Conventions

- **Zero runtime dependencies** — stdlib only (urllib, json, csv, datetime, collections, re, pathlib, zoneinfo)
- **Date-based versioning** (`YYYY.MM.DD`) in `pyproject.toml` — **always bump to today's date after making changes**, then run `uv sync --dev` to update `uv.lock`
- **TypedDict for data structures** — all inter-module data contracts defined in `compute.py`
- **mypy** with `warn_return_any` and `warn_unused_configs` enabled
- **Version series classification** — pre-1.0 uses minor (`0.2.x`), post-1.0 uses major.minor (`2.1.x`); see `classify_major()`

## Data & Generated Files

Fetched to `data/raw/` (gitignored): `npm-times.json`, `npm-sizes.json`, `CHANGELOG.md`

Generated outputs (gitignored): `public/index.html` (Chart.js dashboard), `data/cooked/data.json`, `data/cooked/notes.json`, `data/cooked/releases.csv`

`npm-sizes.json` is optional — the build runs without it (sizes will be blank).

CI runs tests on every push/PR (`test.yml`) and deploys `public/` to GitHub Pages nightly at ~midnight US/Pacific (08:00 UTC), on push to main, and via `workflow_dispatch`.

`GA_MEASUREMENT_ID` env var (optional) — injects GA4 gtag.js snippet into the dashboard. Set as a GitHub Actions secret for deploys; omitted locally.
