"""The interactive menu loop and its five actions.

One order is remembered, by identifier alone, for the life of the process. Every
screen that shows it fetches it again, because the worker changes orders between
actions and a cached copy would be stale.

The status list is only displayed and selected from. Which transition is legal is
decided by the API, never derived here from the order's current status.

Nothing typed here is validated before it is sent: a value the rules refuse comes
back as an error the API describes.
"""

from typing import Any
from uuid import UUID

from pizza.entrypoints.cli import render
from pizza.entrypoints.cli.client import (
    STATUSES,
    ApiClient,
    ApiError,
    TransportFailure,
    UnexpectedResponse,
)

_ACTIONS = (
    "Place an order",
    "Register a driver",
    "List orders and select one",
    "Update the selected order's status",
    "Quit",
)


def run_menu(api: ApiClient) -> None:
    """Run the menu until the user quits or input ends.

    End of input is an ordinary exit: a container started without a terminal reads
    EOF at the first prompt, which is not a failure.
    """
    try:
        _loop(api)
    except (EOFError, KeyboardInterrupt):
        print()


def _loop(api: ApiClient) -> None:
    selected: UUID | None = None
    while True:
        render.block(
            "Pizza Dispatch",
            [f"{number}. {action}" for number, action in enumerate(_ACTIONS, 1)],
        )
        choice = _prompt(f"Choose [1-{len(_ACTIONS)}]")
        try:
            if choice == "1":
                _place_order(api)
            elif choice == "2":
                _register_driver(api)
            elif choice == "3":
                chosen = _select_order(api)
                if chosen is not None:
                    selected = chosen
            elif choice == "4":
                _update_status(api, selected)
            elif choice == "5":
                return
            else:
                render.note(f"Choose a number from 1 to {len(_ACTIONS)}.")
        except ApiError as error:
            render.api_error(error.status, error.detail)
        except TransportFailure as error:
            render.transport_failure(error.base_url)
        except UnexpectedResponse as error:
            render.unexpected(error.status, error.body)


def _place_order(api: ApiClient) -> None:
    customer_name = _prompt("Customer name")
    address = _prompt("Address")
    typed = _prompt("Items, separated by commas")
    created = api.place_order(customer_name, address, typed.split(",") if typed else [])
    render.success(f"Order placed: {created['id']}")


def _register_driver(api: ApiClient) -> None:
    created = api.register_driver(_prompt("Driver name"))
    render.success(f"Driver registered: {created['id']}")


def _select_order(api: ApiClient) -> UUID | None:
    """List the orders and open the one that was picked.

    Selection triggers a fetch, because the list carries no driver and the numbering
    is regenerated on every listing.
    """
    orders = api.list_orders()
    if not orders:
        render.note("No orders yet.")
        return None

    render.block(
        "Orders",
        render.table(
            ("#", "Customer", "Status", "Assignment", "Created"),
            [
                (
                    str(number),
                    order["customer_name"],
                    order["status"],
                    order["assignment_state"],
                    order["created_at"],
                )
                for number, order in enumerate(orders, 1)
            ],
        ),
    )

    picked = _pick(f"Select [1-{len(orders)}], or Enter to return", len(orders))
    if picked is None:
        return None
    order_id = UUID(orders[picked - 1]["id"])
    _show(api.get_order(order_id))
    return order_id


def _update_status(api: ApiClient, selected: UUID | None) -> None:
    if selected is None:
        render.note("Select an order first, with option 3.")
        return

    order = api.get_order(selected)
    render.block(
        "Update status",
        [
            render.chain(STATUSES, order["status"]),
            "",
            *(f"{number}. {status}" for number, status in enumerate(STATUSES, 1)),
        ],
    )

    picked = _pick(f"Choose [1-{len(STATUSES)}], or Enter to return", len(STATUSES))
    if picked is None:
        return
    updated = api.advance_status(selected, STATUSES[picked - 1])
    render.success(f"Status is now {updated['status']}.")
    _show(updated)


def _show(order: dict[str, Any]) -> None:
    driver = order["driver"]
    render.block(
        "Order",
        render.fields(
            [
                ("Id", order["id"]),
                ("Customer", order["customer_name"]),
                ("Address", order["address"]),
                ("Items", ", ".join(order["items"])),
                ("Status", order["status"]),
                ("Assignment", order["assignment_state"]),
                ("Assigned at", order["assigned_at"] or "-"),
                ("Created", order["created_at"]),
                ("Driver", _driver(driver)),
            ]
        ),
    )


def _driver(driver: dict[str, Any] | None) -> str:
    return "-" if driver is None else f"{driver['name']} ({driver['status']})"


def _pick(label: str, count: int) -> int | None:
    """Read one number from the displayed list, or None.

    An unusable answer prints a note and returns None; it never becomes a request.
    """
    answer = _prompt(label)
    if not answer:
        return None
    if not answer.isdigit() or not 1 <= int(answer) <= count:
        render.note(f"Choose a number from 1 to {count}.")
        return None
    return int(answer)


def _prompt(label: str) -> str:
    return input(f"\n{render.BOLD}{label}:{render.RESET} ")
