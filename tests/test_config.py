"""Tests for application configuration behavior."""

from __future__ import annotations

import pytest

from app.config import AppConfig
from app.utils.exceptions import ConfigurationError


def test_config_defaults_when_env_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default configuration should load when env vars are absent."""
    for key in [
        "APP_NAME",
        "APP_ENV",
        "APP_DEBUG",
        "APP_LOG_LEVEL",
        "APP_MAX_UPLOAD_SIZE_MB",
        "APP_ALLOWED_UPLOAD_EXTENSIONS",
    ]:
        monkeypatch.delenv(key, raising=False)

    config = AppConfig.from_env()

    assert config.app_name == "AI Data Analytics Platform"
    assert config.app_env == "development"
    assert config.debug is False
    assert config.max_upload_size_mb == 25
    assert config.allowed_upload_extensions == (".csv", ".xlsx")


def test_config_reads_environment_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment values should be parsed into typed config fields."""
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_DEBUG", "true")
    monkeypatch.setenv("APP_LOG_LEVEL", "warning")
    monkeypatch.setenv("APP_MAX_UPLOAD_SIZE_MB", "15")
    monkeypatch.setenv("APP_ALLOWED_UPLOAD_EXTENSIONS", ".csv,.xlsx,.xls")

    config = AppConfig.from_env()

    assert config.app_name == "Test App"
    assert config.app_env == "test"
    assert config.debug is True
    assert config.log_level == "WARNING"
    assert config.max_upload_size_mb == 15
    assert config.allowed_upload_extensions == (".csv", ".xlsx", ".xls")


def test_config_rejects_invalid_max_upload_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid max upload size should raise configuration error."""
    monkeypatch.setenv("APP_MAX_UPLOAD_SIZE_MB", "0")

    with pytest.raises(ConfigurationError):
        AppConfig.from_env()
