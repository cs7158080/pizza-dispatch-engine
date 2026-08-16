"""Configuration boundary: environment strings validated into typed settings.

Nothing here reads the environment at import time. Loading is an explicit call made
once by a composition root, so importing this module cannot fail on a missing
variable.
"""

from collections.abc import Mapping
from typing import Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

_PREFIX = "PIZZA_"

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ConfigurationError(Exception):
    """The environment does not describe a usable configuration."""


class ServiceSettings(BaseModel):
    """Settings required by the api and the worker."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    database_url: str = Field(min_length=1)
    broker_url: str = Field(min_length=1)
    log_level: LogLevel
    broker_publish_timeout_seconds: float = Field(gt=0)
    dispatch_retry_delay_seconds: int = Field(gt=0)
    dispatch_max_retries: int = Field(ge=1)


class ClientSettings(BaseModel):
    """Settings required by the CLI and the integration suite."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    api_base_url: str

    @field_validator("api_base_url")
    @classmethod
    def _without_trailing_slash(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("must start with http:// or https://")
        return value.rstrip("/")


_Settings = TypeVar("_Settings", bound=BaseModel)


def _load(model: type[_Settings], env: Mapping[str, str]) -> _Settings:
    declared = {
        key.removeprefix(_PREFIX).lower(): value
        for key, value in env.items()
        if key.startswith(_PREFIX)
    }
    try:
        return model.model_validate(declared)
    except ValidationError as error:
        raise ConfigurationError(_describe(error)) from error


def _describe(error: ValidationError) -> str:
    faults = [
        f"{_PREFIX}{'_'.join(str(part) for part in item['loc']).upper()}: {item['msg']}"
        for item in error.errors()
    ]
    return "invalid configuration:\n" + "\n".join(faults)


def load_service_settings(env: Mapping[str, str]) -> ServiceSettings:
    """Read the service settings from the environment.

    Raises:
        ConfigurationError: A variable is missing or does not validate.
    """
    return _load(ServiceSettings, env)


def load_client_settings(env: Mapping[str, str]) -> ClientSettings:
    """Read the client settings from the environment.

    Raises:
        ConfigurationError: A variable is missing or does not validate.
    """
    return _load(ClientSettings, env)
