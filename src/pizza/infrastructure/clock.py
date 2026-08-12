"""The clock the use cases read, and the only place the current time enters."""

from datetime import UTC, datetime

from pizza.application.ports import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)
