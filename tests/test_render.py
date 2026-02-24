"""Tests for HTML template rendering."""
# [Created with AI: Claude Code with Opus 4.6]

from claude_code_release_cadence.render import _json_for_html


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
