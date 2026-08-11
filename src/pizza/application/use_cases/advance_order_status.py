"""Move an order one step, and act on the two facts the transition reports (R2, R5).

This is where 7.5's ordering lives: the transaction commits first, and only then is the
event published. The accepted failure is a lost event, recorded as an outbox row that
was never marked published — never a database transaction held open across a network
call to a second system.
"""

import logging
from uuid import UUID, uuid4

from pizza.application.events import OrderReadyEvent
from pizza.application.ports import (
    Clock,
    EventPublisher,
    OutboxWriteFailed,
    PublishFailed,
    UnitOfWork,
)
from pizza.domain.errors import OrderNotFound
from pizza.domain.order import Order, OrderStatus

logger = logging.getLogger(__name__)


class AdvanceOrderStatus:
    def __init__(
        self, uow: UnitOfWork, clock: Clock, publisher: EventPublisher
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._publisher = publisher

    def __call__(self, order_id: UUID, to: OrderStatus) -> Order:
        now = self._clock.now()
        event: OrderReadyEvent | None = None

        with self._uow as uow:
            order = uow.orders.get(order_id)
            if order is None:
                raise OrderNotFound(order_id)

            result = order.advance_to(to)  # raises IllegalTransition (5.2)
            uow.orders.save(order)

            if result.releases_driver and order.driver_id is not None:
                driver = uow.drivers.get(order.driver_id)
                if driver is not None:
                    driver.release()
                    uow.drivers.save(driver)

            if result.must_publish:
                event = OrderReadyEvent(
                    event_id=uuid4(), order_id=order.id, occurred_at=now
                )
                uow.outbox.add(event)

            uow.commit()

        # Everything below happens after the commit. 7.5's whole decision is this line
        # ordering, and nothing between the commit and here touches the transaction.
        if event is not None:
            self._publish_and_mark(event)

        return order

    def _publish_and_mark(self, event: OrderReadyEvent) -> None:
        try:
            self._publisher.publish(event)
        except PublishFailed:
            # 7.6: the status change already happened, so the request succeeds. The
            # unpublished row is what names which order lost its dispatch.
            logger.error(
                "publish failed for order %s, event %s", event.order_id, event.event_id
            )
            return

        try:
            with self._uow as uow:
                uow.outbox.mark_published(event.event_id, self._clock.now())
                uow.commit()
        except OutboxWriteFailed:
            # Logged, not raised: nothing acts on unpublished rows (3.4). The event did
            # reach the broker, so the only cost is a row that understates what happened.
            logger.error("could not mark event %s published", event.event_id)
