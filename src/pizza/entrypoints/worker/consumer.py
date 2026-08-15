"""One message in, one dispatch attempt, one acknowledgement out.

Every path through the callback ends in an ack or a reject, so a message can never
be held: the queue hands out one at a time and nothing here can keep it.

Which of the two a message gets is the whole policy. A message is acked once its
effect is durable or once repeating it could not help — an order that is already
assigned, bytes that will never decode, an order that is not there. It is rejected
when the attempt might succeed later, which sends it into the wait queue and back.

The decoder arrives as a callable rather than an import, because this module may not
name the one it comes from.
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
    """How often the broker has dead-lettered this message from `queue` as rejected.

    Zero for a first delivery, which carries no header at all. The wait queue keeps
    an entry of its own counting expiries, and the two advance together — reading
    both would double the number the retry budget is measured against.
    """
    for entry in (headers or {}).get("x-death", []):
        if entry.get("queue") == queue and entry.get("reason") == "rejected":
            return int(entry["count"])
    return 0


class DispatchConsumer:
    """The message callback, holding what a use case cannot decide.

    `max_retries` counts rejections rather than deliveries, so the first attempt is
    not one of them.
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
        """Handle one delivery. The signature is the one pika calls."""
        event = self._decode(body)
        if event is None:
            # Answered before anything else: this is the one failure with no
            # order to name, so the body is the whole record of it.
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
            # A fault of ours or of something we depend on. Both are repaired by
            # someone acting, after which the message passes, so it keeps circling.
            logger.exception("event=dispatch_error order_id=%s", event.order_id)
            acknowledge = False

        if acknowledge:
            channel.basic_ack(method.delivery_tag)
        else:
            channel.basic_reject(method.delivery_tag, requeue=False)

    def _attempt(self, event: OrderReadyEvent, rejections: int) -> bool:
        """Dispatch once, and report whether the message is finished with.

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
