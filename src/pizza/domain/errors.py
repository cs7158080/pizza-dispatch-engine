"""Business errors: outcomes the rules refuse.

The API maps each to a status code; nothing here knows a code. Errors describing a failed
port live beside that port, in `application/ports.py`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from pizza.domain.order import OrderStatus


class IllegalTransition(Exception):
    """The requested status does not follow the current one."""

    def __init__(
        self, current_status: OrderStatus, requested_status: OrderStatus
    ) -> None:
        super().__init__(
            f"cannot move from {current_status.value} to {requested_status.value}"
        )
        self.current_status = current_status
        self.requested_status = requested_status


class OrderNotFound(Exception):
    """No order carries this identifier."""

    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"no order with id {order_id}")
        self.order_id = order_id
