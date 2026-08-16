"""Unit test for the part of the broker topology checkable without a broker."""

from pizza.infrastructure.broker.topology import wait_queue_arguments


def test_the_wait_queue_holds_a_message_for_the_configured_delay() -> None:
    """Scenario: the retry delay, configured in seconds, is declared in milliseconds.

    Why it matters: without the conversion the broker reads eight milliseconds instead
    of eight seconds, and the retry budget — sized so a person can register a driver
    by hand — expires almost instantly. Nothing reports a fault while it happens: the
    logs still say no driver was available.
    """
    assert wait_queue_arguments(8)["x-message-ttl"] == 8000
