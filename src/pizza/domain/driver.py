"""Driver entity and its availability.

A driver carries one order at a time. The link to that order is held on the
order, not here.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class DriverStatus(Enum):
    """Whether the driver can be given an order."""

    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"


@dataclass
class Driver:
    id: UUID
    name: str
    status: DriverStatus
    created_at: datetime  # also the order in which drivers are selected

    @classmethod
    def new(cls, id: UUID, name: str, now: datetime) -> "Driver":
        """Create a newly registered driver, available from the start."""
        return cls(id=id, name=name, status=DriverStatus.AVAILABLE, created_at=now)

    def mark_busy(self) -> None:
        """Take the driver out of the available pool."""
        self.status = DriverStatus.BUSY

    def release(self) -> None:
        """Return the driver to the available pool."""
        self.status = DriverStatus.AVAILABLE
