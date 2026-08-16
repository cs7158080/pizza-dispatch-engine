"""Composition root of the worker service: the only module that builds the adapters.

Settings are loaded as the first statement of `main()`, so an invalid environment
exits non-zero instead of subscribing and then failing every message. Importing this
module reads nothing.

Nothing here retries. An unreachable broker, a connection lost while consuming, and
a cancelled subscription all end the process; the restart policy brings it back. The
worker holds no state, and an in-flight message was never acknowledged, so the broker
redelivers it.
"""

import logging
import os
import sys

import pika
from pika.exceptions import AMQPError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pizza.application.use_cases.dispatch_order import DispatchOrder
from pizza.config import ConfigurationError, load_service_settings
from pizza.entrypoints.worker.consumer import DispatchConsumer
from pizza.infrastructure.broker.serialization import deserialize_or_none
from pizza.infrastructure.broker.topology import DISPATCH_QUEUE, declare
from pizza.infrastructure.clock import SystemClock
from pizza.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from pizza.log import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Subscribe to the dispatch queue and consume until the connection ends."""
    try:
        settings = load_service_settings(os.environ)
    except ConfigurationError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error

    configure_logging(settings.log_level)

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_factory = sessionmaker(engine, autoflush=False, expire_on_commit=False)
    # One consumer on one thread, so a single unit of work is re-entered per message
    # rather than rebuilt.
    consumer = DispatchConsumer(
        dispatch=DispatchOrder(SqlAlchemyUnitOfWork(session_factory), SystemClock()),
        decode=deserialize_or_none,
        queue=DISPATCH_QUEUE,
        max_retries=settings.dispatch_max_retries,
    )

    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.broker_url))
    except (AMQPError, OSError) as error:
        # Repr rather than str: pika's connection errors carry their cause in the
        # repr and leave str empty, which would log an empty field.
        logger.error("event=broker_unreachable error=%r", error)
        raise SystemExit(1) from error

    try:
        channel = connection.channel()
        declare(channel, settings.dispatch_retry_delay_seconds)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(DISPATCH_QUEUE, consumer.on_message)
        logger.info("event=worker_ready")
        channel.start_consuming()
    except (AMQPError, OSError) as error:
        logger.error("event=broker_connection_lost error=%r", error)
        raise SystemExit(1) from error

    # Consuming ends without an error only when the broker cancels the subscription,
    # which leaves the process with nothing to consume.
    logger.error("event=broker_connection_lost")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
