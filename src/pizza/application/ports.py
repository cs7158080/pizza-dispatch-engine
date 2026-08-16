"""Ports the core requires of the outside world, and the transaction boundary.

Protocols rather than base classes: an adapter satisfies one structurally, so this
module imports nothing from infrastructure/ while infrastructure/ imports it.

Each port error is declared above the port that raises it.
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

    def get_for_update(self, order_id: UUID) -> Order | None:
        """Lock the order and return it, holding the lock until the transaction ends.

        For write paths only: taking this lock on a read path would block writers
        needlessly.
        """
        ...

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

        Oldest-first is a convention, not a business rule: any available driver
        satisfies the requirement, and a fixed order makes the choice assertable.

        The driver is returned locked and not yet marked busy. The caller must mark
        and save it within the same transaction.
        """
        ...


class OutboxWriteFailed(Exception):
    """The outbox row could not be written or updated."""


class OutboxStore(Protocol):
    def add(self, event: OrderReadyEvent) -> None:
        """Record the event in the transaction that caused it."""
        ...

    def mark_published(self, event_id: UUID, now: datetime) -> None:
        """Record that the event reached the broker.

        Raises:
            OutboxWriteFailed: The outbox row could not be updated.
        """
        ...


class PublishFailed(Exception):
    """The event did not reach the broker."""


class EventPublisher(Protocol):
    def publish(self, event: OrderReadyEvent) -> None:
        """Send the event to the broker.

        Raises:
            PublishFailed: The event did not reach the broker.
        """
        ...


class TransactionFailed(Exception):
    """The transaction could not be committed."""


class UnitOfWork(Protocol):
    """One transaction, holding the repositories bound to it.

    Leaving the block without calling commit() rolls back. The context manager is
    re-enterable, so a caller may open a second transaction after the first commits.
    """

    orders: OrderRepository
    drivers: DriverRepository
    outbox: OutboxStore

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, *exc: object) -> None: ...

    def commit(self) -> None:
        """Commit the transaction.

        Raises:
            TransactionFailed: The transaction could not be committed.
        """
        ...
