"""Read paths: no rules, no writes, no commit.

They return entities; the response shape is assembled by the calling adapter.
"""

from dataclasses import dataclass
from uuid import UUID

from pizza.application.ports import UnitOfWork
from pizza.domain.driver import Driver
from pizza.domain.errors import OrderNotFound
from pizza.domain.order import Order


@dataclass(frozen=True)
class OrderDetail:
    order: Order
    driver: Driver | None


def get_order(uow: UnitOfWork, order_id: UUID) -> OrderDetail:
    """Fetch one order, with its driver when it has one.

    Raises:
        OrderNotFound: No order carries this identifier.
    """
    with uow:
        order = uow.orders.get(order_id)
        if order is None:
            raise OrderNotFound(order_id)
        driver = uow.drivers.get(order.driver_id) if order.driver_id else None
    return OrderDetail(order=order, driver=driver)


def list_orders(uow: UnitOfWork) -> list[Order]:
    """Fetch every order, newest first, without drivers.

    Drivers are omitted to keep this a single query rather than one per row.
    """
    with uow:
        return uow.orders.list_all()
