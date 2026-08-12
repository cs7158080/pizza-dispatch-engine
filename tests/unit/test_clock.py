"""The one place the current time enters the system."""

from datetime import UTC, timedelta

from pizza.infrastructure.clock import SystemClock


def test_the_clock_reads_utc_with_an_offset() -> None:
    """`now()` is timezone-aware and its offset is zero.

    Every timestamp in the system is one read of this clock, and a naive
    `datetime.now()` is the one-character version of this method that satisfies the
    type checker: the value reaches a `timestamptz` column and the API looking the
    same, and only its comparisons and its rendering are wrong.
    """
    now = SystemClock().now()

    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)
    assert now.tzinfo.utcoffset(now) == UTC.utcoffset(None)
