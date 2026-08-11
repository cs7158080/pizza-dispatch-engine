"""The driver: four fields (4.3) and the two-state life 5.8 fixes.

Layer 1 of 3.1 — standard library only, and no import of `order.py`: the relationship is
held once, on `orders.driver_id` (4.4), and a driver never mutates an order. Coordinating
the two writes is the use case's job (4.9, 3.5).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class DriverStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"


@dataclass
class Driver:
    id: UUID
    name: str
    status: DriverStatus
    created_at: datetime

    @classmethod
    def new(cls, id: UUID, name: str, now: datetime) -> "Driver":
        """A registered driver is available. `created_at` is 5.4's tie-breaker."""
        return cls(id=id, name=name, status=DriverStatus.AVAILABLE, created_at=now)

    def mark_busy(self) -> None:
        """Taken by an order. The claim that selected them is 8.9's, in the adapter."""
        self.status = DriverStatus.BUSY

    def release(self) -> None:
        """Back into the pool, on the transition into DELIVERED (5.6)."""
        self.status = DriverStatus.AVAILABLE
