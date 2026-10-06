"""Centralized application configuration for the AI Data Analytics Platform."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

from app.utils.exceptions import ConfigurationError


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """Typed application configuration loaded from environment variables."""

    app_name: str = "AI Data Analytics Platform"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    max_upload_size_mb: int = 25
    allowed_upload_extensions: tuple[str, ...] = (".csv", ".xlsx")

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Build application configuration from environment variables."""
        raw_extensions = os.getenv("APP_ALLOWED_UPLOAD_EXTENSIONS", ".csv,.xlsx")
        allowed_extensions = tuple(
            ext.strip().lower() for ext in raw_extensions.split(",") if ext.strip()
        )

        config = cls(
            app_name=os.getenv("APP_NAME", cls.app_name),
            app_env=os.getenv("APP_ENV", cls.app_env),
            debug=_to_bool(os.getenv("APP_DEBUG", str(cls.debug))),
            log_level=os.getenv("APP_LOG_LEVEL", cls.log_level).upper(),
            max_upload_size_mb=_to_int(
                os.getenv("APP_MAX_UPLOAD_SIZE_MB", str(cls.max_upload_size_mb)),
                "APP_MAX_UPLOAD_SIZE_MB",
            ),
            allowed_upload_extensions=allowed_extensions
            or cls.allowed_upload_extensions,
        )
        _validate_config(config)
        return config


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Return cached application configuration."""
    return AppConfig.from_env()


def _to_bool(value: str) -> bool:
    """Parse a boolean-like string into a bool value."""
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str, variable_name: str) -> int:
    """Parse an integer environment variable value."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(
            f"Environment variable '{variable_name}' must be an integer."
        ) from exc


def _validate_config(config: AppConfig) -> None:
    """Validate loaded configuration values and raise on invalid values."""
    if config.max_upload_size_mb <= 0:
        raise ConfigurationError("APP_MAX_UPLOAD_SIZE_MB must be greater than zero.")

    if not config.allowed_upload_extensions:
        raise ConfigurationError("At least one upload file extension must be configured.")

    for extension in config.allowed_upload_extensions:
        if not extension.startswith("."):
            raise ConfigurationError(
                "All APP_ALLOWED_UPLOAD_EXTENSIONS values must start with '.'."
            )
