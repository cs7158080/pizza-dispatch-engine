"""Unit test for the system clock, the one place the current time enters."""

from datetime import UTC, timedelta

from pizza.infrastructure.clock import SystemClock


def test_the_clock_reads_utc_with_an_offset() -> None:
    """Scenario: `now()` returns a timezone-aware value whose offset is zero.

    Why it matters: every timestamp in the system is one read of this clock. A naive
    `datetime.now()` type-checks and reaches both the `timestamptz` column and the
    API looking identical; only its comparisons and its rendering are wrong.
    """
    now = SystemClock().now()

    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)
    assert now.tzinfo.utcoffset(now) == UTC.utcoffset(None)
