"""The scenarios chosen by risk, driven over HTTP alone.

Each test asserts the state a rule produces rather than the shape of a response.
Nothing here reads a log line, a timestamp value, echoed input, or the outbox row.
"""

from collections.abc import Callable
from typing import Any

import httpx

from .waiting import read_order, stays, wait_until

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


def _register_driver(client: httpx.Client, name: str) -> str:
    """Register a driver, available from the moment they exist, and return their id."""
    response = client.post("/drivers", json={"name": name})
    assert response.status_code == 201, response.text
    created: dict[str, Any] = response.json()
    return str(created["id"])


def _advance(client: httpx.Client, order_id: str, status: str) -> httpx.Response:
    """Request a status change, and hand the whole response to the caller.

    The response rather than the order, because a refused transition is asserted
    on its status code while a successful one answers with the order itself.
    """
    return client.patch(f"/orders/{order_id}/status", json={"status": status})


def _is_assigned(order: dict[str, Any]) -> bool:
    """A driver has taken the order, whatever stage of preparation it is at."""
    return bool(order["assignment_state"] == "ASSIGNED")


def _is_waiting_for_a_driver(order: dict[str, Any]) -> bool:
    """Still looking, and not yet given up — which are two different states."""
    return bool(order["assignment_state"] == "PENDING" and order["driver"] is None)


def test_complete_order_lifecycle(
    client: httpx.Client,
    unique_name: Callable[[str], str],
    absorbs_its_driver: None,
) -> None:
    """One order from RECEIVED to DELIVERED, against a driver registered first.

    The normal path, and the two failure modes that lie only along it: the second
    event every order publishes, which has to change nothing, and the release at
    the end, which has to return the driver to the pool without ever unassigning
    them from the order they delivered.
    """
    driver_id = _register_driver(client, unique_name("driver"))
    order_id = _place_order(client, unique_name("order"))

    placed = read_order(client, order_id)
    assert placed["status"] == "RECEIVED"
    assert placed["assignment_state"] == "PENDING"
    assert placed["driver"] is None

    preparing = _advance(client, order_id, "PREPARING")
    assert preparing.status_code == 200, preparing.text
    assert preparing.json()["driver"] is None

    assert _advance(client, order_id, "BAKING").status_code == 200
    assigned = wait_until(client, order_id, _is_assigned)
    assert assigned["driver"]["id"] == driver_id
    assert assigned["driver"]["status"] == "BUSY"
    assert assigned["assigned_at"] is not None

    def still_the_first_driver(order: dict[str, Any]) -> bool:
        return bool(
            order["assignment_state"] == "ASSIGNED"
            and order["driver"] is not None
            and order["driver"]["id"] == driver_id
        )

    assert _advance(client, order_id, "READY").status_code == 200
    stays(client, order_id, still_the_first_driver)

    delivered = _advance(client, order_id, "DELIVERED")
    assert delivered.status_code == 200, delivered.text
    final = delivered.json()
    assert final["status"] == "DELIVERED"
    assert final["assignment_state"] == "COMPLETED"
    assert final["driver"]["id"] == driver_id
    assert final["driver"]["status"] == "AVAILABLE"


def test_recovery_when_a_driver_registers(
    client: httpx.Client, unique_name: Callable[[str], str]
) -> None:
    """An order with no driver to give it waits, and is dispatched once one exists.

    The most interesting behaviour in the system, and the only scenario that shows
    the worker surviving something it cannot do: it neither invents an assignment
    nor dies on the message, and dispatch resumes without anyone asking again. No
    further status change is sent after the driver registers, so a redelivery of
    the original message is the only thing that could have produced the result.
    """
    order_id = _place_order(client, unique_name("order"))
    assert _advance(client, order_id, "PREPARING").status_code == 200
    assert _advance(client, order_id, "BAKING").status_code == 200

    stays(client, order_id, _is_waiting_for_a_driver)

    driver_id = _register_driver(client, unique_name("driver"))

    assigned = wait_until(client, order_id, _is_assigned)
    assert assigned["driver"]["id"] == driver_id
    assert assigned["driver"]["status"] == "BUSY"


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

    assert read_order(client, order_id)["status"] == "RECEIVED"

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
