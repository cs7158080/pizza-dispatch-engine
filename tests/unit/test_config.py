"""Unit tests for the configuration boundary.

Every test passes a literal mapping instead of touching `os.environ`, so no test can
affect another and repeated runs give the same result.
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
    """Scenario: a complete environment loads both settings objects.

    Why it matters: the environment holds only strings, so a number left unconverted
    would surface as a type error inside the broker adapter rather than here, and a
    surviving trailing slash would become a double slash in every URL built from it.
    The mappings also carry unprefixed variables, which the loader must ignore.
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
    """Scenario: a missing variable is reported by its environment name.

    Why it matters: the process must not start on a value nobody supplied, and the
    message must name `PIZZA_DATABASE_URL` rather than the field `database_url`,
    since the environment variable is what the reader can fix.
    """
    incomplete = {
        key: value for key, value in _SERVICE_ENV.items() if key != "PIZZA_DATABASE_URL"
    }

    with pytest.raises(ConfigurationError) as caught:
        load_service_settings(incomplete)

    assert "PIZZA_DATABASE_URL" in str(caught.value)


def test_unknown_prefixed_variable_is_rejected() -> None:
    """Scenario: an unknown prefixed variable is rejected rather than ignored.

    Why it matters: under Compose every variable is supplied, so a typo produces an
    extra variable rather than a missing one. Ignoring it would start the service on
    a default nobody chose, with no interface reporting a fault.
    """
    with pytest.raises(ConfigurationError) as caught:
        load_service_settings({**_SERVICE_ENV, "PIZZA_LOG_LEVL": "DEBUG"})

    assert "PIZZA_LOG_LEVL" in str(caught.value)


def test_out_of_range_values_are_rejected() -> None:
    """Scenario: values of the right type but outside the allowed range are rejected.

    Why it matters: a retry cap of zero would mark an order FAILED on the first
    rejection with no retry at all, and an unknown log level would be silently
    reinterpreted. Neither is reported anywhere, so the bounds are the only guard.
    """
    with pytest.raises(ConfigurationError):
        load_service_settings({**_SERVICE_ENV, "PIZZA_DISPATCH_MAX_RETRIES": "0"})

    with pytest.raises(ConfigurationError):
        load_service_settings({**_SERVICE_ENV, "PIZZA_LOG_LEVEL": "verbose"})
