"""The seam the routes receive their use cases through.

`Wiring` names ports and callables only, never an implementation, which is what
lets the composition root be the one module that imports infrastructure. It is
built there and read from the request, so nothing here is bound at import time.

A unit of work is built per request: it holds the session it opened, and two
requests genuinely run in parallel, so a shared one would have two threads
overwriting one transaction. The clock and the publisher are shared, the
publisher being thread-safe by its own lock.
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
    """What the composition root hands the routes."""

    new_unit_of_work: Callable[[], UnitOfWork]
    clock: Clock
    publisher: EventPublisher
    database_reachable: Callable[[], bool]


def _wiring(request: Request) -> Wiring:
    # Through a local, because application state is untyped.
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
