"""The one part of the topology that can be checked without a broker."""

from pizza.infrastructure.broker.topology import wait_queue_arguments


def test_the_wait_queue_holds_a_message_for_the_configured_delay() -> None:
    """The retry delay is configured in seconds and declared in milliseconds.

    Without the conversion the broker reads eight milliseconds instead of eight
    seconds, and the whole retry budget — sized so that a person has time to register
    a driver by hand — expires in a fraction of a second. Nothing looks broken while it
    happens: every log line still reports that no driver was available, so the fault
    presents as an order that cannot be rescued rather than as a wrong unit.
    """
    assert wait_queue_arguments(8)["x-message-ttl"] == 8000
