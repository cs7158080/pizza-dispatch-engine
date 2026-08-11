"""The configuration boundary: environment strings turned into typed settings.

10.1 registers the variables; 10.2 fixes this module's shape and placement. No module
under domain/ or application/ imports it, and nothing here reads the environment at
import time — loading is a call, made once by a composition root.
"""

from collections.abc import Mapping
from typing import Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

_PREFIX = "PIZZA_"

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ConfigurationError(Exception):
    """The environment does not describe a usable configuration."""


class ServiceSettings(BaseModel):
    """Read by the api and the worker (10.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    database_url: str = Field(min_length=1)
    broker_url: str = Field(min_length=1)
    log_level: LogLevel
    broker_publish_timeout_seconds: float = Field(gt=0)
    dispatch_retry_delay_seconds: int = Field(gt=0)
    dispatch_max_retries: int = Field(ge=1)


class ClientSettings(BaseModel):
    """Read by the CLI and the integration suite (10.1)."""

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
    return _load(ServiceSettings, env)


def load_client_settings(env: Mapping[str, str]) -> ClientSettings:
    return _load(ClientSettings, env)
