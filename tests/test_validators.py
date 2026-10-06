"""Tests for reusable validation utilities."""

from __future__ import annotations

import pytest

from app.utils.exceptions import ConfigurationError, ValidationError
from app.utils.validators import (
    validate_file_size,
    validate_required_config_values,
    validate_uploaded_file_type,
)


def test_validate_uploaded_file_type_accepts_allowed_extension() -> None:
    """Allowed file extensions should pass validation."""
    extension = validate_uploaded_file_type("dataset.CSV", {".csv", ".xlsx"})
    assert extension == ".csv"


def test_validate_uploaded_file_type_rejects_disallowed_extension() -> None:
    """Disallowed extensions should raise validation errors."""
    with pytest.raises(ValidationError):
        validate_uploaded_file_type("dataset.txt", {".csv", ".xlsx"})


def test_validate_file_size_within_limit() -> None:
    """A file under the limit should validate successfully."""
    validate_file_size(file_size_bytes=1024, max_size_mb=1)


def test_validate_file_size_rejects_oversized_file() -> None:
    """An oversized file should raise validation error."""
    with pytest.raises(ValidationError):
        validate_file_size(file_size_bytes=3 * 1024 * 1024, max_size_mb=1)


def test_validate_required_config_values_rejects_missing_values() -> None:
    """Missing required config values should raise configuration error."""
    config = {"APP_NAME": "AI App", "OPENAI_API_KEY": ""}

    with pytest.raises(ConfigurationError):
        validate_required_config_values(config, ["APP_NAME", "OPENAI_API_KEY"])
