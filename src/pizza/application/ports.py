"""What the core asks of the outside world (3.4), and the transaction boundary (3.5).

`Protocol`s, not base classes: an adapter satisfies one by shape, so `infrastructure/`
imports this module and nothing here imports `infrastructure/`. That inversion is the
whole of "dependencies point inward" (3.1) — the runtime call goes outward, the import
does not.

Each port error sits immediately above the port that raises it. `domain/errors.py` holds
business outcomes, which cross every layer to the client; these travel one layer inward
and stop.
"""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from pizza.application.events import OrderReadyEvent
from pizza.domain.driver import Driver
from pizza.domain.order import Order


class Clock(Protocol):
    def now(self) -> datetime:
        """Timezone-aware UTC (4.8). A port, so a test can control it."""
        ...


class OrderRepository(Protocol):
    def add(self, order: Order) -> None: ...

    def get(self, order_id: UUID) -> Order | None: ...

    def save(self, order: Order) -> None: ...

    def list_all(self) -> list[Order]:
        """Every order, newest first (6.6). No cap, no paging, no filter."""
        ...


class DriverRepository(Protocol):
    def add(self, driver: Driver) -> None: ...

    def get(self, driver_id: UUID) -> Driver | None: ...

    def save(self, driver: Driver) -> None: ...

    def claim_next_available_driver(self) -> Driver | None:
        """Lock and return the earliest-registered available driver, or None.

        The ordering is a **convention, not a business rule** (3.2). R7 asks for *an*
        available driver and names no preference, so 5.4 chose oldest-first purely as a
        deterministic tie-breaker — there is nothing here that could be violated. It
        lives in the adapter because selecting in Python and then locking is a
        read-then-lock race, so the selection and the lock must be one statement (8.9).

        If a preference ever expresses business intent — proximity, load — it becomes a
        rule, moves into `domain/`, and this signature grows a criteria argument. Not
        before: a criteria type with no fields is a speculative abstraction.

        The returned driver is **locked and not yet marked**. The use case marks and
        saves it inside the same transaction (8.9, 4.3).
        """
        ...


class OutboxWriteFailed(Exception):
    """The outbox row could not be written or updated (3.4)."""


class OutboxStore(Protocol):
    def add(self, event: OrderReadyEvent) -> None:
        """Record the event in the transaction that caused it (7.5)."""
        ...

    def mark_published(self, event_id: UUID, now: datetime) -> None:
        """Raises OutboxWriteFailed. Runs after the commit, so in a second transaction."""
        ...


class PublishFailed(Exception):
    """The event did not reach the broker (3.4). Not a violated rule — 7.6 returns 200."""


class EventPublisher(Protocol):
    def publish(self, event: OrderReadyEvent) -> None:
        """Raises PublishFailed. Confirms make failure detectable (7.5)."""
        ...


class UnitOfWork(Protocol):
    """One transaction, holding the repositories bound to it (3.5).

    The repositories are reached through the unit of work rather than injected beside it,
    so atomicity is the type's job instead of the composition root's. Leaving the block
    without `commit()` rolls back. It must be **re-enterable**: 7.5 marks the outbox row
    after the commit, in a second transaction, and each entry opens a fresh session.
    """

    orders: OrderRepository
    drivers: DriverRepository
    outbox: OutboxStore

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, *exc: object) -> None: ...

    def commit(self) -> None: ...
