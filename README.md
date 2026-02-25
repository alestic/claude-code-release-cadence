<!-- [Created with AI: Claude Code with Opus 4.6] -->

# claude-code-release-cadence

Analyze and visualize the release cadence of [Claude Code](https://github.com/anthropics/claude-code) (`@anthropic-ai/claude-code` on npm).

Generates an interactive dashboard showing release frequency, day-of-week and hour-of-day patterns, version series breakdowns, fix-vs-feature classification, and per-series statistics.

> **Disclaimer:** This is an independent project. It is not affiliated with, endorsed by, or sponsored by Anthropic.

> **Caveat:** The accuracy of the generated data and graphs have not been verified. This is presented for entertainment value only.

## Prerequisites

- Python 3.12+

## Quick run (no clone needed)

```
uvx --from git+https://github.com/alestic/claude-code-release-cadence claude-code-release-cadence
```

This fetches data, builds the dashboard, and writes output to the current directory.

## Quickstart (local development)

```
make install-dev    # create venv and install
make all            # fetch data + build dashboard
make open           # open dashboard in browser
```

Or step by step:

```
make install-dev    # one-time setup
make fetch          # download fresh data from npm registry and GitHub (required before first build)
make build          # generate dashboard and exports (requires fetched data)
```

## What it produces

| Output                     | Description                                                                    |
| -------------------------- | ------------------------------------------------------------------------------ |
| `public/index.html`        | Interactive dashboard (open in any browser)                                    |
| `data/cooked/data.json`    | All computed statistics as JSON                                                |
| `data/cooked/notes.json`   | Release notes with bullet counts and full text                                 |
| `data/cooked/releases.csv` | Flat release list (version, date, timestamp, major, unpacked_size, file_count) |

All outputs are generated from two public data sources:

- [npm: @anthropic-ai/claude-code](https://www.npmjs.com/package/@anthropic-ai/claude-code) -- publish timestamps for every version
- [GitHub: CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) -- release notes from the Claude Code GitHub repo

## Development

```
make test           # run mypy type checking + pytest
make lint           # run all linters: ruff + prettier (no changes)
make format         # run all formatters: ruff + prettier
make bump-version   # bump version to current timestamp (run before committing)
make clean          # remove public/ and data/cooked/
make purge          # remove public/, data/, venv, caches
make help           # show all targets
```

## Analytics

The deployed dashboard supports Google Analytics 4. To enable it, add a
`GA_MEASUREMENT_ID` repository secret (Settings > Secrets > Actions) with
your `G-XXXXXXXXXX` measurement ID. Local builds omit the tracking snippet.

## How it works

1. Fetch -- downloads npm package metadata and CHANGELOG.md via HTTP
2. Parse -- extracts version timestamps and release note sections
3. Compute -- classifies versions into series, detects fix-only releases, computes gaps/distributions/statistics
4. Render -- injects computed data into a Chart.js HTML template
5. Export -- writes JSON and CSV files

## Attribution

Created with AI: Claude Code with Opus 4.6

Directed by: [Eric Hammond](https://esh.dev/)

## License

Apache 2.0. See [LICENSE](LICENSE).
