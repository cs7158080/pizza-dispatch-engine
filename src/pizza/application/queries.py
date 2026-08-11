"""The read paths (R4, 6.5, 6.6): no rules, no writes, no commit.

Functions rather than classes: each has one dependency and no state, so a class would be
a constructor and nothing else. They use the same unit of work as the write paths (3.5)
and never commit — a second read-only port would exist only to avoid the word.

What they return is entities. The nested driver object, the field selection and the
`null` key are the API's shape, assembled by the adapter (6.5): the core never sees it.
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
    """Two keyed reads, and the second is skipped when there is no driver (6.5).

    Not a join: there is exactly one driver to fetch and it is a primary-key lookup, so a
    join would buy a round trip and cost a flattened row to unpack. The recorded cost is
    that two statements are not one snapshot — a driver released between them could be
    reported available on an order that still reads assigned. It is a display field on a
    read, and nothing decides anything on it.
    """
    with uow:
        order = uow.orders.get(order_id)
        if order is None:
            raise OrderNotFound(order_id)
        driver = uow.drivers.get(order.driver_id) if order.driver_id else None
    return OrderDetail(order=order, driver=driver)


def list_orders(uow: UnitOfWork) -> list[Order]:
    """Every order, newest first — one query, and deliberately no driver (6.6).

    Nesting a driver per row would turn a list of N into N+1 queries and invalidate 6.5's
    two-keyed-reads decision. The API projects the light field list from these entities.
    """
    with uow:
        return uow.orders.list_all()
