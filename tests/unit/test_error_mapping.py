"""Unit test for the completeness of the API's domain-error mapping."""

import inspect

from pizza.domain import errors as domain_errors
from pizza.entrypoints.api.errors import _STATUS


def test_every_domain_error_has_a_status() -> None:
    """Scenario: every error defined in the domain has a row in the status table.

    Why it matters: an unmapped domain error falls through to the handler for
    `Exception` and answers 500 with an empty body, on a request the rules refused
    deliberately. No HTTP scenario can cover this, because the error it guards
    against has not been written yet.
    """
    defined = {
        member
        for _, member in inspect.getmembers(domain_errors, inspect.isclass)
        if issubclass(member, Exception) and member.__module__ == domain_errors.__name__
    }

    assert defined <= set(_STATUS)
