"""Rows in, entities out — the two repositories the core asks for.

Every conversion between a table row and a domain entity happens here, so nothing
ORM-shaped leaves this module and the core never learns that SQLAlchemy exists.

Each repository is bound to one `Session` and cannot outlive it; the unit of work
builds them.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from pizza.application.ports import DriverRepository, OrderRepository
from pizza.domain.driver import Driver, DriverStatus
from pizza.domain.order import AssignmentState, Order, OrderStatus
from pizza.infrastructure.db.models import DriverModel, OrderModel


def _to_order(row: OrderModel) -> Order:
    return Order(
        id=row.id,
        customer_name=row.customer_name,
        address=row.address,
        items=list(row.items),
        status=OrderStatus(row.status),
        assignment_state=AssignmentState(row.assignment_state),
        driver_id=row.driver_id,
        assigned_at=row.assigned_at,
        created_at=row.created_at,
    )


def _to_driver(row: DriverModel) -> Driver:
    return Driver(
        id=row.id,
        name=row.name,
        status=DriverStatus(row.status),
        created_at=row.created_at,
    )


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, order: Order) -> None:
        self._session.add(
            OrderModel(
                id=order.id,
                customer_name=order.customer_name,
                address=order.address,
                items=order.items,
                status=order.status.value,
                assignment_state=order.assignment_state.value,
                driver_id=order.driver_id,
                assigned_at=order.assigned_at,
                created_at=order.created_at,
            )
        )

    def get(self, order_id: UUID) -> Order | None:
        row = self._session.get(OrderModel, order_id)
        return None if row is None else _to_order(row)

    def get_for_update(self, order_id: UUID) -> Order | None:
        """Lock the order and return it, holding the lock for the whole transaction.

        The primary-key path get() takes, with the lock added, so the two cannot
        drift in how they load a row. The lock argument also bypasses the identity
        map, so the SELECT is issued even for a row this Session already holds.
        """
        row = self._session.get(OrderModel, order_id, with_for_update=True)
        return None if row is None else _to_order(row)

    def save(self, order: Order) -> None:
        # Loaded earlier in this Session by get(), so this resolves from the
        # identity map; it would issue a SELECT otherwise. A row that is not there
        # is a broken invariant, and get_one raises rather than writing nothing.
        row = self._session.get_one(OrderModel, order.id)
        row.status = order.status.value
        row.assignment_state = order.assignment_state.value
        row.driver_id = order.driver_id
        row.assigned_at = order.assigned_at

    def list_all(self) -> list[Order]:
        # The identifier breaks ties, so two orders created inside one clock tick
        # still come back in a fixed order.
        query = select(OrderModel).order_by(OrderModel.created_at.desc(), OrderModel.id)
        return [_to_order(row) for row in self._session.scalars(query)]


class SqlAlchemyDriverRepository(DriverRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, driver: Driver) -> None:
        self._session.add(
            DriverModel(
                id=driver.id,
                name=driver.name,
                status=driver.status.value,
                created_at=driver.created_at,
            )
        )

    def get(self, driver_id: UUID) -> Driver | None:
        row = self._session.get(DriverModel, driver_id)
        return None if row is None else _to_driver(row)

    def save(self, driver: Driver) -> None:
        row = self._session.get_one(DriverModel, driver.id)
        row.status = driver.status.value

    def claim_next_available_driver(self) -> Driver | None:
        """Lock and return the earliest-registered available driver, or None.

        The row is locked for the rest of the transaction and is returned unmarked:
        the caller marks it busy and saves it in that same transaction.
        """
        query = (
            select(DriverModel)
            .where(DriverModel.status == DriverStatus.AVAILABLE.value)
            .order_by(DriverModel.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        row = self._session.scalars(query).first()
        return None if row is None else _to_driver(row)
