"""The exchanges, queues and bindings the system publishes and consumes through.

Both services declare all of it, from this one function. Declaring is idempotent, so
whichever starts first creates the topology and the other finds it already there;
neither depends on the order.

The two exchanges form a cycle that supplies the delay between dispatch attempts. A
message the worker rejects leaves the dispatch queue for the retry exchange, waits in a
queue that has no consumer until its time to live expires, and returns to the main
exchange. Nothing in this system runs a timer for it.

Changing an argument of a queue that already exists is refused by the broker and closes
the channel. Recreating the broker is the repair.
"""

from pika.adapters.blocking_connection import BlockingChannel

ORDERS_EXCHANGE = "pizza.orders"
DISPATCH_QUEUE = "pizza.orders.dispatch"
RETRY_EXCHANGE = "pizza.orders.retry"
WAIT_QUEUE = "pizza.orders.dispatch.wait"

ORDER_READY_KEY = "order.ready"
ORDER_READY_WAIT_KEY = "order.ready.wait"


def wait_queue_arguments(retry_delay_seconds: int) -> dict[str, object]:
    """Build the wait queue's arguments from the configured retry delay.

    The delay is configured in seconds and AMQP expresses a queue's time to live in
    milliseconds, so the conversion happens here and nowhere else.
    """
    return {
        "x-message-ttl": retry_delay_seconds * 1000,
        "x-dead-letter-exchange": ORDERS_EXCHANGE,
        "x-dead-letter-routing-key": ORDER_READY_KEY,
    }


def declare(channel: BlockingChannel, retry_delay_seconds: int) -> None:
    """Declare every object above on the given channel.

    Called by both services on every connection they open, including the first.
    Publishing to an exchange that does not exist closes the channel, so this runs
    before the first publish rather than only after a reconnection.
    """
    channel.exchange_declare(ORDERS_EXCHANGE, exchange_type="direct", durable=True)
    channel.exchange_declare(RETRY_EXCHANGE, exchange_type="direct", durable=True)

    channel.queue_declare(
        DISPATCH_QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": RETRY_EXCHANGE,
            "x-dead-letter-routing-key": ORDER_READY_WAIT_KEY,
        },
    )
    channel.queue_bind(DISPATCH_QUEUE, ORDERS_EXCHANGE, ORDER_READY_KEY)

    channel.queue_declare(
        WAIT_QUEUE,
        durable=True,
        arguments=wait_queue_arguments(retry_delay_seconds),
    )
    channel.queue_bind(WAIT_QUEUE, RETRY_EXCHANGE, ORDER_READY_WAIT_KEY)
