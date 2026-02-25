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
make install-hooks  # install pre-commit git hooks (one-time)
make help           # show all targets
```

CLI flags (via `uv run python -m claude_code_release_cadence`):

- _(default)_ — fetch fresh data, then build
- `--fetch-only` — fetch data without building
- `--build-only` — build from existing data without fetching
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
make lint           # all linters: ruff + prettier (no changes)
make format         # all formatters: ruff + prettier
make lint-py        # ruff check + format check only
make format-py      # ruff auto-fix + format only
make lint-md        # prettier --check on *.md files
make format-md      # prettier --write on *.md files
make lint-css       # prettier --check on CSS files
make format-css     # prettier --write on CSS files
make lint-js        # prettier --check on JS files
make format-js      # prettier --write on JS files
```

Ruff rules: E, F, W, I (errors, pyflakes, warnings, import sorting). Target: Python 3.12.
Prettier formats Markdown, CSS, and JS files (`.prettierrc` at project root; `singleQuote: true` for JS).

### Pre-commit Hooks

`pre-commit` auto-fixes formatting (prettier for Markdown/CSS/JS, ruff for Python), auto-bumps the version, then runs mypy and pytest. Install once with `make install-hooks`. To bypass temporarily: `git commit --no-verify`.

**Before committing**, always run:

```
make bump-version && git add pyproject.toml uv.lock
```

then stage your changes and commit. If you skip this, the pre-commit hook will bump the version and fail, requiring you to re-stage `pyproject.toml` and `uv.lock` and commit again.

## Architecture

Source lives in `src/claude_code_release_cadence/`. Five-stage pipeline orchestrated by `__main__.py`:

1. **Fetch** (`fetch.py`) — downloads npm registry metadata and CHANGELOG.md via urllib; 30s timeout, 50MB response limit
2. **Parse** (`parse.py`) — loads JSON timestamps, package sizes, and markdown changelog sections into dicts
3. **Compute** (`compute.py`) — the core engine; classifies versions into major series, detects fix-only releases via `FIX_PATTERN` regex, computes gaps/distributions/heatmaps; returns a `ComputedData` TypedDict (defined at top of file with all sub-TypedDicts)
4. **Render** (`render.py`) — assembles the dashboard from template partials and injects computed data. First resolves `{{INLINE:filename}}` markers to inline CSS/JS files, then replaces data placeholders with HTML-safe JSON
5. **Export** (`export.py`) — writes `data.json`, `releases.csv`, `notes.json` to `data/cooked/`

Supporting modules:

- `config.py` — color palette assignment for major version series
- `tz.py` — UTC to US Pacific timezone conversion

Template partials in `templates/`:

- `dashboard.template.html` — HTML skeleton with `{{INLINE:...}}` markers and `{{PLACEHOLDER}}` values
- `dashboard.css` — all CSS (plain, no placeholders; formatted by prettier)
- `theme-init.js` — theme initialization IIFE (no placeholders)
- `colors.js` — injected data declarations, `getTheme()`, color palette, hatch patterns
- `chart-helpers.js` — shared Chart.js utilities, defaults, series-label plugin
- `stats.js` — trend computation (28-day window) and stats cards
- `charts.js` — scatter plot and four stacked bar charts
- `notes-overlay.js` — changelog entries per release chart with outlier capping and overlay system
- `heatmap.js` — DOW×Hour heatmap grid with keyboard nav and theme update
- `init.js` — major version table, package size chart, footer, theme toggle, anchor links

## Key Conventions

- **Zero runtime dependencies** — stdlib only (urllib, json, csv, datetime, collections, re, pathlib, zoneinfo)
- **Date-based versioning** (`YYYY.MM.DD.HHMM` America/Los_Angeles) in `pyproject.toml` — **always run `make bump-version && git add pyproject.toml uv.lock` before `git commit`** to avoid the pre-commit hook failing and requiring a re-stage/re-commit cycle
- **TypedDict for data structures** — all inter-module data contracts defined in `compute.py`
- **mypy** with `warn_return_any` and `warn_unused_configs` enabled
- **Version series classification** — pre-1.0 uses minor (`0.2.x`), post-1.0 uses major.minor (`2.1.x`); see `classify_major()`

## Data & Generated Files

Fetched to `data/raw/` (gitignored): `npm-times.json`, `npm-sizes.json`, `CHANGELOG.md`

Generated outputs (gitignored): `public/index.html` (Chart.js dashboard), `data/cooked/data.json`, `data/cooked/notes.json`, `data/cooked/releases.csv`

`npm-sizes.json` is optional — the build runs without it (sizes will be blank).

CI runs tests on every push/PR (`test.yml`) and deploys `public/` to GitHub Pages nightly at ~midnight US/Pacific (08:00 UTC), on push to main, and via `workflow_dispatch`.

`GA_MEASUREMENT_ID` env var (optional) — injects GA4 gtag.js snippet into the dashboard. Set as a GitHub Actions secret for deploys; omitted locally.
