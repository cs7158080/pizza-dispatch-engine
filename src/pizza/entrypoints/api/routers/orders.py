"""The four order routes.

Each one validates, calls, and renders. No route catches a domain error and no
route decides anything: a refused transition leaves as an exception and the
installed handler answers it.
"""

from uuid import UUID

from fastapi import APIRouter

from pizza.application import queries
from pizza.entrypoints.api.deps import (
    AdvanceOrderStatusDep,
    PlaceOrderDep,
    UnitOfWorkDep,
)
from pizza.entrypoints.api.errors import CONFLICT, NOT_FOUND
from pizza.entrypoints.api.schemas import (
    Created,
    CreateOrderRequest,
    OrderResponse,
    OrderSummary,
    UpdateStatusRequest,
)

router = APIRouter()


@router.post("/orders", status_code=201)
def place_order(body: CreateOrderRequest, place: PlaceOrderDep) -> Created:
    """Place an order, and answer with its identifier."""
    return Created(id=place(body.customer_name, body.address, body.items))


@router.patch("/orders/{order_id}/status", responses={**NOT_FOUND, **CONFLICT})
def advance_order_status(
    order_id: UUID, body: UpdateStatusRequest, advance: AdvanceOrderStatusDep
) -> OrderResponse:
    """Move an order to the requested status, and answer with the whole order."""
    return OrderResponse.of(advance(order_id, body.status))


@router.get("/orders/{order_id}", responses=NOT_FOUND)
def get_order(order_id: UUID, uow: UnitOfWorkDep) -> OrderResponse:
    """Fetch one order, with its driver nested or null."""
    return OrderResponse.of(queries.get_order(uow, order_id))


@router.get("/orders")
def list_orders(uow: UnitOfWorkDep) -> list[OrderSummary]:
    """List every order, newest first, without drivers."""
    return [OrderSummary.of(order) for order in queries.list_orders(uow)]
