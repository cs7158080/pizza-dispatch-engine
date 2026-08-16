"""Assigning a driver to an order, at most once.

Two events are published per order, so repeated dispatch attempts are routine and
are made idempotent by the guard in `__call__`.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from pizza.application.ports import Clock, UnitOfWork
from pizza.domain.errors import OrderNotFound


class DispatchOutcome(Enum):
    """Result of a dispatch attempt, which the caller turns into an acknowledgement."""

    ASSIGNED = "ASSIGNED"  # a driver was given the order
    NOTHING_TO_DO = "NOTHING_TO_DO"  # already assigned, or already delivered
    NO_DRIVER_AVAILABLE = "NO_DRIVER_AVAILABLE"  # none free; worth retrying


@dataclass(frozen=True)
class DispatchResult:
    """Outcome of a dispatch attempt, with the driver when one was assigned.

    The three assignment fields carry values on `ASSIGNED` and are None otherwise.
    """

    outcome: DispatchOutcome
    driver_id: UUID | None = None
    driver_name: str | None = None
    at: datetime | None = None


class DispatchOrder:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, order_id: UUID) -> DispatchResult:
        """Assign a driver to the order if it still needs one.

        Returns:
            The outcome of the attempt and, on assignment, the driver and the time.

        Raises:
            OrderNotFound: No order carries this identifier.
        """
        with self._uow as uow:
            order = uow.orders.get(order_id)
            if order is None:
                # The event is written in the same transaction as the order, so a
                # missing order is a broken invariant rather than a race.
                raise OrderNotFound(order_id)

            if not order.can_be_assigned():
                return DispatchResult(DispatchOutcome.NOTHING_TO_DO)

            driver = uow.drivers.claim_next_available_driver()
            if driver is None:
                return DispatchResult(DispatchOutcome.NO_DRIVER_AVAILABLE)

            # One transaction: the driver's status and the order's assignment are
            # written together or not at all.
            assigned_at = self._clock.now()
            driver.mark_busy()
            order.assign_to(driver.id, assigned_at)
            uow.drivers.save(driver)
            uow.orders.save(order)
            uow.commit()

        return DispatchResult(
            outcome=DispatchOutcome.ASSIGNED,
            driver_id=driver.id,
            driver_name=driver.name,
            at=assigned_at,
        )

    def give_up(self, order_id: UUID) -> None:
        """Record that no driver was found, once the retry budget is spent.

        The caller counts the attempts. The call is ignored if the order has since
        been assigned or delivered.

        Raises:
            OrderNotFound: No order carries this identifier.
        """
        with self._uow as uow:
            order = uow.orders.get(order_id)
            if order is None:
                raise OrderNotFound(order_id)
            order.mark_dispatch_failed()
            uow.orders.save(order)
            uow.commit()
