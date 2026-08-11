"""Typed business errors (5.2): outcomes the rules refuse, not process faults.

`entrypoints/api/errors.py` maps each to a status code as one registered handler (3.1);
nothing here knows a code. Errors describing a failed port live beside that port in
`application/ports.py` instead — an unreachable broker is not a violated rule.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from pizza.domain.order import OrderStatus


class IllegalTransition(Exception):
    """5.1's graph refused the move. The API maps this to 409 (5.2)."""

    def __init__(
        self, current_status: OrderStatus, requested_status: OrderStatus
    ) -> None:
        super().__init__(
            f"cannot move from {current_status.value} to {requested_status.value}"
        )
        self.current_status = current_status
        self.requested_status = requested_status


class OrderNotFound(Exception):
    """No order carries this identifier. The API maps this to 404."""

    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"no order with id {order_id}")
        self.order_id = order_id
