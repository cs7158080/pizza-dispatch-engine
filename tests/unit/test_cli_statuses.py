"""Unit test comparing the CLI's copy of the status names with the domain's own.

The CLI must not import the core, so the five names exist twice and nothing in the
running system compares them. This test is that comparison.
"""

from pizza.domain.order import OrderStatus
from pizza.entrypoints.cli.client import STATUSES


def test_the_cli_lists_the_statuses_the_domain_declares() -> None:
    """Scenario: the CLI's status list matches the domain's, in name and in order.

    Why it matters: a renamed status surfaces as a 422 the moment anyone selects it.
    A reordered or extended chain does not: the status sub-menu draws the sequence
    from this list, so a stale copy renders a wrong chain that looks correct.
    """
    assert list(STATUSES) == [status.value for status in OrderStatus]
