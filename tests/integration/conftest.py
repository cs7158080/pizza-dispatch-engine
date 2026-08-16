"""What every scenario is given: a client, and a name that collides with nothing.

The suite speaks HTTP and nothing else, so the client is the only fixture
holding state. Names exist for the person reading the data afterwards, never for a
test to search by — every test identifies its rows by the id the API returned.
"""

import os
from collections.abc import Callable, Iterator
from uuid import uuid4

import httpx
import pytest

from pizza.config import load_client_settings


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
