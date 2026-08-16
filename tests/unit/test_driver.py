"""Unit test for driver availability, exercised against the entity alone."""

from datetime import UTC, datetime
from uuid import uuid4

from pizza.domain.driver import Driver, DriverStatus

_NOW = datetime(2026, 8, 11, 12, 0, tzinfo=UTC)


def test_a_registered_driver_starts_available_and_returns_to_it() -> None:
    """Scenario: a driver starts available, becomes busy, and returns to available.

    Why it matters: without the return the pool is consumed once and never refilled,
    and every order past the driver count waits in the retry path forever. A `new()`
    that started BUSY, or these two methods swapped, produce the same failure while
    every component still reports success.
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
