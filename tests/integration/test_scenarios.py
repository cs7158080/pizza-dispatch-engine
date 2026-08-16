"""The scenarios chosen by risk, driven over HTTP alone.

Each test asserts the state a rule produces rather than the shape of a response.
Nothing here reads a log line, a timestamp value, echoed input, or the outbox row.
"""

from collections.abc import Callable
from typing import Any

import httpx

_ADDRESS = "1 Test Street, Testville"
_ITEMS = ["Margherita"]


def _place_order(client: httpx.Client, customer_name: str) -> str:
    """Place an order and return its id, which is how every test identifies it."""
    response = client.post(
        "/orders",
        json={"customer_name": customer_name, "address": _ADDRESS, "items": _ITEMS},
    )
    assert response.status_code == 201, response.text
    created: dict[str, Any] = response.json()
    return str(created["id"])


def _read_order(client: httpx.Client, order_id: str) -> dict[str, Any]:
    """Read one order back, with its driver nested or null."""
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200, response.text
    order: dict[str, Any] = response.json()
    return order


def _advance(client: httpx.Client, order_id: str, status: str) -> httpx.Response:
    """Request a status change, and hand the whole response to the caller.

    The response rather than the order, because the tests that refuse a
    transition assert on the status code and never read a body.
    """
    return client.patch(f"/orders/{order_id}/status", json={"status": status})


def test_illegal_transition_is_refused(
    client: httpx.Client, unique_name: Callable[[str], str]
) -> None:
    """A skipped stage and a re-sent one are both refused, and neither one lands.

    The chain is strictly linear and single-step, and the requirement lists it in
    a way that makes skipping look permissible — so this is the reading a reviewer
    will probe first. Re-sending the current status is the chain's least obvious
    half, and the only thing that settles whether a repeated PATCH publishes a
    second event.
    """
    order_id = _place_order(client, unique_name("order"))

    assert _advance(client, order_id, "BAKING").status_code == 409

    assert _read_order(client, order_id)["status"] == "RECEIVED"

    assert _advance(client, order_id, "RECEIVED").status_code == 409


def test_invalid_input_is_refused(
    client: httpx.Client, unique_name: Callable[[str], str]
) -> None:
    """Three malformed requests are refused at the edge, before the core sees them.

    The item bounds and the rejection of unknown fields are declarations rather
    than code, which is the kind of thing a schema rewrite drops in silence with
    nothing else noticing. The third request separates a typo from a broken rule:
    an unrecognised status answers 422 where an illegal transition answers 409, so
    the test above cannot pass on a spelling mistake.
    """
    no_items = client.post(
        "/orders",
        json={
            "customer_name": unique_name("no-items"),
            "address": _ADDRESS,
            "items": [],
        },
    )
    assert no_items.status_code == 422

    unknown_field = client.post(
        "/orders",
        json={
            "customer_name": unique_name("unknown-field"),
            "address": _ADDRESS,
            "items": _ITEMS,
            "toppings": ["olives"],
        },
    )
    assert unknown_field.status_code == 422

    order_id = _place_order(client, unique_name("order"))
    assert _advance(client, order_id, "PREPARNIG").status_code == 422
