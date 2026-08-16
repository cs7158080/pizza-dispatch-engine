"""Order entity, its status lifecycle, and its transition rules."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from pizza.domain.errors import IllegalTransition


class OrderStatus(Enum):
    """Stages of an order, in the only sequence they may be reached."""

    RECEIVED = "RECEIVED"
    PREPARING = "PREPARING"
    BAKING = "BAKING"
    READY = "READY"
    DELIVERED = "DELIVERED"


class AssignmentState(Enum):
    """Outcome of dispatch for an order, tracked separately from its status."""

    PENDING = "PENDING"  # no driver assigned yet; the initial state
    ASSIGNED = "ASSIGNED"  # a driver took the order
    COMPLETED = "COMPLETED"  # a driver took the order and it was delivered
    FAILED = "FAILED"  # no driver was found before the retries ran out


# The complete set of legal transitions. DELIVERED is terminal: it has no entry.
_NEXT = {
    OrderStatus.RECEIVED: OrderStatus.PREPARING,
    OrderStatus.PREPARING: OrderStatus.BAKING,
    OrderStatus.BAKING: OrderStatus.READY,
    OrderStatus.READY: OrderStatus.DELIVERED,
}


@dataclass(frozen=True)
class TransitionResult:
    """Actions the caller must take after a successful transition."""

    must_publish: bool
    releases_driver: bool


@dataclass
class Order:
    id: UUID
    customer_name: str
    address: str
    items: list[str]
    status: OrderStatus
    # `driver_id` records who took the order and is never cleared;
    # `assignment_state` records how that dispatch ended.
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
        """Create a newly placed order, in RECEIVED status and PENDING dispatch.

        Stored orders are rebuilt through the dataclass constructor instead.
        """
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
        """Advance the order to the next status in its lifecycle.

        Args:
            requested_status: Must be the status immediately following the current one.

        Returns:
            Whether an event must be published and whether the driver is released.

        Raises:
            IllegalTransition: The requested status does not follow the current one.
        """
        if _NEXT.get(self.status) is not requested_status:
            raise IllegalTransition(self.status, requested_status)
        self.status = requested_status
        # FAILED is the only record that dispatch gave up, so it is preserved.
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
        """Return whether the order may still be given a driver.

        Delivered orders are excluded: a retried dispatch event arriving after
        delivery would mark a driver busy past the only transition that
        releases them.
        """
        return self.driver_id is None and self.status is not OrderStatus.DELIVERED

    def assign_to(self, driver_id: UUID, now: datetime) -> None:
        """Record the driver that took the order and the time of assignment.

        Unguarded: callers must check `can_be_assigned` first.
        """
        self.driver_id = driver_id
        self.assignment_state = AssignmentState.ASSIGNED
        self.assigned_at = now

    def mark_dispatch_failed(self) -> None:
        """Mark dispatch as failed, unless the order has since moved on."""
        if not self.can_be_assigned():
            return
        self.assignment_state = AssignmentState.FAILED
