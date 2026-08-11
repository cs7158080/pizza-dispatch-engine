"""The ORDER_READY event: the message the API publishes and the worker consumes.

It carries identifiers only. The consumer must read the current order row regardless,
because the state may have changed since the message was written.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID


@dataclass(frozen=True)
class OrderReadyEvent:
    EVENT_TYPE: ClassVar[str] = "ORDER_READY"

    event_id: UUID  # also the outbox row's key
    order_id: UUID
    occurred_at: datetime  # UTC-aware
