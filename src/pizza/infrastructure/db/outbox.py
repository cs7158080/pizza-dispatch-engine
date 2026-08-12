"""The record of every event, written in the transaction that caused it.

The row is the evidence that an event was meant to go out. It is written with the
same function that produces the published message, so the two cannot describe
different things, and it is not committed here: the commit belongs to the use case,
which is what makes the row and the status change atomic.
"""

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pizza.application.events import OrderReadyEvent
from pizza.application.ports import OutboxStore, OutboxWriteFailed
from pizza.infrastructure.broker.serialization import serialize
from pizza.infrastructure.db.models import OutboxModel


class SqlAlchemyOutboxStore(OutboxStore):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, event: OrderReadyEvent) -> None:
        self._session.add(
            OutboxModel(
                event_id=event.event_id,
                event_type=OrderReadyEvent.EVENT_TYPE,
                payload=json.loads(serialize(event).decode("utf-8")),
                created_at=event.occurred_at,
                published_at=None,
            )
        )

    def mark_published(self, event_id: UUID, now: datetime) -> None:
        """Raises OutboxWriteFailed."""
        try:
            row = self._session.get(OutboxModel, event_id)
            if row is None:
                # The row was written in a transaction that has committed, so its
                # absence is a broken invariant rather than a race.
                raise OutboxWriteFailed(f"no outbox row for event {event_id}")
            row.published_at = now
        except SQLAlchemyError as error:
            raise OutboxWriteFailed(f"could not mark event {event_id}") from error
