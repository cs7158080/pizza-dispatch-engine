"""Business errors: outcomes the rules refuse.

The API maps each to a status code; nothing here knows a code. Each message is
the sentence the API answers with, written once and addressed to a person. An
error describing a failed port lives beside that port, in `application/ports.py`.
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
            f"Cannot advance order from {current_status.value}"
            f" to {requested_status.value}"
        )
        self.current_status = current_status
        self.requested_status = requested_status


class OrderNotFound(Exception):
    """No order carries this identifier."""

    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"Order {order_id} not found")
        self.order_id = order_id
