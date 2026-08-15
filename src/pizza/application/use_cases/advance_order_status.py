"""Moving an order forward, and acting on what the transition reports.

The event is published only after the transaction commits, so no database lock
is held across a call to the broker. The accepted cost is a lost event, which
the outbox row records by staying unpublished.
"""

import logging
from uuid import UUID, uuid4

from pizza.application.events import OrderReadyEvent
from pizza.application.ports import (
    Clock,
    EventPublisher,
    OutboxWriteFailed,
    PublishFailed,
    TransactionFailed,
    UnitOfWork,
)
from pizza.application.queries import OrderDetail
from pizza.domain.errors import OrderNotFound
from pizza.domain.order import OrderStatus

logger = logging.getLogger(__name__)


class AdvanceOrderStatus:
    def __init__(
        self, uow: UnitOfWork, clock: Clock, publisher: EventPublisher
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._publisher = publisher

    def __call__(self, order_id: UUID, requested_status: OrderStatus) -> OrderDetail:
        """Move the order to the requested status and return it with its driver.

        The driver is the one the order holds after the transition, so a release
        is visible in what comes back.

        Raises `OrderNotFound`, or `IllegalTransition` when the requested status
        is not the adjacent one.
        """
        now = self._clock.now()
        event: OrderReadyEvent | None = None

        with self._uow as uow:
            order = uow.orders.get_for_update(order_id)
            if order is None:
                raise OrderNotFound(order_id)

            result = order.advance_to(requested_status)
            uow.orders.save(order)

            driver = uow.drivers.get(order.driver_id) if order.driver_id else None
            if result.releases_driver and driver is not None:
                driver.release()
                uow.drivers.save(driver)

            if result.must_publish:
                event = OrderReadyEvent(
                    event_id=uuid4(), order_id=order.id, occurred_at=now
                )
                uow.outbox.add(event)

            uow.commit()

        # Past the commit. Nothing below may touch the transaction.
        if event is not None:
            self._publish_and_mark(event)

        return OrderDetail(order=order, driver=driver)

    def _publish_and_mark(self, event: OrderReadyEvent) -> None:
        try:
            self._publisher.publish(event)
        except PublishFailed:
            # The status change is already durable, so the caller still succeeds.
            # The unpublished row names which order lost its dispatch.
            logger.error(
                "publish failed for order %s, event %s", event.order_id, event.event_id
            )
            return

        try:
            with self._uow as uow:
                uow.outbox.mark_published(event.event_id, self._clock.now())
                uow.commit()
        except (OutboxWriteFailed, TransactionFailed):
            # The UPDATE leaves with the transaction, so the commit is where a
            # database fault lands. Nothing reads unpublished rows, so this costs a
            # row that understates what happened rather than any behaviour.
            logger.error("could not mark event %s published", event.event_id)
