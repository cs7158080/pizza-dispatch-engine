"""The retry budget, as it is read back off the broker's own header."""

from typing import Any

from pizza.entrypoints.worker.consumer import rejection_count

_DISPATCH_QUEUE = "pizza.orders.dispatch"
_WAIT_QUEUE = "pizza.orders.dispatch.wait"


def _headers(rejections: int, expiries: int) -> dict[str, Any]:
    """A header table shaped as the broker writes it during the retry cycle."""
    return {
        "x-death": [
            {"queue": _WAIT_QUEUE, "reason": "expired", "count": expiries},
            {"queue": _DISPATCH_QUEUE, "reason": "rejected", "count": rejections},
        ]
    }


def test_only_rejections_from_the_dispatch_queue_count() -> None:
    """One entry of the header is the budget, and the message carries two.

    A message circling the retry cycle collects an entry for the rejections that
    sent it away and another for the expiries that brought it back, and the two
    advance one after the other. Summing them spends the budget in half the
    attempts; reading the wrong one spends it at the wrong moment. Either way
    nothing looks broken while it happens — the order really has no driver, so
    every log line stays truthful and the fault presents as an order that gives
    up too early, at a point no message or record explains.

    A first delivery carries no header at all, which is zero attempts rather
    than an unknown number.
    """
    assert rejection_count(None, _DISPATCH_QUEUE) == 0
    assert rejection_count({}, _DISPATCH_QUEUE) == 0
    assert rejection_count(_headers(rejections=3, expiries=2), _DISPATCH_QUEUE) == 3
