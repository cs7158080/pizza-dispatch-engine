"""The order: its fields, its status lifecycle, and what a transition reports back.

Identity and time arrive as arguments; the entity reaches for neither.
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


# The whole legal graph: only the adjacent status is reachable, and DELIVERED is
# terminal because it has no entry.
_NEXT = {
    OrderStatus.RECEIVED: OrderStatus.PREPARING,
    OrderStatus.PREPARING: OrderStatus.BAKING,
    OrderStatus.BAKING: OrderStatus.READY,
    OrderStatus.READY: OrderStatus.DELIVERED,
}


@dataclass(frozen=True)
class TransitionResult:
    """What the caller must do after a successful transition."""

    must_publish: bool
    releases_driver: bool


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
        """Build a fresh order. The generated constructor rebuilds a stored one."""
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
        """Move one step forward, or raise IllegalTransition."""
        if _NEXT.get(self.status) is not requested_status:
            raise IllegalTransition(self.status, requested_status)
        self.status = requested_status
        # FAILED records that dispatch gave up and is not overwritten by delivery.
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
        """No driver yet, and not delivered."""
        return self.driver_id is None and self.status is not OrderStatus.DELIVERED

    def assign_to(self, driver_id: UUID, now: datetime) -> None:
        """Record the assignment. The caller asks can_be_assigned() first."""
        self.driver_id = driver_id
        self.assignment_state = AssignmentState.ASSIGNED
        self.assigned_at = now

    def mark_dispatch_failed(self) -> None:
        """Record that no driver was found. Ignored once the order has moved on."""
        if not self.can_be_assigned():
            return
        self.assignment_state = AssignmentState.FAILED
