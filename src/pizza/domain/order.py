"""The order: its fields (4.1), its lifecycle (5.1), and what a transition reports back.

Layer 1 of 3.1 — standard library only. Nothing here knows that an order is stored,
published or served: identity and time arrive as arguments (4.7, 4.8), and the two facts
an adapter needs after a transition leave as a returned value rather than as a call.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from pizza.domain.errors import IllegalTransition


class OrderStatus(Enum):
    RECEIVED = "RECEIVED"
    PREPARING = "PREPARING"
    BAKING = "BAKING"
    READY = "READY"
    DELIVERED = "DELIVERED"


class AssignmentState(Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# 5.1's whole graph. Terminality is a missing key rather than a separate rule, and the
# same lookup rejects skipping, reversing and re-sending the current status (4.9).
_NEXT = {
    OrderStatus.RECEIVED: OrderStatus.PREPARING,
    OrderStatus.PREPARING: OrderStatus.BAKING,
    OrderStatus.BAKING: OrderStatus.READY,
    OrderStatus.READY: OrderStatus.DELIVERED,
}


@dataclass(frozen=True)
class TransitionResult:
    """What the caller must do next, decided here so no adapter decides it."""

    must_publish: bool  # 5.3
    releases_driver: bool  # 5.6


@dataclass
class Order:
    id: UUID
    customer_name: str
    address: str
    items: list[str]
    status: OrderStatus
    assignment_state: AssignmentState
    driver_id: UUID | None
    assigned_at: datetime | None
    created_at: datetime

    @classmethod
    def new(
        cls,
        id: UUID,
        customer_name: str,
        address: str,
        items: list[str],
        now: datetime,
    ) -> "Order":
        """The only place R1's initial status and 4.4's initial state are written."""
        return cls(
            id=id,
            customer_name=customer_name,
            address=address,
            items=items,
            status=OrderStatus.RECEIVED,
            assignment_state=AssignmentState.PENDING,
            driver_id=None,
            assigned_at=None,
            created_at=now,
        )

    def advance_to(self, requested_status: OrderStatus) -> TransitionResult:
        """Move one step forward, or refuse (5.1, 5.2)."""
        if _NEXT.get(self.status) is not requested_status:
            raise IllegalTransition(self.status, requested_status)
        self.status = requested_status
        if (
            self.status is OrderStatus.DELIVERED
            and self.assignment_state is not AssignmentState.FAILED
        ):
            self.assignment_state = AssignmentState.COMPLETED
        return TransitionResult(
            must_publish=self.status in (OrderStatus.BAKING, OrderStatus.READY),
            releases_driver=self.status is OrderStatus.DELIVERED,
        )

    def can_be_assigned(self) -> bool:
        """5.5: no driver yet, and not delivered. Both clauses are load-bearing."""
        return self.driver_id is None and self.status is not OrderStatus.DELIVERED

    def assign_to(self, driver_id: UUID, now: datetime) -> None:
        """Write 4.4's triple together. The caller asks can_be_assigned() first (8.1)."""
        self.driver_id = driver_id
        self.assignment_state = AssignmentState.ASSIGNED
        self.assigned_at = now

    def mark_dispatch_failed(self) -> None:
        """8.3's terminal record, ignored once the order moved on (4.9)."""
        if not self.can_be_assigned():
            return
        self.assignment_state = AssignmentState.FAILED
