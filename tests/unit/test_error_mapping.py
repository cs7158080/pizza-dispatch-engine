"""The one gap in the error mapping that no request can be written against."""

import inspect

from pizza.domain import errors as domain_errors
from pizza.entrypoints.api.errors import _STATUS


def test_every_domain_error_has_a_status() -> None:
    """Every error the domain defines is mapped to a status code.

    A domain error added later without a row in the table does not fail: it falls
    through to the handler for `Exception` and answers `500` with a body that says
    nothing, on a request the rules refused deliberately. A `500` is a defect here
    rather than a contract, and omitting a row is the one way the system could
    produce one without anyone writing a bug.

    No HTTP scenario can cover this, because the error it is about does not exist
    yet — which is what makes the assertion belong here rather than in the suite.
    """
    defined = {
        member
        for _, member in inspect.getmembers(domain_errors, inspect.isclass)
        if issubclass(member, Exception) and member.__module__ == domain_errors.__name__
    }

    assert defined <= set(_STATUS)
