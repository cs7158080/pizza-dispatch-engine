"""What every scenario is given: a client, and a name that collides with nothing.

The suite speaks HTTP and nothing else, so the client is the only fixture
holding state. Names exist for the person reading the data afterwards, never for a
test to search by — every test identifies its rows by the id the API returned.

The run's verdict is written from here too, since the suite is started by a
container whose output a person reads rather than a command they typed.
"""

import os
from collections.abc import Callable, Iterator
from uuid import uuid4

import httpx
import pytest

from pizza.config import load_client_settings

from .waiting import wait_until


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter, exitstatus: pytest.ExitCode
) -> None:
    """Write the run's verdict as a separator wide enough not to be scrolled past.

    Keyed on the exit status rather than on a count of failures, so a run that
    collected nothing at all reports FAIL instead of printing a green banner over
    an empty suite. It prints beside that status rather than between it and the
    caller, so nothing here can change what the run returns.
    """
    verdict = "PASS" if exitstatus == pytest.ExitCode.OK else "FAIL"
    terminalreporter.write_sep("=", verdict)


@pytest.fixture(scope="session")
def client() -> Iterator[httpx.Client]:
    """One connection pool for the whole run, aimed at the configured API.

    The base URL comes from the environment rather than a literal, so the same
    suite runs from the host against the published port and from inside the
    network against the service name.
    """
    settings = load_client_settings(os.environ)
    with httpx.Client(base_url=settings.api_base_url) as opened:
        yield opened


@pytest.fixture
def unique_name(request: pytest.FixtureRequest) -> Callable[[str], str]:
    """Builds a name that says which test created the row, and repeats never."""

    def make(label: str) -> str:
        return f"{request.node.name}-{label}-{uuid4().hex[:8]}"

    return make


@pytest.fixture
def absorbs_its_driver(
    client: httpx.Client, unique_name: Callable[[str], str]
) -> Iterator[None]:
    """Leaves the driver pool exactly as the test found it: empty.

    Only one scenario ends with a driver back in the pool, so only one has to take
    it out again. With this in place every test begins and ends at zero available
    drivers, which is what lets them run in any order, as any subset, and twice.

    It yields, so the absorption also happens when the test fails partway. A
    failure after the driver became busy leaves this order unassigned and ends at
    the waiting timeout — noise on a run that is already red, which is the price of
    never silently leaving a driver behind.
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
