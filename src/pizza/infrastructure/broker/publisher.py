"""Putting an event on the wire, over one connection opened at the first publish.

A lock covers the send, the confirmation and the reconnection: requests arrive on a
thread pool and this client is not thread-safe.

The retry is asymmetric. The broker closes an idle connection, since heartbeats go
unserviced between publishes — so a failure on a connection we already held is repaired
by one fresh one, while a connection that cannot be opened at all has nothing to
reconnect from and is reported instead.

Every failure leaves as `PublishFailed`: the use case that catches it may not import a
pika exception, so reducing them all to one named type is this module's duty here.
"""

import threading

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError

from pizza.application.events import OrderReadyEvent
from pizza.application.ports import EventPublisher, PublishFailed
from pizza.infrastructure.broker.serialization import serialize
from pizza.infrastructure.broker.topology import (
    ORDER_READY_KEY,
    ORDERS_EXCHANGE,
    declare,
)

_BROKER_FAULTS = (AMQPError, OSError)


class PikaEventPublisher(EventPublisher):
    """Publishes to RabbitMQ over one long-lived connection.

    Construction performs no I/O, so a service starts whether or not the broker is
    reachable. `close()` belongs to whoever built it.
    """

    def __init__(
        self,
        broker_url: str,
        publish_timeout_seconds: float,
        retry_delay_seconds: int,
    ) -> None:
        self._broker_url = broker_url
        self._publish_timeout_seconds = publish_timeout_seconds
        self._retry_delay_seconds = retry_delay_seconds
        self._lock = threading.Lock()
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def publish(self, event: OrderReadyEvent) -> None:
        """Raises PublishFailed."""
        body = serialize(event)

        with self._lock:
            channel = self._channel
            if channel is None:
                channel = self._open_or_fail()
                self._send_or_fail(channel, body)
                return

            try:
                self._send(channel, body)
            except _BROKER_FAULTS:
                channel = self._reconnect_or_fail()
                self._send_or_fail(channel, body)

    def close(self) -> None:
        """Close the connection if one was ever opened. Safe to call at any time."""
        with self._lock:
            self._discard_connection()

    def _open_or_fail(self) -> BlockingChannel:
        try:
            return self._open()
        except _BROKER_FAULTS as error:
            # An open that fails part way leaves a connection behind; without
            # this the next attempt would replace it and never close it.
            self._discard_connection()
            raise PublishFailed(f"could not reach the broker: {error}") from error

    def _reconnect_or_fail(self) -> BlockingChannel:
        self._discard_connection()
        return self._open_or_fail()

    def _send_or_fail(self, channel: BlockingChannel, body: bytes) -> None:
        try:
            self._send(channel, body)
        except _BROKER_FAULTS as error:
            raise PublishFailed(f"could not publish the event: {error}") from error

    def _open(self) -> BlockingChannel:
        self._connection = pika.BlockingConnection(self._parameters())
        channel = self._connection.channel()
        declare(channel, self._retry_delay_seconds)
        channel.confirm_delivery()
        self._channel = channel
        return channel

    def _parameters(self) -> pika.URLParameters:
        """Bound one attempt: the socket connect, the bring-up on top of it, and the
        broker announcing that it is stalled. A default left in place outlasts the
        timeout the caller was promised.
        """
        parameters = pika.URLParameters(self._broker_url)
        parameters.socket_timeout = self._publish_timeout_seconds
        parameters.stack_timeout = self._publish_timeout_seconds
        parameters.blocked_connection_timeout = self._publish_timeout_seconds
        return parameters

    def _send(self, channel: BlockingChannel, body: bytes) -> None:
        channel.basic_publish(
            exchange=ORDERS_EXCHANGE,
            routing_key=ORDER_READY_KEY,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
            mandatory=True,
        )

    def _discard_connection(self) -> None:
        connection, self._connection, self._channel = self._connection, None, None
        if connection is None:
            return
        try:
            connection.close()
        except _BROKER_FAULTS:
            # The connection is being thrown away; whether it closed cleanly
            # changes nothing for the caller.
            pass
