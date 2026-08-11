"""Assign a driver to an order, at most once.

The caller maps the outcome to an acknowledgement; no broker vocabulary belongs here.
Two events are published per order, so a second arrival is expected rather than
exceptional -- the guard below is what makes it harmless.
"""

from enum import Enum
from uuid import UUID

from pizza.application.ports import Clock, UnitOfWork
from pizza.domain.errors import OrderNotFound


class DispatchOutcome(Enum):
    ASSIGNED = "ASSIGNED"
    NOTHING_TO_DO = "NOTHING_TO_DO"
    NO_DRIVER_AVAILABLE = "NO_DRIVER_AVAILABLE"


class DispatchOrder:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, order_id: UUID) -> DispatchOutcome:
        with self._uow as uow:
            order = uow.orders.get(order_id)
            if order is None:
                # The event is written in the same transaction as the order, so this is
                # a broken invariant rather than a race.
                raise OrderNotFound(order_id)

            if not order.can_be_assigned():
                return DispatchOutcome.NOTHING_TO_DO

            driver = uow.drivers.claim_next_available_driver()
            if driver is None:
                return DispatchOutcome.NO_DRIVER_AVAILABLE

            # The driver's status and the order's assignment are written together or
            # not at all, which one transaction is what enforces.
            driver.mark_busy()
            order.assign_to(driver.id, self._clock.now())
            uow.drivers.save(driver)
            uow.orders.save(order)
            uow.commit()

        return DispatchOutcome.ASSIGNED

    def give_up(self, order_id: UUID) -> None:
        """Record that no driver was found, once the retry budget is spent.

        The caller counts the attempts. The entity ignores this if the order has since
        been assigned or delivered.
        """
        with self._uow as uow:
            order = uow.orders.get(order_id)
            if order is None:
                raise OrderNotFound(order_id)
            order.mark_dispatch_failed()
            uow.orders.save(order)
            uow.commit()
