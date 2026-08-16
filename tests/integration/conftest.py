"""Fixtures shared by the integration scenarios: an HTTP client and unique names.

The suite speaks HTTP and nothing else, so the client is the only fixture holding
state. Names exist for whoever reads the data afterwards; tests identify their rows
by the id the API returned, never by name.
"""

import os
from collections.abc import Callable, Iterator
from uuid import uuid4

import httpx
import pytest

from pizza.config import load_client_settings

from .waiting import wait_until


@pytest.fixture(scope="session")
def client() -> Iterator[httpx.Client]:
    """Open one connection pool for the whole run, aimed at the configured API.

    The base URL comes from the environment rather than a literal, so the same suite
    runs from the host against the published port and from inside the network against
    the service name.
    """
    settings = load_client_settings(os.environ)
    with httpx.Client(base_url=settings.api_base_url) as opened:
        yield opened


@pytest.fixture
def unique_name(request: pytest.FixtureRequest) -> Callable[[str], str]:
    """Build names that identify the test which created the row, and never repeat."""

    def make(label: str) -> str:
        return f"{request.node.name}-{label}-{uuid4().hex[:8]}"

    return make


@pytest.fixture
def absorbs_its_driver(
    client: httpx.Client, unique_name: Callable[[str], str]
) -> Iterator[None]:
    """Consume the driver the test released, leaving the pool empty as it was found.

    Only one scenario ends with a driver back in the pool, so only one has to take it
    out again. Every test then begins and ends at zero available drivers, which is
    what lets them run in any order, as any subset, and twice.

    The teardown runs after a failure too. A failure that leaves the driver busy makes
    this order wait for the full timeout: noise on an already red run, accepted so
    that a driver is never left behind silently.
    """
    yield

    placed = client.post(
        "/orders",
        json={
            "customer_name": unique_name("absorb"),
            "address": "1 Test Street, Testville",
            "items": ["Margherita"],
        },
    )
    assert placed.status_code == 201, placed.text
    order_id = placed.json()["id"]

    for status in ("PREPARING", "BAKING"):
        moved = client.patch(f"/orders/{order_id}/status", json={"status": status})
        assert moved.status_code == 200, moved.text

    wait_until(client, order_id, lambda order: order["driver"] is not None)
