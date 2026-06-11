import pytest

from app.config import ConfigurationError, load_runtime_config


def test_default_runtime_config_is_local_memory() -> None:
    config = load_runtime_config({})

    assert config.ordostack_env == "local"
    assert config.data_store == "memory"
    assert config.scheduler_service_url == "http://scheduler-service:8100"
    assert config.ml_service_url == "http://ml-service:8200"
    assert config.auth_token_secret
    assert config.auth_token_ttl_minutes == 10080
    assert config.auth_login_max_failures == 5
    assert config.auth_password_min_length == 12


def test_blank_local_auth_token_secret_uses_fallback() -> None:
    config = load_runtime_config({"AUTH_TOKEN_SECRET": ""})

    assert config.auth_token_secret


def test_mysql_runtime_config_accepts_local_empty_password() -> None:
    config = load_runtime_config(
        {
            "ORDOSTACK_ENV": "local",
            "DATA_STORE": "mysql",
            "DB_HOST": "mysql",
            "DB_PORT": "3306",
            "DB_NAME": "ordostack",
            "DB_USER": "root",
            "DB_PASSWORD": "",
        },
    )

    assert config.data_store == "mysql"
    assert config.db_port == 3306
    assert config.db_password == ""


def test_invalid_environment_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="ORDOSTACK_ENV"):
        load_runtime_config({"ORDOSTACK_ENV": "staging"})


def test_invalid_data_store_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="DATA_STORE"):
        load_runtime_config({"DATA_STORE": "sqlite"})


def test_invalid_port_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="DB_PORT"):
        load_runtime_config({"DB_PORT": "not-a-port"})


def test_invalid_service_url_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="ML_SERVICE_URL"):
        load_runtime_config({"ML_SERVICE_URL": "ml-service:8200"})


def test_invalid_auth_numeric_setting_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="AUTH_TOKEN_TTL_MINUTES"):
        load_runtime_config({"AUTH_TOKEN_TTL_MINUTES": "0"})


def test_production_requires_explicit_service_urls() -> None:
    with pytest.raises(ConfigurationError, match="SCHEDULER_SERVICE_URL"):
        load_runtime_config(
            {
                "ORDOSTACK_ENV": "production",
                "DATA_STORE": "memory",
            },
        )


def test_production_mysql_requires_password() -> None:
    with pytest.raises(ConfigurationError, match="DB_PASSWORD"):
        load_runtime_config(
            {
                "ORDOSTACK_ENV": "production",
                "DATA_STORE": "mysql",
                "DB_HOST": "mysql",
                "DB_PORT": "3306",
                "DB_NAME": "ordostack",
                "DB_USER": "root",
                "DB_PASSWORD": "",
                "SCHEDULER_SERVICE_URL": "http://scheduler-service:8100",
                "ML_SERVICE_URL": "http://ml-service:8200",
                "AUTH_TOKEN_SECRET": "production-secret-value-with-32-chars",
            },
        )


def test_production_requires_auth_token_secret() -> None:
    with pytest.raises(ConfigurationError, match="AUTH_TOKEN_SECRET"):
        load_runtime_config(
            {
                "ORDOSTACK_ENV": "production",
                "DATA_STORE": "memory",
                "SCHEDULER_SERVICE_URL": "http://scheduler-service:8100",
                "ML_SERVICE_URL": "http://ml-service:8200",
            },
        )


def test_production_rejects_short_auth_token_secret() -> None:
    with pytest.raises(ConfigurationError, match="AUTH_TOKEN_SECRET"):
        load_runtime_config(
            {
                "ORDOSTACK_ENV": "production",
                "DATA_STORE": "memory",
                "SCHEDULER_SERVICE_URL": "http://scheduler-service:8100",
                "ML_SERVICE_URL": "http://ml-service:8200",
                "AUTH_TOKEN_SECRET": "short-secret",
            },
        )
