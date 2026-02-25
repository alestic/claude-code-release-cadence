"""Tests for HTML template rendering."""
# [Created with AI: Claude Code with Opus 4.6]

from pathlib import Path

import pytest

from claude_code_release_cadence.render import _inline_partials, _json_for_html


def test_json_for_html_escapes_lt() -> None:
    """< should be escaped to prevent breaking script tags."""
    assert "\\u003c" in _json_for_html("<script>")


def test_json_for_html_escapes_gt() -> None:
    """> should be escaped."""
    assert "\\u003e" in _json_for_html("</script>")


def test_json_for_html_escapes_amp() -> None:
    """& should be escaped."""
    assert "\\u0026" in _json_for_html("a&b")


def test_json_for_html_preserves_normal_text() -> None:
    """Normal strings should round-trip through JSON."""
    assert _json_for_html("hello world") == '"hello world"'


def test_json_for_html_handles_dict() -> None:
    """Dict values should serialize to JSON."""
    result = _json_for_html({"key": "value"})
    assert '"key"' in result
    assert '"value"' in result


def test_json_for_html_handles_list() -> None:
    """List values should serialize to JSON."""
    result = _json_for_html([1, 2, 3])
    assert result == "[1, 2, 3]"


def test_inline_partials_replaces_marker(tmp_path: Path) -> None:
    """{{INLINE:filename}} markers should be replaced with file contents."""
    (tmp_path / "part.txt").write_text("hello world")
    result = _inline_partials("before {{INLINE:part.txt}} after", tmp_path)
    assert result == "before hello world after"


def test_inline_partials_multiple(tmp_path: Path) -> None:
    """Multiple INLINE markers should all be resolved."""
    (tmp_path / "a.css").write_text("body{}")
    (tmp_path / "b.js").write_text("var x=1;")
    result = _inline_partials(
        "<style>{{INLINE:a.css}}</style><script>{{INLINE:b.js}}</script>",
        tmp_path,
    )
    assert "body{}" in result
    assert "var x=1;" in result


def test_inline_partials_missing_file(tmp_path: Path) -> None:
    """Missing partial file should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        _inline_partials("{{INLINE:missing.txt}}", tmp_path)
