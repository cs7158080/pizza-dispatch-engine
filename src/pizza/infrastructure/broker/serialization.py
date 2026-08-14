"""The wire format of an event: JSON, encoded UTF-8.

One pair of functions produces both copies of a message — the one published to the
broker and the one stored in the outbox row — so the record of what was meant to go
out cannot drift from what went out.

The reader is tolerant: fields it does not know are ignored, so a field may be added
without coordinating both sides. Anything it cannot turn into a valid event raises
`SerializationError`, and nothing else escapes it — decoding happens inside this
boundary so that a caller has one family of error to catch.
"""

import json
from datetime import datetime
from uuid import UUID

from pizza.application.events import OrderReadyEvent


class SerializationError(Exception):
    """The bytes do not describe a valid event."""


def serialize(event: OrderReadyEvent) -> bytes:
    document = {
        "event_type": OrderReadyEvent.EVENT_TYPE,
        "event_id": str(event.event_id),
        "order_id": str(event.order_id),
        "occurred_at": event.occurred_at.isoformat(),
    }
    return json.dumps(document).encode("utf-8")


def deserialize(raw: bytes) -> OrderReadyEvent:
    """Build an event from a published message. Raises `SerializationError`."""
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

    For a caller that may not name `SerializationError`. The absent event is a
    value the signature forces every caller to handle, so nothing else that goes
    wrong inside is turned into one.
    """
    try:
        return deserialize(raw)
    except SerializationError:
        return None
