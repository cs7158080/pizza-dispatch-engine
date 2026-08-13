"""What a request may carry, and what a response answers with.

The request models are the edge validation: unknown fields are forbidden and every
bound is declared, so nothing hand-written stands between the wire and the core. The
response models assemble the shapes the API promises — the nested driver among them —
from the types the application layer returns, which is why the core never sees one.
"""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from pizza.application.queries import OrderDetail
from pizza.domain.driver import DriverStatus
from pizza.domain.order import AssignmentState, Order, OrderStatus

# Trimmed before the length is checked, so a value of spaces is rejected rather
# than stored, and what is stored is what was measured.
_Text100 = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
_Text200 = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]


class _Request(BaseModel):
    """Every request model: unknown fields are rejected rather than ignored."""

    model_config = ConfigDict(extra="forbid")


class CreateOrderRequest(_Request):
    customer_name: _Text100
    address: _Text200
    items: list[_Text100] = Field(min_length=1, max_length=20)


class UpdateStatusRequest(_Request):
    # The domain enum, so an unrecognised status never reaches the core.
    status: OrderStatus


class RegisterDriverRequest(_Request):
    name: _Text100


class Created(BaseModel):
    """The body of both creations: the one fact the client could not predict."""

    id: UUID


class DriverResponse(BaseModel):
    id: UUID
    name: str
    status: DriverStatus


class OrderResponse(BaseModel):
    id: UUID
    customer_name: str
    address: str
    items: list[str]
    status: OrderStatus
    assignment_state: AssignmentState
    assigned_at: datetime | None
    created_at: datetime
    driver: DriverResponse | None

    @classmethod
    def of(cls, detail: OrderDetail) -> "OrderResponse":
        """Build the full representation, with the driver nested or null."""
        order, driver = detail.order, detail.driver
        return cls(
            id=order.id,
            customer_name=order.customer_name,
            address=order.address,
            items=order.items,
            status=order.status,
            assignment_state=order.assignment_state,
            assigned_at=order.assigned_at,
            created_at=order.created_at,
            driver=(
                None
                if driver is None
                else DriverResponse(
                    id=driver.id, name=driver.name, status=driver.status
                )
            ),
        )


class OrderSummary(BaseModel):
    """The light representation the list answers with: no driver, so no second read."""

    id: UUID
    customer_name: str
    status: OrderStatus
    assignment_state: AssignmentState
    created_at: datetime

    @classmethod
    def of(cls, order: Order) -> "OrderSummary":
        return cls(
            id=order.id,
            customer_name=order.customer_name,
            status=order.status,
            assignment_state=order.assignment_state,
            created_at=order.created_at,
        )


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
