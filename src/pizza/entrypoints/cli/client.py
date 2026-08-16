"""What the CLI knows about the API, and the three ways a call can fail.

A client holds the published contract and nothing beyond it: the paths, the bodies
it sends and reads, and the names of the five statuses. It never decides which
status may follow which — the menu offers all five and the API answers.

Every method returns the parsed body or raises. The three errors below are the
whole vocabulary a caller has to handle: an answer the contract describes, a call
that never reached the server, and anything else.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

import httpx

# The statuses the API publishes, in the order it declares them. The menu offers
# every one of them and derives none from another, so this list is displayed and
# selected from — never used to work out what comes next.
STATUSES = ("RECEIVED", "PREPARING", "BAKING", "READY", "DELIVERED")

# One value for every call. It clears the longest bounded wait the API can impose
# on a status update, so the client never abandons a request the API is about to
# answer successfully.
_TIMEOUT_SECONDS = 15.0

# The failures the contract describes a body for. Anything else is a defect rather
# than a covered path, and is shown as one.
_DESCRIBED_FAILURES = frozenset({404, 409, 422, 503})


@dataclass(frozen=True)
class FieldFault:
    """One entry of a validation failure: where it was, and what was wrong."""

    location: str
    message: str


class CliError(Exception):
    """Anything that stopped a call from answering."""


class ApiError(CliError):
    """The API refused, in one of the ways its contract describes.

    `detail` is a sentence where the server can state one, and one entry per field
    where the failure is per-field; the type varies with the class of failure.
    """

    def __init__(self, status: int, detail: str | tuple[FieldFault, ...]) -> None:
        super().__init__(f"the API answered {status}")
        self.status = status
        self.detail = detail


class TransportFailure(CliError):
    """The call never reached the API, so there is no status and no body."""

    def __init__(self, base_url: str) -> None:
        super().__init__(f"could not reach {base_url}")
        self.base_url = base_url


class UnexpectedResponse(CliError):
    """An answer outside the contract, carried raw so it is not dressed up."""

    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"the API answered {status}")
        self.status = status
        self.body = body


class ApiClient:
    """One connection to the API, for the life of the process."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._http = httpx.Client(base_url=base_url, timeout=_TIMEOUT_SECONDS)

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self._http.close()

    def place_order(
        self, customer_name: str, address: str, items: list[str]
    ) -> dict[str, Any]:
        created: dict[str, Any] = self._call(
            "POST",
            "/orders",
            {"customer_name": customer_name, "address": address, "items": items},
        )
        return created

    def register_driver(self, name: str) -> dict[str, Any]:
        created: dict[str, Any] = self._call("POST", "/drivers", {"name": name})
        return created

    def list_orders(self) -> list[dict[str, Any]]:
        orders: list[dict[str, Any]] = self._call("GET", "/orders")
        return orders

    def get_order(self, order_id: UUID) -> dict[str, Any]:
        order: dict[str, Any] = self._call("GET", f"/orders/{order_id}")
        return order

    def advance_status(self, order_id: UUID, status: str) -> dict[str, Any]:
        order: dict[str, Any] = self._call(
            "PATCH", f"/orders/{order_id}/status", {"status": status}
        )
        return order

    def _call(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        """Perform one request and classify what came back.

        Every method routes through here, so the three shapes are decided once.
        """
        try:
            response = self._http.request(method, path, json=body)
        except httpx.RequestError as error:
            raise TransportFailure(self._base_url) from error

        if response.status_code in _DESCRIBED_FAILURES:
            raise ApiError(response.status_code, _detail(response))
        if response.is_error:
            raise UnexpectedResponse(response.status_code, response.text)

        try:
            return response.json()
        except ValueError as error:
            # A success that is not JSON is outside the contract, not a fault of
            # the connection.
            raise UnexpectedResponse(response.status_code, response.text) from error


def _detail(response: httpx.Response) -> str | tuple[FieldFault, ...]:
    """The error body, as the sentence or the field list the contract carries."""
    try:
        body: dict[str, Any] = response.json()
    except ValueError:
        return response.text

    detail = body.get("detail")
    if isinstance(detail, list):
        return tuple(_fault(entry) for entry in detail)
    if isinstance(detail, str):
        return detail
    return response.text


def _fault(entry: dict[str, Any]) -> FieldFault:
    """Where one value was rejected, and why.

    The leading element is dropped only when it is `body`: a path parameter names
    its own source, and a failure on the whole body carries nothing else.
    """
    parts = [str(part) for part in entry.get("loc", ())]
    if len(parts) > 1 and parts[0] == "body":
        parts = parts[1:]
    return FieldFault(".".join(parts) or "body", str(entry.get("msg", "")))
