"""HTML template rendering."""
# [Created with AI: Claude Code with Opus 4.6]

import json
import logging
import re
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


def _inline_partials(html: str, template_dir: Path) -> str:
    """Replace ``{{INLINE:filename}}`` markers with file contents."""

    def _replace(m: re.Match[str]) -> str:
        return (template_dir / m.group(1)).read_text()

    return re.sub(r"\{\{INLINE:([^}]+)\}\}", _replace, html)


# Keys in ComputedData that map directly to "__DATA_<KEY>__" JSON placeholders
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
    colors_dark: dict[str, str],
    colors_light: dict[str, str],
    *,
    ga_measurement_id: str = "",
) -> None:
    """Render HTML dashboard from template and computed data.

    First inlines partial files (CSS, JS) via ``{{INLINE:filename}}``
    markers, then replaces data placeholders with JSON-serialized or
    string values.
    """
    with open(template_path) as f:
        html: str = f.read()

    # Phase 1: inline partial files from the templates directory
    html = _inline_partials(html, template_path.parent)

    # Phase 2: replace data and metadata placeholders
    # JS data placeholders use '__DATA_KEY__' (quoted in source to keep JS valid)
    replacements: dict[str, str] = {
        f"'__DATA_{k.upper()}__'": _json_for_html(data[k])  # type: ignore[literal-required]
        for k in _JSON_KEYS
        if k != "releases"
    }
    # Strip date/major from releases — JS only uses version, timestamp, length
    replacements["'__DATA_RELEASES__'"] = _json_for_html(
        [
            {"version": r["version"], "timestamp": r["timestamp"]}
            for r in data["releases"]
        ]
    )
    replacements["'__DATA_COLORS_DARK__'"] = _json_for_html(colors_dark)
    replacements["'__DATA_COLORS_LIGHT__'"] = _json_for_html(colors_light)
    # JS string placeholder (inside an existing JS string literal)
    replacements["__GENERATED_AT__"] = data["generated_at"]

    # HTML placeholders use {{KEY}} syntax
    replacements.update(
        {
            "{{GA_SNIPPET}}": _ga_snippet(ga_measurement_id),
            "{{TOTAL_COUNT}}": str(data["total_count"]),
            "{{FIRST_DATE}}": data["first_date"],
            "{{LAST_DATE}}": data["last_date"],
            "{{NOTES_COUNT}}": str(data["notes_count"]),
            "{{VERSION}}": ".".join(
                f"{int(p):02d}" if i else p
                for i, p in enumerate(
                    pkg_version("claude-code-release-cadence").split(".")
                )
            ),
        }
    )

    for key, value in replacements.items():
        if key not in html:
            log.warning("placeholder %s not found in template", key)
        html = html.replace(key, value)

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
