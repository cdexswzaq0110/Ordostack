from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping
from urllib.parse import urlparse


VALID_ENVIRONMENTS = {"local", "test", "production"}
VALID_DATA_STORES = {"memory", "mysql"}
DEFAULT_SCHEDULER_SERVICE_URL = "http://scheduler-service:8100"
DEFAULT_ML_SERVICE_URL = "http://ml-service:8200"
DEFAULT_LOCAL_AUTH_TOKEN_SECRET = "ordostack-local-dev-auth-token-secret"


class ConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeConfig:
    ordostack_env: str
    data_store: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    scheduler_service_url: str
    ml_service_url: str
    auth_token_secret: str


def load_runtime_config(environment: Mapping[str, str] | None = None) -> RuntimeConfig:
    values = os.environ if environment is None else environment
    ordostack_env = get_value(values, "ORDOSTACK_ENV", "local").lower()
    data_store = get_value(values, "DATA_STORE", "memory").lower()
    scheduler_service_url = get_value(values, "SCHEDULER_SERVICE_URL", DEFAULT_SCHEDULER_SERVICE_URL)
    ml_service_url = get_value(values, "ML_SERVICE_URL", DEFAULT_ML_SERVICE_URL)

    if ordostack_env not in VALID_ENVIRONMENTS:
        raise ConfigurationError("ORDOSTACK_ENV must be one of: local, test, production")
    if data_store not in VALID_DATA_STORES:
        raise ConfigurationError("DATA_STORE must be one of: memory, mysql")

    config = RuntimeConfig(
        ordostack_env=ordostack_env,
        data_store=data_store,
        db_host=get_value(values, "DB_HOST", "mysql"),
        db_port=parse_port(get_value(values, "DB_PORT", "3306"), "DB_PORT"),
        db_name=get_value(values, "DB_NAME", "ordostack"),
        db_user=get_value(values, "DB_USER", "root"),
        db_password=get_value(values, "DB_PASSWORD", ""),
        scheduler_service_url=normalize_url(scheduler_service_url, "SCHEDULER_SERVICE_URL"),
        ml_service_url=normalize_url(ml_service_url, "ML_SERVICE_URL"),
        auth_token_secret=get_non_empty_value(values, "AUTH_TOKEN_SECRET", DEFAULT_LOCAL_AUTH_TOKEN_SECRET),
    )
    validate_runtime_config(config=config, explicit_values=values)
    return config


def validate_runtime_config(config: RuntimeConfig, explicit_values: Mapping[str, str]) -> None:
    if config.data_store == "mysql":
        require_non_empty(config.db_host, "DB_HOST")
        require_non_empty(config.db_name, "DB_NAME")
        require_non_empty(config.db_user, "DB_USER")

    if config.ordostack_env == "production":
        require_explicit(explicit_values, "DATA_STORE")
        require_explicit(explicit_values, "SCHEDULER_SERVICE_URL")
        require_explicit(explicit_values, "ML_SERVICE_URL")
        require_explicit(explicit_values, "AUTH_TOKEN_SECRET")
        if config.data_store == "mysql":
            require_non_empty(config.db_password, "DB_PASSWORD")


def get_value(values: Mapping[str, str], key: str, default: str) -> str:
    value = values.get(key, default)
    return value.strip() if isinstance(value, str) else str(value)


def get_non_empty_value(values: Mapping[str, str], key: str, default: str) -> str:
    value = get_value(values, key, default)
    return default if value == "" else value


def require_explicit(values: Mapping[str, str], key: str) -> None:
    if key not in values or get_value(values, key, "") == "":
        raise ConfigurationError(f"{key} must be set when ORDOSTACK_ENV=production")


def require_non_empty(value: str, key: str) -> None:
    if value == "":
        raise ConfigurationError(f"{key} must not be empty")


def parse_port(value: str, key: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise ConfigurationError(f"{key} must be an integer") from error

    if port < 1 or port > 65535:
        raise ConfigurationError(f"{key} must be between 1 and 65535")
    return port


def normalize_url(value: str, key: str) -> str:
    parsed_url = urlparse(value)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ConfigurationError(f"{key} must be an http or https URL")
    return value.rstrip("/")
