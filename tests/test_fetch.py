"""Tests for fetch module helpers."""
# [Created with AI: Claude Code with Opus 4.6]

import io

import pytest

from claude_code_release_cadence.fetch import _read_limited


class FakeResponse(io.BytesIO):
    """Minimal file-like object mimicking urllib response.read()."""

    pass


def test_read_limited_within_limit() -> None:
    """Data within limit should be returned in full."""
    resp = FakeResponse(b"hello world")
    result = _read_limited(resp, max_bytes=100)
    assert result == b"hello world"


def test_read_limited_exactly_at_limit() -> None:
    """Data exactly at the limit should succeed."""
    data = b"x" * 50
    resp = FakeResponse(data)
    result = _read_limited(resp, max_bytes=50)
    assert result == data


def test_read_limited_exceeds_limit() -> None:
    """Data exceeding the limit should raise ValueError."""
    data = b"x" * 101
    resp = FakeResponse(data)
    with pytest.raises(ValueError, match="exceeds"):
        _read_limited(resp, max_bytes=100)


def test_read_limited_empty_response() -> None:
    """Empty response should return empty bytes."""
    resp = FakeResponse(b"")
    result = _read_limited(resp, max_bytes=100)
    assert result == b""
