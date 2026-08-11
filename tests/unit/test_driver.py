"""The driver half of 5.6, provable against domain/ alone (5.7)."""

from datetime import UTC, datetime
from uuid import uuid4

from pizza.domain.driver import Driver, DriverStatus

_NOW = datetime(2026, 8, 11, 12, 0, tzinfo=UTC)


def test_a_registered_driver_starts_available_and_returns_to_it() -> None:
    """The pool must refill, which is the whole reason 5.6 exists.

    5.6 was added because without release the driver pool is consumed once and never
    refilled: after as many orders as there are drivers the system sits permanently in
    the no-driver retry path. A `new()` that started BUSY, or these two methods written
    the wrong way round, produce exactly that — a demo that stops working on the second
    order, with every part of the system reporting success.
    """
    driver = Driver.new(id=uuid4(), name="Noa", now=_NOW)

    observed: list[DriverStatus] = [driver.status]
    driver.mark_busy()
    observed.append(driver.status)
    driver.release()
    observed.append(driver.status)

    assert observed == [
        DriverStatus.AVAILABLE,
        DriverStatus.BUSY,
        DriverStatus.AVAILABLE,
    ]
