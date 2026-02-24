"""Timezone conversion utilities for US Pacific time."""
# [Created with AI: Claude Code with Opus 4.6]

from datetime import datetime
from zoneinfo import ZoneInfo

PACIFIC: ZoneInfo = ZoneInfo("America/Los_Angeles")


def to_pacific(dt_utc: datetime) -> datetime:
    """Convert a UTC datetime to US Pacific (PST/PDT aware).

    Args:
        dt_utc: Datetime in UTC (must have tzinfo=timezone.utc).

    Returns:
        Datetime in Pacific time with proper PST/PDT offset.
    """
    return dt_utc.astimezone(PACIFIC)
