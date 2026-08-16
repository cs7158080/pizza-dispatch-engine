"""Message callback: one message in, one dispatch attempt, one acknowledgement out.

Every path through the callback ends in an ack or a reject, so no message is ever
held.

A message is acked once its effect is durable, or once repeating it could not help:
an order that is already assigned, bytes that will never decode, an order that does
not exist. It is rejected when a later attempt might succeed, which sends it through
the wait queue and back.

The decoder is injected as a callable, since this module must not import the broker
serialization it comes from.
"""

import logging
from collections.abc import Callable, Mapping
from typing import Any

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from pizza.application.events import OrderReadyEvent
from pizza.application.use_cases.dispatch_order import DispatchOrder, DispatchOutcome
from pizza.domain.errors import OrderNotFound

logger = logging.getLogger(__name__)

# Enough to show a whole well-formed message and the head of anything larger.
_LOGGED_BODY_BYTES = 200


def rejection_count(headers: Mapping[str, Any] | None, queue: str) -> int:
    """Return how often the broker dead-lettered this message from `queue` as rejected.

    A first delivery carries no header at all and counts as zero. The wait queue keeps
    a separate entry counting expiries; the two advance together, so counting both
    would double the number the retry budget is measured against.
    """
    for entry in (headers or {}).get("x-death", []):
        if entry.get("queue") == queue and entry.get("reason") == "rejected":
            return int(entry["count"])
    return 0


class DispatchConsumer:
    """Consumes ORDER_READY messages and applies the acknowledgement policy.

    `max_retries` counts rejections rather than deliveries, so the first attempt does
    not consume the budget.
    """

    def __init__(
        self,
        dispatch: DispatchOrder,
        decode: Callable[[bytes], OrderReadyEvent | None],
        queue: str,
        max_retries: int,
    ) -> None:
        self._dispatch = dispatch
        self._decode = decode
        self._queue = queue
        self._max_retries = max_retries

    def on_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        """Handle one delivery. The signature is the one pika requires."""
        event = self._decode(body)
        if event is None:
            # The only failure with no order to name, so the body is logged instead.
            logger.error("event=poison_message body=%r", body[:_LOGGED_BODY_BYTES])
            channel.basic_ack(method.delivery_tag)
            return

        rejections = rejection_count(properties.headers, self._queue)
        try:
            acknowledge = self._attempt(event, rejections)
        except OrderNotFound:
            logger.error("event=order_not_found order_id=%s", event.order_id)
            acknowledge = True
        except Exception:
            # A fault in this service or in a dependency. Both require intervention,
            # after which the retried message succeeds, so it keeps circling.
            logger.exception("event=dispatch_error order_id=%s", event.order_id)
            acknowledge = False

        if acknowledge:
            channel.basic_ack(method.delivery_tag)
        else:
            channel.basic_reject(method.delivery_tag, requeue=False)

    def _attempt(self, event: OrderReadyEvent, rejections: int) -> bool:
        """Dispatch once and return whether the message can be acknowledged.

        False sends it back for another attempt after the wait.
        """
        result = self._dispatch(event.order_id)

        if result.outcome is DispatchOutcome.ASSIGNED:
            logger.info(
                "event=dispatch_notification order_id=%s"
                " driver_id=%s driver_name=%s at=%s",
                event.order_id,
                result.driver_id,
                result.driver_name,
                result.at,
            )
            return True

        if result.outcome is DispatchOutcome.NOTHING_TO_DO:
            logger.info("event=nothing_to_do order_id=%s", event.order_id)
            return True

        if rejections >= self._max_retries:
            self._dispatch.give_up(event.order_id)
            logger.error("event=dispatch_failed order_id=%s", event.order_id)
            return True

        logger.warning(
            "event=no_driver_available order_id=%s attempt=%s",
            event.order_id,
            rejections + 1,
        )
        return False
