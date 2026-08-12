"""The tables, and the two invariants a single writer cannot hold for itself.

The schema enforces what concurrency can break: that one driver carries at most one
assigned order, and that an assigned order names both a driver and a time. Everything
else a rule can hold in one place is held in the layer that owns it.

Columns carry no `server_default`: identity is generated in the application and every
timestamp is one read of the clock, so a database default would be a second clock no
test can control.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pizza.domain.driver import DriverStatus
from pizza.domain.order import AssignmentState, OrderStatus


def _one_of(column: str, values: type[Enum]) -> str:
    """Render a CHECK over an enum's values, so the column cannot outlive them."""
    listed = ", ".join(f"'{member.value}'" for member in values)
    return f"{column} IN ({listed})"


class Base(DeclarativeBase):
    pass


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    customer_name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    items: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    assignment_state: Mapped[str] = mapped_column(Text, nullable=False)
    driver_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("drivers.id"), nullable=True
    )
    assigned_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )

    __table_args__ = (
        CheckConstraint(_one_of("status", OrderStatus), name="ck_orders_status"),
        CheckConstraint(
            _one_of("assignment_state", AssignmentState),
            name="ck_orders_assignment_state",
        ),
        CheckConstraint(
            "assignment_state <> 'ASSIGNED'"
            " OR (driver_id IS NOT NULL AND assigned_at IS NOT NULL)",
            name="ck_orders_assigned_has_driver_and_time",
        ),
        Index(
            "uq_orders_one_assigned_order_per_driver",
            "driver_id",
            unique=True,
            postgresql_where=text("assignment_state = 'ASSIGNED'"),
        ),
    )


class DriverModel(Base):
    __tablename__ = "drivers"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )

    __table_args__ = (
        CheckConstraint(_one_of("status", DriverStatus), name="ck_drivers_status"),
    )


class OutboxModel(Base):
    __tablename__ = "outbox"

    event_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
