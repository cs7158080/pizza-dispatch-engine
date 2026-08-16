"""Terminal output: blocks, columns, colour, and the three failure screens.

Every block is a title, a rule, its content, and the rule again. The rule is as wide
as the widest line, so no fixed width has to be maintained and nothing is truncated.

Output is ASCII only: the target is a container viewed through a Windows console,
where box-drawing characters fail. Colour is disabled when stdout is not a terminal,
so a redirected stream carries no escape sequences.

These functions take values and print them. They read no input, hold no state, and
decide nothing about what is shown.
"""

import sys
from collections.abc import Sequence

from pizza.entrypoints.cli.client import FieldFault

_TTY = sys.stdout.isatty()

RED = "\033[31m" if _TTY else ""
GREEN = "\033[32m" if _TTY else ""
BOLD = "\033[1m" if _TTY else ""
RESET = "\033[0m" if _TTY else ""


def block(title: str, lines: Sequence[str], colour: str = BOLD) -> None:
    """Print a titled block, ruled to the width of its widest line.

    The colour applies to the title alone, so the rule is measured against text that
    carries no escape sequences.
    """
    rule = "-" * max([len(title), *(len(line) for line in lines)])
    print(f"\n{colour}{title}{RESET}")
    print(rule)
    for line in lines:
        print(line)
    print(rule)


def fields(pairs: Sequence[tuple[str, str]]) -> list[str]:
    """Render one `label: value` line per pair, labels padded to a common width."""
    width = max([len(label) for label, _ in pairs], default=0)
    return [f"{label + ':':<{width + 2}}{value}" for label, value in pairs]


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> list[str]:
    """Render aligned columns, sized from the data, with nothing truncated."""
    widths = [
        max([len(headers[column]), *(len(row[column]) for row in rows)])
        for column in range(len(headers))
    ]
    return [_row(headers, widths), *(_row(row, widths) for row in rows)]


def chain(statuses: Sequence[str], current: str) -> str:
    """Render the status sequence with the current status marked.

    The sequence is passed in rather than known here: this module draws what it is
    given and never derives which status follows which.
    """
    return " -> ".join(
        f"[ {status} ]" if status == current else status for status in statuses
    )


def note(message: str) -> None:
    """Print one line about an input that never became a request."""
    print(f"\n{message}")


def success(message: str) -> None:
    """Print one line confirming a successful call."""
    print(f"\n{GREEN}{message}{RESET}")


def api_error(status: int, detail: str | tuple[FieldFault, ...]) -> None:
    """Print a refusal the API described, as a message or one line per field."""
    lines = (
        [detail]
        if isinstance(detail, str)
        else fields([(fault.location, fault.message) for fault in detail])
    )
    block(f"Error {status}", lines, RED)


def transport_failure(base_url: str) -> None:
    """Print that a call never reached the API, naming the address that was tried.

    The address is all there is to show: there is no status and no body, and naming
    a cause here would be a guess presented as a fact.
    """
    block("Cannot reach the API", [f"No answer from {base_url}"], RED)


def unexpected(status: int, body: str) -> None:
    """Print a response outside the contract, with its body shown raw."""
    block(f"Unexpected response {status}", [body or "(empty body)"], RED)


def _row(cells: Sequence[str], widths: Sequence[int]) -> str:
    return "  ".join(
        cell.ljust(width) for cell, width in zip(cells, widths, strict=True)
    ).rstrip()
