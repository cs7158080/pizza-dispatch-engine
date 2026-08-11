"""Create an order and store it (R1).

The identifier is generated here rather than by the database (4.7), which is why it is
known before the transaction opens and needs no read back. `items` arrived bounded and
trimmed from the edge (4.2); nothing in this layer inspects it.
"""

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
