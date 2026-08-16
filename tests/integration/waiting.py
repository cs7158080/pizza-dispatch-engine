"""Polling helpers for state the API shows only after the worker acts on a message.

The two helpers fail for opposite reasons: one when a condition never arrives, the
other when it stops holding before its window is out. They are the only place the
suite waits, so no test carries a sleep of its own.
"""

import time
from collections.abc import Callable
from typing import Any

import httpx

# Long enough for a retry: an assignment that follows a rejection waits for the
# message to return from the wait queue, a whole retry delay away.
TIMEOUT_SECONDS = 20.0

# Covers one delivery rather than one retry cycle: the first delivery is never
# delayed, and every fault a negative assertion excludes would appear on it.
WINDOW_SECONDS = 3.0

# The cadence at which the condition is tested.
POLL_SECONDS = 0.25

Predicate = Callable[[dict[str, Any]], bool]


def read_order(client: httpx.Client, order_id: str) -> dict[str, Any]:
    """Read one order back, with its driver nested or null."""
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200, response.text
    order: dict[str, Any] = response.json()
    return order


def wait_until(
    client: httpx.Client, order_id: str, predicate: Predicate
) -> dict[str, Any]:
    """Poll the order until the predicate holds, and return the order it held for.

    A timeout reports the last order seen alongside the elapsed time; without it a
    red suite cannot tell an order still waiting for a driver from one that gave up
    or was assigned to an unexpected driver.

    Raises:
        AssertionError: The predicate did not hold within `TIMEOUT_SECONDS`.
    """
    deadline = time.monotonic() + TIMEOUT_SECONDS
    order = read_order(client, order_id)
    while not predicate(order):
        if time.monotonic() >= deadline:
            raise AssertionError(
                f"still not true after {TIMEOUT_SECONDS:.0f}s - last order: {order}"
            )
        time.sleep(POLL_SECONDS)
        order = read_order(client, order_id)
    return order


def stays(client: httpx.Client, order_id: str, predicate: Predicate) -> None:
    """Assert the predicate holds throughout the window, failing at the first breach.

    The condition is tested repeatedly rather than once at the end: a single read
    after a sleep would miss a state that appeared and was overwritten in between.

    Raises:
        AssertionError: The predicate stopped holding within `WINDOW_SECONDS`.
    """
    deadline = time.monotonic() + WINDOW_SECONDS
    while time.monotonic() < deadline:
        order = read_order(client, order_id)
        if not predicate(order):
            raise AssertionError(f"stopped being true - order: {order}")
        time.sleep(POLL_SECONDS)
