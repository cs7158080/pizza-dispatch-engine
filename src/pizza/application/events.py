"""The `ORDER_READY` event (7.2): identifiers only, built in this layer.

3.4 places the type here rather than in `domain/`, which never builds an event — the
transition returns a flag — and rather than in `infrastructure/`, which `application/`
may not import. U6 owns the wire format (7.3); this is the value both sides agree on.

It carries no snapshot of the order on purpose: 5.5 requires the consumer to read the
current row, and under 8.2's retry cycle the message may be minutes old, so any field
here beyond an identifier would be data nobody is permitted to trust.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID


@dataclass(frozen=True)
class OrderReadyEvent:
    # A field with one possible value is not data, it is a declaration that can be
    # written wrong. It reaches the wire and the outbox column from here (7.2).
    EVENT_TYPE: ClassVar[str] = "ORDER_READY"

    event_id: UUID  # uuid4, generated in this layer (4.7); the outbox row's key
    order_id: UUID
    occurred_at: datetime  # UTC-aware, the one Clock.now() of the invocation (4.8, 7.2)
