"""Request and response models of the HTTP API.

The request models are the edge validation: unknown fields are forbidden and every
bound is declared, so no hand-written check stands between the wire and the core.

The response models assemble the shapes the API promises, including the nested
driver, from the types the application layer returns.
"""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from pizza.application.queries import OrderDetail
from pizza.domain.driver import DriverStatus
from pizza.domain.order import AssignmentState, Order, OrderStatus

# Trimmed before the length is checked, so a value of only spaces is rejected and
# the stored value is the one that was measured.
_Text100 = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
_Text200 = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]


class _Request(BaseModel):
    """Base of every request model: unknown fields are rejected, not ignored."""

    model_config = ConfigDict(extra="forbid")


class CreateOrderRequest(_Request):
    customer_name: _Text100
    address: _Text200
    items: list[_Text100] = Field(min_length=1, max_length=20)


class UpdateStatusRequest(_Request):
    # The domain enum: an unrecognised status is rejected before reaching the core.
    status: OrderStatus


class RegisterDriverRequest(_Request):
    name: _Text100


class Created(BaseModel):
    """Body returned by both creation endpoints: the generated identifier."""

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
    """Light representation used by the list endpoint: no driver, so no second read."""

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
