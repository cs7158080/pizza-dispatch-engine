"""The driver: four fields and a two-state life.

A driver carries one order at a time. The link to that order is held on the order, not
here, and a driver never mutates one.
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
        """Build a newly registered driver. `created_at` orders driver selection."""
        return cls(id=id, name=name, status=DriverStatus.AVAILABLE, created_at=now)

    def mark_busy(self) -> None:
        """Taken by an order."""
        self.status = DriverStatus.BUSY

    def release(self) -> None:
        """Back into the pool, once the order is delivered."""
        self.status = DriverStatus.AVAILABLE
