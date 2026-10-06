"""Tests for custom exception hierarchy."""

from app.utils.exceptions import (
    AppError,
    ConfigurationError,
    DataProcessingError,
    ValidationError,
)


def test_custom_exceptions_inherit_from_app_error() -> None:
    """Domain exceptions should inherit from AppError for consistent handling."""
    assert issubclass(ConfigurationError, AppError)
    assert issubclass(DataProcessingError, AppError)
    assert issubclass(ValidationError, AppError)


def test_exception_messages_are_preserved() -> None:
    """Exception messages should be available for user-facing/reporting flows."""
    message = "Validation failed"
    error = ValidationError(message)

    assert str(error) == message
