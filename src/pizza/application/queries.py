"""The read paths: no rules, no writes, no commit.

They return entities. The response shape -- the nested driver, the field selection -- is
the API's, assembled by the adapter.
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
    """Fetch one order, and its driver when it has one."""
    with uow:
        order = uow.orders.get(order_id)
        if order is None:
            raise OrderNotFound(order_id)
        driver = uow.drivers.get(order.driver_id) if order.driver_id else None
    return OrderDetail(order=order, driver=driver)


def list_orders(uow: UnitOfWork) -> list[Order]:
    """Every order, newest first, without drivers -- one query rather than N+1."""
    with uow:
        return uow.orders.list_all()
