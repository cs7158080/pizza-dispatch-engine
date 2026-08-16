"""Unit tests for the order rules, exercised against the entity alone.

Each test states the scenario it covers and the failure it would catch.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from pizza.domain.errors import IllegalTransition
from pizza.domain.order import AssignmentState, Order, OrderStatus

_NOW = datetime(2026, 8, 11, 12, 0, tzinfo=UTC)

_TO_DELIVERED = (
    OrderStatus.PREPARING,
    OrderStatus.BAKING,
    OrderStatus.READY,
    OrderStatus.DELIVERED,
)


def _an_order() -> Order:
    return Order.new(
        id=uuid4(),
        customer_name="Dana",
        address="1 Herzl St",
        items=["Margherita"],
        now=_NOW,
    )


def test_the_lifecycle_walks_forward_once_per_step() -> None:
    """Scenario: an order walks the full lifecycle, one status at a time.

    Why it matters: a publish flag on the wrong transition would dispatch an order
    that is not baking yet, and a release flag on the wrong one would return a driver
    mid-delivery. Neither is visible outside this test until an end-to-end run.
    """
    order = _an_order()
    expected = [
        (OrderStatus.PREPARING, False, False),
        (OrderStatus.BAKING, True, False),
        (OrderStatus.READY, True, False),
        (OrderStatus.DELIVERED, False, True),
    ]

    for target, must_publish, releases_driver in expected:
        result = order.advance_to(target)
        assert order.status is target
        assert result.must_publish is must_publish
        assert result.releases_driver is releases_driver


def test_skipping_reversing_and_repeating_are_all_refused() -> None:
    """Scenario: skipping, reversing and repeating a transition are all rejected.

    Why it matters: a skip would allow delivery without dispatch, and a successful
    repeat would publish ORDER_READY twice for one transition. The error carries both
    statuses, without which the API can only report an opaque conflict.
    """
    skipping = _an_order()
    with pytest.raises(IllegalTransition) as refused:
        skipping.advance_to(OrderStatus.BAKING)
    assert refused.value.current_status is OrderStatus.RECEIVED
    assert refused.value.requested_status is OrderStatus.BAKING
    assert skipping.status is OrderStatus.RECEIVED

    baking = _an_order()
    baking.advance_to(OrderStatus.PREPARING)
    baking.advance_to(OrderStatus.BAKING)

    with pytest.raises(IllegalTransition):
        baking.advance_to(OrderStatus.PREPARING)
    with pytest.raises(IllegalTransition):
        baking.advance_to(OrderStatus.BAKING)
    assert baking.status is OrderStatus.BAKING


def test_an_order_admits_exactly_one_driver() -> None:
    """Scenario: the assignment guard, on an assigned order and on a delivered one.

    Why it matters: without the first clause a second driver is given to an order
    already on its way. Without the second, a retried event assigns a driver after
    the only transition that releases them, leaking that driver from the pool with no
    interface reporting it.
    """
    assigned = _an_order()
    assert assigned.can_be_assigned() is True
    assigned.assign_to(driver_id=uuid4(), now=_NOW)
    assert assigned.can_be_assigned() is False

    delivered = _an_order()
    for step in _TO_DELIVERED:
        delivered.advance_to(step)
    assert delivered.can_be_assigned() is False


def test_a_failed_dispatch_survives_delivery() -> None:
    """Scenario: an order marked FAILED keeps that state after being delivered.

    Why it matters: FAILED is recorded nowhere else. Overwriting it on delivery would
    erase the record that no driver was ever found, through an unrelated status
    update.
    """
    order = _an_order()
    order.mark_dispatch_failed()
    assert order.assignment_state is AssignmentState.FAILED

    for step in _TO_DELIVERED:
        order.advance_to(step)

    assert order.status is OrderStatus.DELIVERED
    assert order.assignment_state is AssignmentState.FAILED


def test_giving_up_is_ignored_once_a_driver_is_assigned() -> None:
    """Scenario: giving up on dispatch is ignored once a driver has been assigned.

    Why it matters: two messages per order are in flight, so one can exhaust its retry
    budget after the other has assigned. Without the guard, the exhausted message
    would mark an order FAILED while a driver is delivering it.
    """
    order = _an_order()
    driver_id = uuid4()
    order.assign_to(driver_id=driver_id, now=_NOW)

    order.mark_dispatch_failed()

    assert order.assignment_state is AssignmentState.ASSIGNED
    assert order.driver_id == driver_id
