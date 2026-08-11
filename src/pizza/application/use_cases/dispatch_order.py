"""Assign a driver to an order, at most once (R7, R8).

The consumer calls this and maps the outcome to an AMQP verb; the three values below are
8.1's first three cases. The verb itself is not here — 3.2 keeps ack and reject in
`entrypoints/worker/consumer.py`, so this module contains no broker vocabulary at all.

The guard is 5.5's, evaluated in the core: R5 puts two events per order in flight, so a
second arrival, a redelivery and a repeated status update all collapse into one rule.
"""

from enum import Enum
from uuid import UUID

from pizza.application.ports import Clock, UnitOfWork
from pizza.domain.errors import OrderNotFound


class DispatchOutcome(Enum):
    """8.1's cases 1 to 3. Case 4, an exhausted budget, is `give_up` below."""

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
                # The outbox row and the status change are written in one transaction
                # (7.5), so this is a broken invariant rather than a race. Reporting it
                # as "nothing to do" would erase the only evidence it happened.
                raise OrderNotFound(order_id)

            if not order.can_be_assigned():
                return DispatchOutcome.NOTHING_TO_DO

            driver = uow.drivers.claim_next_available_driver()
            if driver is None:
                return DispatchOutcome.NO_DRIVER_AVAILABLE

            # 4.3's invariant: the driver's status and the order's assignment are
            # written together or not at all. One transaction is what enforces it.
            driver.mark_busy()
            order.assign_to(driver.id, self._clock.now())
            uow.drivers.save(driver)
            uow.orders.save(order)
            uow.commit()

        return DispatchOutcome.ASSIGNED

    def give_up(self, order_id: UUID) -> None:
        """Record 8.3's terminal state once the retry budget is spent.

        Exhaustion is counted by the broker, in the `x-death` header (7.4), so the
        consumer decides when this is called and the core never learns the number. The
        entity's own guard makes it a no-op on an order that has since been assigned or
        delivered, which R5's second event makes an ordinary path rather than an edge.
        """
        with self._uow as uow:
            order = uow.orders.get(order_id)
            if order is None:
                raise OrderNotFound(order_id)
            order.mark_dispatch_failed()
            uow.orders.save(order)
            uow.commit()
