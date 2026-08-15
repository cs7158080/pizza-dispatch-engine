"""The exchanges, queues and bindings, declared by both services from one function.

Declaring is idempotent, so neither depends on which started first. The two exchanges
form the retry cycle: a rejected message waits in a queue that has no consumer until its
time to live expires, then returns to the main exchange — the delay between dispatch
attempts, with no timer of ours in it.
"""

from pika.adapters.blocking_connection import BlockingChannel

ORDERS_EXCHANGE = "pizza.orders"
DISPATCH_QUEUE = "pizza.orders.dispatch"
RETRY_EXCHANGE = "pizza.orders.retry"
WAIT_QUEUE = "pizza.orders.dispatch.wait"

ORDER_READY_KEY = "order.ready"
ORDER_READY_WAIT_KEY = "order.ready.wait"


def wait_queue_arguments(retry_delay_seconds: int) -> dict[str, object]:
    """The delay is configured in seconds and AMQP declares it in milliseconds."""
    return {
        "x-message-ttl": retry_delay_seconds * 1000,
        "x-dead-letter-exchange": ORDERS_EXCHANGE,
        "x-dead-letter-routing-key": ORDER_READY_KEY,
    }


def declare(channel: BlockingChannel, retry_delay_seconds: int) -> None:
    """Declare everything above, on every connection either service opens.

    Publishing to an exchange that does not exist closes the channel, so this runs
    before the first publish and not only after a reconnection.
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
