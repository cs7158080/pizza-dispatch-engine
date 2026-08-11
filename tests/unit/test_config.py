"""The configuration boundary.

Every test passes a literal mapping instead of touching `os.environ`, so no
test can affect another and repeated runs give the same result.
"""

import pytest

from pizza.config import ConfigurationError, load_client_settings, load_service_settings

_SERVICE_ENV = {
    "PIZZA_DATABASE_URL": "postgresql+psycopg://user:secret@db:5432/app",
    "PIZZA_BROKER_URL": "amqp://user:secret@broker:5672/",
    "PIZZA_LOG_LEVEL": "INFO",
    "PIZZA_BROKER_PUBLISH_TIMEOUT_SECONDS": "5",
    "PIZZA_DISPATCH_RETRY_DELAY_SECONDS": "8",
    "PIZZA_DISPATCH_MAX_RETRIES": "8",
}


def test_complete_environment_loads() -> None:
    """A full environment yields both settings objects, with two conversions.

    The environment holds only strings, so a number that stayed a string would
    surface as a type error deep inside the broker adapter or the worker rather
    than here; and a trailing slash that survived would become a double slash in
    every URL the CLI and the test suite build. The mappings also carry
    variables outside the prefix, which the loader must ignore rather than
    reject.
    """
    service = load_service_settings({**_SERVICE_ENV, "PATH": "/usr/local/bin"})

    assert service.dispatch_max_retries == 8
    assert service.dispatch_retry_delay_seconds == 8
    assert service.broker_publish_timeout_seconds == 5.0
    assert service.log_level == "INFO"

    client = load_client_settings(
        {"PIZZA_API_BASE_URL": "http://api:8000/", "HOSTNAME": "abc"}
    )

    assert client.api_base_url == "http://api:8000"


def test_missing_variable_names_it() -> None:
    """A missing variable fails loudly, naming the variable and not the field.

    This is what configuration validation at startup means: the process must not
    start on a value nobody supplied. The message has to name
    `PIZZA_DATABASE_URL`, because that is what the reader can fix —
    `database_url` would send them to the source instead.
    """
    incomplete = {
        key: value for key, value in _SERVICE_ENV.items() if key != "PIZZA_DATABASE_URL"
    }

    with pytest.raises(ConfigurationError) as caught:
        load_service_settings(incomplete)

    assert "PIZZA_DATABASE_URL" in str(caught.value)


def test_unknown_prefixed_variable_is_rejected() -> None:
    """A mistyped variable is rejected rather than ignored.

    Under Compose every variable is supplied, so a typo produces an extra
    variable rather than a missing one. Ignoring it would start the service on a
    default nobody chose, and nothing anywhere would report a fault.
    """
    with pytest.raises(ConfigurationError) as caught:
        load_service_settings({**_SERVICE_ENV, "PIZZA_LOG_LEVL": "DEBUG"})

    assert "PIZZA_LOG_LEVL" in str(caught.value)


def test_out_of_range_values_are_rejected() -> None:
    """Values of the right type but outside the allowed range are still faults.

    A retry cap of zero would mark an order FAILED on the first rejection with
    no retry at all, and an unknown log level would be applied as something
    else. Neither is reported by any interface as a configuration fault, so the
    bounds are the only guard.
    """
    with pytest.raises(ConfigurationError):
        load_service_settings({**_SERVICE_ENV, "PIZZA_DISPATCH_MAX_RETRIES": "0"})

    with pytest.raises(ConfigurationError):
        load_service_settings({**_SERVICE_ENV, "PIZZA_LOG_LEVEL": "verbose"})
