"""Reusable validation helpers for file and configuration checks."""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping

from app.utils.exceptions import ConfigurationError, ValidationError


def validate_uploaded_file_type(
    filename: str, allowed_extensions: Iterable[str]
) -> str:
    """Validate uploaded filename extension and return the normalized extension."""
    if not filename:
        raise ValidationError("A filename is required for upload validation.")

    extension = os.path.splitext(filename)[1].lower()
    normalized_allowed = {item.lower() for item in allowed_extensions}

    if extension not in normalized_allowed:
        allowed_display = ", ".join(sorted(normalized_allowed))
        raise ValidationError(
            f"Unsupported file type '{extension}'. Allowed types: {allowed_display}."
        )

    return extension


def validate_file_size(file_size_bytes: int, max_size_mb: int) -> None:
    """Validate that uploaded file size is within the configured limit."""
    if file_size_bytes < 0:
        raise ValidationError("File size cannot be negative.")

    if max_size_mb <= 0:
        raise ValidationError("Maximum file size must be greater than zero.")

    max_bytes = max_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise ValidationError(
            f"File size exceeds {max_size_mb} MB upload limit."
        )


def validate_required_config_values(
    config_values: Mapping[str, object], required_keys: Iterable[str]
) -> None:
    """Validate that required configuration keys exist and are non-empty."""
    missing_keys = []
    for key in required_keys:
        value = config_values.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing_keys.append(key)

    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ConfigurationError(f"Missing required configuration values: {missing}.")
