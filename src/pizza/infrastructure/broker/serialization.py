"""Wire format of an event: JSON encoded as UTF-8.

These functions produce both copies of a message — the one published to the broker
and the one stored in the outbox row — so the two cannot diverge.

Reading is tolerant: unknown fields are ignored, so a field can be added without
coordinating both sides. Anything that cannot be turned into a valid event raises
`SerializationError`, and no other exception escapes this module.
"""

import json
from datetime import datetime
from uuid import UUID

from pizza.application.events import OrderReadyEvent


class SerializationError(Exception):
    """The bytes do not describe a valid event."""


def serialize(event: OrderReadyEvent) -> bytes:
    """Render the event as the JSON message published to the broker."""
    document = {
        "event_type": OrderReadyEvent.EVENT_TYPE,
        "event_id": str(event.event_id),
        "order_id": str(event.order_id),
        "occurred_at": event.occurred_at.isoformat(),
    }
    return json.dumps(document).encode("utf-8")


def deserialize(raw: bytes) -> OrderReadyEvent:
    """Build an event from a published message.

    Raises:
        SerializationError: The bytes do not describe a valid event.
    """
    try:
        document = json.loads(raw.decode("utf-8"))
        occurred_at = datetime.fromisoformat(document["occurred_at"])
        if occurred_at.tzinfo is None:
            raise ValueError("occurred_at carries no offset")
        return OrderReadyEvent(
            event_id=UUID(document["event_id"]),
            order_id=UUID(document["order_id"]),
            occurred_at=occurred_at,
        )
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        raise SerializationError(f"not a valid ORDER_READY message: {error}") from error


def deserialize_or_none(raw: bytes) -> OrderReadyEvent | None:
    """Build an event, or return None when the bytes do not describe one.

    For callers that handle a malformed message as a value rather than an exception.
    Only `SerializationError` is converted to None.
    """
    try:
        return deserialize(raw)
    except SerializationError:
        return None
