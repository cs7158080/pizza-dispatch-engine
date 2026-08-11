"""The order rules, proved against the entity alone with no test double.

Each test names the failure it would catch and why that failure would otherwise be
invisible until the whole system is running.
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
    """The forward path, and the two flags that hang off it.

    A publish trigger firing on the wrong transition would dispatch an order that is not
    baking yet; a release flag on the wrong one would return a driver mid-delivery.
    Neither shows up anywhere but here until an end-to-end run.
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
    """The three illegal shapes, and what the error carries.

    A skip would make delivery without dispatch a supported path; a repeat that succeeded
    would publish ORDER_READY twice for one transition. The error names both statuses
    because an API that cannot name them turns a rule failure into an opaque conflict.
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
    """Both clauses of the assignment guard.

    Dropping "no driver yet" assigns a second driver to an order already on its way.
    Dropping "not delivered" lets a retrying event assign a driver after the only
    transition that could release them has passed, leaking that driver out of the pool
    permanently — which no interface reports.
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
    """Delivery does not erase a failed dispatch.

    FAILED is the only assignment state written deliberately, and the only one with no
    copy anywhere else. Overwriting it on delivery would erase the record that no driver
    was ever found, through a status update that has nothing to do with it.
    """
    order = _an_order()
    order.mark_dispatch_failed()
    assert order.assignment_state is AssignmentState.FAILED

    for step in _TO_DELIVERED:
        order.advance_to(step)

    assert order.status is OrderStatus.DELIVERED
    assert order.assignment_state is AssignmentState.FAILED


def test_giving_up_is_ignored_once_a_driver_is_assigned() -> None:
    """Giving up is ignored once a driver is on the way.

    Two messages per order are in flight, so one can exhaust its retry budget after the
    other has already assigned. Without the guard the exhausted message would mark an
    order FAILED while a driver is delivering it.
    """
    order = _an_order()
    driver_id = uuid4()
    order.assign_to(driver_id=driver_id, now=_NOW)

    order.mark_dispatch_failed()

    assert order.assignment_state is AssignmentState.ASSIGNED
    assert order.driver_id == driver_id
