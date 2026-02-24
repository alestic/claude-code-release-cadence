"""HTML template rendering."""
# [Created with AI: Claude Code with Opus 4.6]

import json
import logging
from importlib.metadata import version as pkg_version
from pathlib import Path

from .compute import ComputedData

log: logging.Logger = logging.getLogger(__name__)

_GA_SNIPPET_TEMPLATE: str = (
    '<script async src="https://www.googletagmanager.com/gtag/js?id={mid}"></script>'
    "<script>window.dataLayer=window.dataLayer||[];"
    "function gtag(){{dataLayer.push(arguments)}}"
    'gtag("js",new Date());gtag("config","{mid}")</script>\n'
)


def _ga_snippet(measurement_id: str) -> str:
    """Return the gtag.js snippet for a GA4 measurement ID, or empty string."""
    if not measurement_id:
        return ""
    return _GA_SNIPPET_TEMPLATE.format(mid=measurement_id)


def _json_for_html(obj: object) -> str:
    """Serialize to JSON safe for embedding inside HTML <script> tags.

    Escapes <, >, & to prevent breaking out of script context.
    """
    return (
        json.dumps(obj)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


# Keys in ComputedData that map directly to DATA_<KEY> JSON placeholders
_JSON_KEYS: list[str] = [
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
    "notes_data",
    "heatmap_dow_hour",
    "heatmap_dow_hour_fixes",
    "size_data",
]


def render(
    template_path: Path,
    output_path: Path,
    data: ComputedData,
    colors: dict[str, str],
    *,
    ga_measurement_id: str = "",
) -> None:
    """Render HTML dashboard from template and computed data.

    Replaces ``{{PLACEHOLDER}}`` markers in the template with
    JSON-serialized or string values.
    """
    with open(template_path) as f:
        html: str = f.read()

    # Build replacements: JSON data keys + string scalars + colors
    replacements: dict[str, str] = {
        f"DATA_{k.upper()}": _json_for_html(data[k])  # type: ignore[literal-required]
        for k in _JSON_KEYS
    }
    replacements.update(
        {
            "GA_SNIPPET": _ga_snippet(ga_measurement_id),
            "DATA_COLORS": _json_for_html(colors),
            "TOTAL_COUNT": str(data["total_count"]),
            "FIRST_DATE": data["first_date"],
            "LAST_DATE": data["last_date"],
            "NOTES_COUNT": str(data["notes_count"]),
            "GENERATED_AT": data["generated_at"],
            "VERSION": ".".join(
                f"{int(p):02d}" if i else p
                for i, p in enumerate(
                    pkg_version("claude-code-release-cadence").split(".")
                )
            ),
        }
    )

    for key, value in replacements.items():
        placeholder: str = "{{" + key + "}}"
        if placeholder not in html:
            log.warning("placeholder %s not found in template", placeholder)
        html = html.replace(placeholder, value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    log.info(
        "Generated %s (%d releases, %s to %s)",
        output_path,
        data["total_count"],
        data["first_date"],
        data["last_date"],
    )
