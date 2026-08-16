"""Integration scenarios, chosen by risk and driven over HTTP alone.

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
    """Place an order and return its id, by which every test identifies it."""
    response = client.post(
        "/orders",
        json={"customer_name": customer_name, "address": _ADDRESS, "items": _ITEMS},
    )
    assert response.status_code == 201, response.text
    created: dict[str, Any] = response.json()
    return str(created["id"])


def _register_driver(client: httpx.Client, name: str) -> str:
    """Register a driver, available from the start, and return their id."""
    response = client.post("/drivers", json={"name": name})
    assert response.status_code == 201, response.text
    created: dict[str, Any] = response.json()
    return str(created["id"])


def _advance(client: httpx.Client, order_id: str, status: str) -> httpx.Response:
    """Request a status change and return the whole response.

    The response rather than the order, because a refused transition is asserted on
    its status code while a successful one answers with the order itself.
    """
    return client.patch(f"/orders/{order_id}/status", json={"status": status})


def _is_assigned(order: dict[str, Any]) -> bool:
    """Return whether a driver has taken the order, at any stage of preparation."""
    return bool(order["assignment_state"] == "ASSIGNED")


def _is_waiting_for_a_driver(order: dict[str, Any]) -> bool:
    """Return whether the order is still waiting, as opposed to having given up."""
    return bool(order["assignment_state"] == "PENDING" and order["driver"] is None)


def test_complete_order_lifecycle(
    client: httpx.Client,
    unique_name: Callable[[str], str],
    absorbs_its_driver: None,
) -> None:
    """Scenario: one order runs from RECEIVED to DELIVERED, with a driver available.

    Why it matters: it covers the two failure modes that occur only on the normal
    path. The second event every order publishes must change nothing, and the release
    at the end must return the driver to the pool without unassigning them from the
    order they delivered.
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
    """Scenario: an order with no driver waits, then is dispatched once one registers.

    Why it matters: it is the only scenario showing the worker survive a request it
    cannot satisfy. It neither invents an assignment nor dies on the message, and
    dispatch resumes on its own. No further status change is sent after the driver
    registers, so only a redelivery of the original message could produce this result.
    """
    order_id = _place_order(client, unique_name("order"))
    assert _advance(client, order_id, "PREPARING").status_code == 200
    assert _advance(client, order_id, "BAKING").status_code == 200

    stays(client, order_id, _is_waiting_for_a_driver)

    driver_id = _register_driver(client, unique_name("driver"))

    assigned = wait_until(client, order_id, _is_assigned)
    assert assigned["driver"]["id"] == driver_id
    assert assigned["driver"]["status"] == "BUSY"


def test_one_driver_two_orders(
    client: httpx.Client, unique_name: Callable[[str], str]
) -> None:
    """Scenario: one driver and two orders; the second waits for the first to deliver.

    Why it matters: this is the only scenario combining release with retry. If the
    claim ignored whether a driver was already busy, or failed to mark them busy in
    the same transaction, both orders would show the same driver — an invariant
    spanning two tables that no database constraint can hold. Delivering the assigned
    order then proves that release really returns a driver to the pool, rather than
    only flipping a status, and that the waiting message comes back.
    """
    driver_id = _register_driver(client, unique_name("driver"))
    order_ids = [_place_order(client, unique_name(f"order{n}")) for n in (1, 2)]
    for order_id in order_ids:
        assert _advance(client, order_id, "PREPARING").status_code == 200
        assert _advance(client, order_id, "BAKING").status_code == 200

    def either_order_has_a_driver(order: dict[str, Any]) -> bool:
        return _is_assigned(order) or _is_assigned(read_order(client, order_ids[1]))

    wait_until(client, order_ids[0], either_order_has_a_driver)

    settled = [read_order(client, order_id) for order_id in order_ids]
    taken = [order for order in settled if _is_assigned(order)]
    waiting = [order for order in settled if _is_waiting_for_a_driver(order)]
    assert len(taken) == 1, settled
    assert len(waiting) == 1, settled
    assert taken[0]["driver"]["id"] == driver_id
    assert taken[0]["driver"]["status"] == "BUSY"

    stays(client, waiting[0]["id"], _is_waiting_for_a_driver)

    assert _advance(client, taken[0]["id"], "READY").status_code == 200
    assert _advance(client, taken[0]["id"], "DELIVERED").status_code == 200

    handed_over = wait_until(client, waiting[0]["id"], _is_assigned)
    assert handed_over["driver"]["id"] == driver_id
    assert handed_over["driver"]["status"] == "BUSY"


def test_illegal_transition_is_refused(
    client: httpx.Client, unique_name: Callable[[str], str]
) -> None:
    """Scenario: a skipped stage and a re-sent one are both refused, and neither lands.

    Why it matters: the chain is strictly linear and single-step, and the requirement
    is worded in a way that makes skipping look permissible, so this is the reading a
    reviewer probes first. Re-sending the current status settles whether a repeated
    PATCH publishes a second event.
    """
    order_id = _place_order(client, unique_name("order"))

    assert _advance(client, order_id, "BAKING").status_code == 409

    assert read_order(client, order_id)["status"] == "RECEIVED"

    assert _advance(client, order_id, "RECEIVED").status_code == 409


def test_invalid_input_is_refused(
    client: httpx.Client, unique_name: Callable[[str], str]
) -> None:
    """Scenario: three malformed requests are refused at the edge, before the core.

    Why it matters: the item bounds and the rejection of unknown fields are
    declarations rather than code, which a schema rewrite can drop with nothing else
    noticing. The third request separates a typo from a broken rule: an unrecognised
    status answers 422 where an illegal transition answers 409, so the test above
    cannot pass on a spelling mistake.
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
