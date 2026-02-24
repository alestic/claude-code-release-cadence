"""Fetch raw data from npm registry and GitHub."""
# [Created with AI: Claude Code with Opus 4.6]

import json
import logging
import urllib.request
from pathlib import Path

log: logging.Logger = logging.getLogger(__name__)

NPM_REGISTRY_URL: str = "https://registry.npmjs.org/@anthropic-ai/claude-code"
CHANGELOG_URL: str = (
    "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
)

REQUEST_TIMEOUT: int = 30  # seconds
MAX_RESPONSE_BYTES: int = 50 * 1024 * 1024  # 50 MB


def _read_limited(
    resp: "urllib.response.addinfourl", max_bytes: int = MAX_RESPONSE_BYTES
) -> bytes:
    """Read an HTTP response with a size limit.

    Raises:
        ValueError: If the response exceeds max_bytes.
    """
    data: bytes = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"Response exceeds {max_bytes} byte limit")
    return data


def fetch_npm_data(
    npm_times_path: Path,
    npm_sizes_path: Path,
) -> None:
    """Fetch npm package metadata and extract timestamps and sizes.

    Makes a single HTTP call to the npm registry and extracts:
    - ``time`` field → npm-times.json (version → ISO timestamp)
    - ``versions[*].dist.{unpackedSize, fileCount}`` → npm-sizes.json

    Args:
        npm_times_path: Where to save npm-times.json.
        npm_sizes_path: Where to save npm-sizes.json.

    Raises:
        urllib.error.URLError: If the HTTP request fails.
    """
    log.info("Fetching npm package data from registry...")
    npm_times_path.parent.mkdir(parents=True, exist_ok=True)
    npm_sizes_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(NPM_REGISTRY_URL, timeout=REQUEST_TIMEOUT) as resp:
        raw: dict = json.loads(_read_limited(resp))

    # Extract timestamps
    times: dict[str, str] = raw.get("time", {})
    times.pop("created", None)
    times.pop("modified", None)
    with open(npm_times_path, "w") as f:
        json.dump(times, f, indent=2)
    log.info("Saved %s (%d versions)", npm_times_path, len(times))

    # Extract sizes from versions[*].dist
    sizes: dict[str, dict[str, int]] = {}
    versions: dict = raw.get("versions", {})
    for ver, meta in versions.items():
        dist: dict = meta.get("dist", {})
        unpacked: int | None = dist.get("unpackedSize")
        if unpacked is not None:
            sizes[ver] = {
                "unpackedSize": unpacked,
                "fileCount": dist.get("fileCount", 0),
            }
    with open(npm_sizes_path, "w") as f:
        json.dump(sizes, f, indent=2)
    log.info("Saved %s (%d versions with size data)", npm_sizes_path, len(sizes))


def fetch_changelog(
    output_path: Path,
    url: str = CHANGELOG_URL,
) -> None:
    """Fetch CHANGELOG.md from GitHub via HTTP.

    Args:
        output_path: Where to save CHANGELOG.md.
        url: URL to fetch from.
    """
    log.info("Fetching CHANGELOG.md...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as resp:
        data: bytes = _read_limited(resp)
    with open(output_path, "wb") as f:
        f.write(data)
    log.info("Saved %s", output_path)
