"""The screen: blocks, columns, colour, and the three ways a failure is shown.

Every block is a title, a rule, its content, and the same rule again. The rule is
as wide as the widest line in the block, so there is no width to keep in step with
anything and nothing is ever truncated to fit.

Nothing here is drawn with a character outside ASCII: the target is a container
seen through a Windows console, and a box-drawing character is what fails there.
Colour is disabled whenever the output is not a terminal, so a redirected stream
carries no escape sequences.

These functions take values and print. They read no input, hold no state, and
decide nothing about what should be shown.
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
    """A titled block, ruled to the width of its widest line.

    The colour applies to the title alone, so the rule is measured against text
    that carries no escape sequences.
    """
    rule = "-" * max([len(title), *(len(line) for line in lines)])
    print(f"\n{colour}{title}{RESET}")
    print(rule)
    for line in lines:
        print(line)
    print(rule)


def fields(pairs: Sequence[tuple[str, str]]) -> list[str]:
    """One `label: value` line per pair, labels padded to a common width."""
    width = max([len(label) for label, _ in pairs], default=0)
    return [f"{label + ':':<{width + 2}}{value}" for label, value in pairs]


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> list[str]:
    """Aligned columns, sized from the data, with nothing cut to fit."""
    widths = [
        max([len(headers[column]), *(len(row[column]) for row in rows)])
        for column in range(len(headers))
    ]
    return [_row(headers, widths), *(_row(row, widths) for row in rows)]


def chain(statuses: Sequence[str], current: str) -> str:
    """The status sequence, with the one the order is on marked.

    The sequence is given rather than known: this module draws what it is handed
    and never works out which status follows which.
    """
    return " -> ".join(
        f"[ {status} ]" if status == current else status for status in statuses
    )


def note(message: str) -> None:
    """One line, for something the user did that never became a request."""
    print(f"\n{message}")


def success(message: str) -> None:
    """One line confirming a call that answered."""
    print(f"\n{GREEN}{message}{RESET}")


def api_error(status: int, detail: str | tuple[FieldFault, ...]) -> None:
    """A refusal the API described, as a sentence or one line per field."""
    lines = (
        [detail]
        if isinstance(detail, str)
        else fields([(fault.location, fault.message) for fault in detail])
    )
    block(f"Error {status}", lines, RED)


def transport_failure(base_url: str) -> None:
    """A call that never arrived, naming what was addressed.

    What was addressed is the whole content: there is no status and no body, and
    any cause named here would be a guess printed as a fact.
    """
    block("Cannot reach the API", [f"No answer from {base_url}"], RED)


def unexpected(status: int, body: str) -> None:
    """An answer outside the contract, shown raw rather than dressed up."""
    block(f"Unexpected response {status}", [body or "(empty body)"], RED)


def _row(cells: Sequence[str], widths: Sequence[int]) -> str:
    return "  ".join(
        cell.ljust(width) for cell, width in zip(cells, widths, strict=True)
    ).rstrip()
