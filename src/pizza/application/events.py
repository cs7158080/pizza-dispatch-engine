"""The ORDER_READY event, published by the API and consumed by the worker.

It carries identifiers only: consumers must read the current order row, since the
state may have changed since the message was written.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID


@dataclass(frozen=True)
class OrderReadyEvent:
    """Signals that an order is ready to be given a driver."""

    EVENT_TYPE: ClassVar[str] = "ORDER_READY"

    event_id: UUID  # also the outbox row's key
    order_id: UUID
    occurred_at: datetime  # UTC-aware
