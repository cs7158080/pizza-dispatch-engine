"""The wire format: what survives a round trip, and what is refused.

The same bytes are published to the broker and stored in the outbox row, so a fault
here is a fault in both copies at once.
"""

import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from pizza.application.events import OrderReadyEvent
from pizza.infrastructure.broker.serialization import (
    SerializationError,
    deserialize,
    serialize,
)


def _an_event() -> OrderReadyEvent:
    return OrderReadyEvent(
        event_id=uuid4(),
        order_id=uuid4(),
        occurred_at=datetime(2026, 8, 12, 9, 30, 15, 123456, tzinfo=UTC),
    )


def test_an_event_survives_the_round_trip() -> None:
    """Identifiers and the instant come back as themselves, not as strings.

    The consumer reads the order by this identifier and nothing else identifies it. A
    UUID returning as text, or a timestamp losing its offset, would arrive as a
    well-formed message that fails further in, where the cause is no longer visible.
    """
    event = _an_event()

    restored = deserialize(serialize(event))

    assert restored == event
    assert isinstance(restored.event_id, UUID)
    assert restored.occurred_at.tzinfo is not None
    assert restored.occurred_at.utcoffset() == UTC.utcoffset(None)


def test_a_message_with_an_unknown_field_still_parses() -> None:
    """A field added by one side does not break the other.

    The tolerant reader is what stands in for a version marker: without it, adding a
    field becomes a coordinated deployment, and the design has no moment at which the
    two sides can be coordinated.
    """
    event = _an_event()
    document = json.loads(serialize(event).decode("utf-8"))
    document["dispatch_attempt"] = 2

    restored = deserialize(json.dumps(document).encode("utf-8"))

    assert restored == event


def test_malformed_input_raises_one_kind_of_error() -> None:
    """Every way of being wrong arrives as `SerializationError`.

    The consumer's poison-message path catches one family of error. A
    `UnicodeDecodeError` or a `KeyError` escaping this module would reach it as an
    unhandled exception and take the worker down instead of the message.
    """
    identifier = "6f1e1f7c-4c33-4f7a-9a1e-6d3d1f0d2a11"
    complete = {
        "event_id": identifier,
        "order_id": identifier,
        "occurred_at": "2026-01-01T00:00:00+00:00",
    }
    cases = {
        "invalid utf-8": b"\xff\xfe",
        "not json": b"{",
        "a missing field": json.dumps({"event_id": identifier}).encode(),
        "an unparseable identifier": json.dumps(
            {**complete, "order_id": "not a uuid"}
        ).encode(),
        "a naive timestamp": json.dumps(
            {**complete, "occurred_at": "2026-01-01T00:00:00"}
        ).encode(),
    }

    for description, raw in cases.items():
        try:
            deserialize(raw)
        except SerializationError:
            continue
        pytest.fail(f"{description} was accepted")
