"""Register a driver (R3).

Same shape as placing an order, and deliberately so: identity and time enter the entity
as arguments, the entity decides its own initial state, and this layer only stores it.
"""

from uuid import UUID, uuid4

from pizza.application.ports import Clock, UnitOfWork
from pizza.domain.driver import Driver


class RegisterDriver:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, name: str) -> UUID:
        driver = Driver.new(id=uuid4(), name=name, now=self._clock.now())
        with self._uow as uow:
            uow.drivers.add(driver)
            uow.commit()
        return driver.id
