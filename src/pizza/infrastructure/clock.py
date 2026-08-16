"""System clock: the only place the current time enters the system."""

from datetime import UTC, datetime

from pizza.application.ports import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        """Return the current time, timezone-aware and in UTC."""
        return datetime.now(UTC)
