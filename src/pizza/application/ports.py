"""What the core asks of the outside world, and the transaction boundary.

Protocols rather than base classes: an adapter satisfies one by shape, so this module
imports nothing from infrastructure/ while infrastructure/ imports it.

Each port error sits above the port that raises it.
"""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from pizza.application.events import OrderReadyEvent
from pizza.domain.driver import Driver
from pizza.domain.order import Order


class Clock(Protocol):
    def now(self) -> datetime:
        """Return the current time, timezone-aware and in UTC."""
        ...


class OrderRepository(Protocol):
    def add(self, order: Order) -> None: ...

    def get(self, order_id: UUID) -> Order | None: ...

    def save(self, order: Order) -> None: ...

    def list_all(self) -> list[Order]:
        """Return every order, newest first."""
        ...


class DriverRepository(Protocol):
    def add(self, driver: Driver) -> None: ...

    def get(self, driver_id: UUID) -> Driver | None: ...

    def save(self, driver: Driver) -> None: ...

    def claim_next_available_driver(self) -> Driver | None:
        """Lock and return the earliest-registered available driver, or None.

        The ordering is a convention rather than a business rule: any available driver
        satisfies the requirement, and oldest-first is chosen so that a test can assert
        which one was claimed. A preference expressing business intent would be a rule,
        and would move into domain/ with a criteria argument added here.

        The driver comes back locked and not yet marked busy. The caller marks and saves
        it inside the same transaction.
        """
        ...


class OutboxWriteFailed(Exception):
    """The outbox row could not be written or updated."""


class OutboxStore(Protocol):
    def add(self, event: OrderReadyEvent) -> None:
        """Record the event in the transaction that caused it."""
        ...

    def mark_published(self, event_id: UUID, now: datetime) -> None:
        """Raises OutboxWriteFailed."""
        ...


class PublishFailed(Exception):
    """The event did not reach the broker."""


class EventPublisher(Protocol):
    def publish(self, event: OrderReadyEvent) -> None:
        """Raises PublishFailed."""
        ...


class UnitOfWork(Protocol):
    """One transaction, holding the repositories bound to it.

    Leaving the block without commit() rolls back. It is re-enterable: the outbox row is
    marked published after the commit, in a second transaction.
    """

    orders: OrderRepository
    drivers: DriverRepository
    outbox: OutboxStore

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, *exc: object) -> None: ...

    def commit(self) -> None: ...
