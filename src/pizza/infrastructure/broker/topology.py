"""Broker topology: the exchanges, queues and bindings, declared by both services.

Declaration is idempotent, so neither service depends on which started first.

The two exchanges form the retry cycle: a rejected message waits in a queue with no
consumer until its time to live expires, then dead-letters back to the main exchange.
The delay between dispatch attempts is therefore the broker's, not a timer of ours.
"""

from pika.adapters.blocking_connection import BlockingChannel

ORDERS_EXCHANGE = "pizza.orders"
DISPATCH_QUEUE = "pizza.orders.dispatch"
RETRY_EXCHANGE = "pizza.orders.retry"
WAIT_QUEUE = "pizza.orders.dispatch.wait"

ORDER_READY_KEY = "order.ready"
ORDER_READY_WAIT_KEY = "order.ready.wait"


def wait_queue_arguments(retry_delay_seconds: int) -> dict[str, object]:
    """Build the wait queue's arguments, converting the delay to milliseconds."""
    return {
        "x-message-ttl": retry_delay_seconds * 1000,
        "x-dead-letter-exchange": ORDERS_EXCHANGE,
        "x-dead-letter-routing-key": ORDER_READY_KEY,
    }


def declare(channel: BlockingChannel, retry_delay_seconds: int) -> None:
    """Declare the exchanges, queues and bindings on the given channel.

    Publishing to an exchange that does not exist closes the channel, so this must
    run on every connection, before the first publish.
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
