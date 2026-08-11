"""The order: its fields, its status lifecycle, and what a transition reports.

Identity and time arrive as arguments; the entity reaches for neither.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from pizza.domain.errors import IllegalTransition


class OrderStatus(Enum):
    """The stages of an order, in the only sequence they may be reached."""

    RECEIVED = "RECEIVED"
    PREPARING = "PREPARING"
    BAKING = "BAKING"
    READY = "READY"
    DELIVERED = "DELIVERED"


class AssignmentState(Enum):
    """Whether a driver is coming, independently of how far the order has got."""

    PENDING = "PENDING"  # no driver yet, which is where every order starts
    ASSIGNED = "ASSIGNED"  # a driver took it
    COMPLETED = "COMPLETED"  # a driver took it and it was delivered
    FAILED = "FAILED"  # no driver was found before the retries ran out


# The whole legal graph: only the adjacent status is reachable. DELIVERED is
# terminal because it is not a key here.
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
    # Two views of one dispatch: `driver_id` is who took the order and is never
    # cleared, `assignment_state` is how that attempt ended.
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
        """Build a freshly placed order.

        Loading a stored one calls the dataclass constructor with all nine fields.
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
        """Move the order one step forward, or raise `IllegalTransition`.

        Returns the two facts the caller must act on: whether to publish, and
        whether to release the assigned driver.
        """
        if _NEXT.get(self.status) is not requested_status:
            raise IllegalTransition(self.status, requested_status)
        self.status = requested_status
        # FAILED is the only record that dispatch gave up, so delivery leaves it.
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
        """Report whether a driver may still be given to this order.

        The second clause is not redundant: a retrying event can arrive after
        delivery, and assigning then would mark a driver busy past the only
        transition that ever releases them.
        """
        return self.driver_id is None and self.status is not OrderStatus.DELIVERED

    def assign_to(self, driver_id: UUID, now: datetime) -> None:
        """Record which driver took the order, and when.

        There is no guard here; the caller asks `can_be_assigned` first.
        """
        self.driver_id = driver_id
        self.assignment_state = AssignmentState.ASSIGNED
        self.assigned_at = now

    def mark_dispatch_failed(self) -> None:
        """Record that no driver was found, unless the order has moved on."""
        if not self.can_be_assigned():
            return
        self.assignment_state = AssignmentState.FAILED
