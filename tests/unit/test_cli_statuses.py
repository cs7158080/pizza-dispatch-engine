"""The CLI's copy of the status names, against the domain's own.

The CLI may not import the core, so the five names exist twice and nothing in the
running system compares them. This test is that comparison.
"""

from pizza.domain.order import OrderStatus
from pizza.entrypoints.cli.client import STATUSES


def test_the_cli_lists_the_statuses_the_domain_declares() -> None:
    """Same names, same order — and the order is the half that fails silently.

    A renamed status shows up as a `422` the moment anyone selects it, which is
    visible. A reordered or extended chain does not: the status sub-menu draws the
    sequence from this list and marks where the order stands, so a stale copy
    renders a chain that is wrong and looks entirely correct.
    """
    assert list(STATUSES) == [status.value for status in OrderStatus]
