"""Unit test for the retry budget, read back off the broker's `x-death` header."""

from typing import Any

from pizza.entrypoints.worker.consumer import rejection_count

_DISPATCH_QUEUE = "pizza.orders.dispatch"
_WAIT_QUEUE = "pizza.orders.dispatch.wait"


def _headers(rejections: int, expiries: int) -> dict[str, Any]:
    """Build a header table shaped as the broker writes it during the retry cycle."""
    return {
        "x-death": [
            {"queue": _WAIT_QUEUE, "reason": "expired", "count": expiries},
            {"queue": _DISPATCH_QUEUE, "reason": "rejected", "count": rejections},
        ]
    }


def test_only_rejections_from_the_dispatch_queue_count() -> None:
    """Scenario: only rejections from the dispatch queue count towards the budget.

    Why it matters: a message circling the retry cycle collects one entry for the
    rejections that sent it away and another for the expiries that brought it back,
    and the two advance in step. Summing them spends the budget in half the attempts;
    reading the wrong one spends it at the wrong moment. Neither is visible in the
    logs, which truthfully report that no driver was available.

    A first delivery carries no header at all, which counts as zero attempts.
    """
    assert rejection_count(None, _DISPATCH_QUEUE) == 0
    assert rejection_count({}, _DISPATCH_QUEUE) == 0
    assert rejection_count(_headers(rejections=3, expiries=2), _DISPATCH_QUEUE) == 3
