"""FastAPI dependencies through which the routes receive their use cases.

`Wiring` names ports and callables only, never an implementation, which keeps the
composition root the only module importing infrastructure. It is built there and
read off the request, so nothing here is bound at import time.

A unit of work is built per request, since it holds the session it opened and
concurrent requests would otherwise share one transaction. The clock and the
publisher are shared; the publisher is thread-safe through its own lock.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request

from pizza.application.ports import Clock, EventPublisher, UnitOfWork
from pizza.application.use_cases.advance_order_status import AdvanceOrderStatus
from pizza.application.use_cases.place_order import PlaceOrder
from pizza.application.use_cases.register_driver import RegisterDriver


@dataclass(frozen=True)
class Wiring:
    """The ports and factories the composition root hands to the routes."""

    new_unit_of_work: Callable[[], UnitOfWork]
    clock: Clock
    publisher: EventPublisher
    database_reachable: Callable[[], bool]


def _wiring(request: Request) -> Wiring:
    # Assigned to a local first: application state is untyped.
    wiring: Wiring = request.app.state.wiring
    return wiring


WiringDep = Annotated[Wiring, Depends(_wiring)]


def _unit_of_work(wiring: WiringDep) -> UnitOfWork:
    return wiring.new_unit_of_work()


UnitOfWorkDep = Annotated[UnitOfWork, Depends(_unit_of_work)]


def _place_order(uow: UnitOfWorkDep, wiring: WiringDep) -> PlaceOrder:
    return PlaceOrder(uow, wiring.clock)


def _advance_order_status(uow: UnitOfWorkDep, wiring: WiringDep) -> AdvanceOrderStatus:
    return AdvanceOrderStatus(uow, wiring.clock, wiring.publisher)


def _register_driver(uow: UnitOfWorkDep, wiring: WiringDep) -> RegisterDriver:
    return RegisterDriver(uow, wiring.clock)


PlaceOrderDep = Annotated[PlaceOrder, Depends(_place_order)]
AdvanceOrderStatusDep = Annotated[AdvanceOrderStatus, Depends(_advance_order_status)]
RegisterDriverDep = Annotated[RegisterDriver, Depends(_register_driver)]
