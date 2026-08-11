"""Create an order and store it."""

from uuid import UUID, uuid4

from pizza.application.ports import Clock, UnitOfWork
from pizza.domain.order import Order


class PlaceOrder:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, customer_name: str, address: str, items: list[str]) -> UUID:
        order = Order.new(
            id=uuid4(),
            customer_name=customer_name,
            address=address,
            items=items,
            now=self._clock.now(),
        )
        with self._uow as uow:
            uow.orders.add(order)
            uow.commit()
        return order.id
