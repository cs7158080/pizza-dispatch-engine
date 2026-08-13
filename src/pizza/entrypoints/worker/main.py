"""The worker's composition root: the one module that builds the adapters.

The settings are loaded as the first statement of `main()`, so a bad environment
costs one line on standard error and a non-zero exit rather than a process that
subscribes and then fails every message. Importing this module reads nothing.

Nothing here retries. A broker that cannot be reached, a connection lost while
consuming, and a subscription the broker cancels all end the process, and the
restart policy is what brings it back — the worker holds no state, and a message
in flight was never acknowledged, so the broker redelivers it to the next one.
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
    try:
        settings = load_service_settings(os.environ)
    except ConfigurationError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error

    configure_logging(settings.log_level)

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_factory = sessionmaker(engine, autoflush=False, expire_on_commit=False)
    # One consumer on one thread, so the unit of work is entered again per
    # message rather than built again.
    consumer = DispatchConsumer(
        dispatch=DispatchOrder(SqlAlchemyUnitOfWork(session_factory), SystemClock()),
        decode=deserialize_or_none,
        queue=DISPATCH_QUEUE,
        max_retries=settings.dispatch_max_retries,
    )

    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.broker_url))
    except (AMQPError, OSError) as error:
        # Repr rather than str: pika's connection errors keep their cause in the
        # repr and leave str empty, which would print the field with nothing in it.
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

    # Consuming ends without an error only when the broker cancels the
    # subscription, which leaves the process with nothing to take.
    logger.error("event=broker_connection_lost")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
