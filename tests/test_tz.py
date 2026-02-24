"""Tests for timezone conversion."""
# [Created with AI: Claude Code with Opus 4.6]

from datetime import datetime, timezone

from claude_code_release_cadence.tz import to_pacific


def test_pst_winter() -> None:
    """Winter time (PST = UTC-8)."""
    dt_utc: datetime = datetime(2025, 1, 15, 20, 0, 0, tzinfo=timezone.utc)
    result: datetime = to_pacific(dt_utc)
    assert result.hour == 12
    assert result.day == 15


def test_pdt_summer() -> None:
    """Summer time (PDT = UTC-7)."""
    dt_utc: datetime = datetime(2025, 7, 15, 20, 0, 0, tzinfo=timezone.utc)
    result: datetime = to_pacific(dt_utc)
    assert result.hour == 13
    assert result.day == 15


def test_dst_spring_forward_before() -> None:
    """Just before DST starts (2025: March 9, 2am PST = 10am UTC)."""
    # 9:59 UTC on March 9 is still PST
    dt_utc: datetime = datetime(2025, 3, 9, 9, 59, 0, tzinfo=timezone.utc)
    result: datetime = to_pacific(dt_utc)
    assert result.hour == 1  # 1:59am PST


def test_dst_spring_forward_after() -> None:
    """Just after DST starts (2025: March 9, 2am PST = 10am UTC)."""
    # 10:01 UTC on March 9 is PDT
    dt_utc: datetime = datetime(2025, 3, 9, 10, 1, 0, tzinfo=timezone.utc)
    result: datetime = to_pacific(dt_utc)
    assert result.hour == 3  # 3:01am PDT (skips 2am)


def test_dst_fall_back_before() -> None:
    """Just before DST ends (2025: November 2, 2am PDT = 9am UTC)."""
    # 8:59 UTC on Nov 2 is still PDT
    dt_utc: datetime = datetime(2025, 11, 2, 8, 59, 0, tzinfo=timezone.utc)
    result: datetime = to_pacific(dt_utc)
    assert result.hour == 1  # 1:59am PDT


def test_dst_fall_back_after() -> None:
    """Just after DST ends (2025: November 2, 2am PDT = 9am UTC)."""
    # 9:01 UTC on Nov 2 is PST
    dt_utc: datetime = datetime(2025, 11, 2, 9, 1, 0, tzinfo=timezone.utc)
    result: datetime = to_pacific(dt_utc)
    assert result.hour == 1  # 1:01am PST (falls back to 1am)


def test_midnight_utc_date_crossing() -> None:
    """Midnight UTC should be previous day in Pacific."""
    dt_utc: datetime = datetime(2025, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
    result: datetime = to_pacific(dt_utc)
    assert result.day == 14  # Still June 14 in Pacific
    assert result.hour == 17  # 5pm PDT


def test_late_utc_same_day() -> None:
    """Late UTC should still be same day in Pacific during summer."""
    dt_utc: datetime = datetime(2025, 6, 15, 23, 0, 0, tzinfo=timezone.utc)
    result: datetime = to_pacific(dt_utc)
    assert result.day == 15
    assert result.hour == 16  # 4pm PDT
