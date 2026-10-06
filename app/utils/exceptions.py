"""Custom exception hierarchy for application-level error handling."""


class AppError(Exception):
    """Base exception for all application-specific errors."""


class ConfigurationError(AppError):
    """Raised when configuration values are missing or invalid."""


class DataProcessingError(AppError):
    """Raised when data processing operations fail."""


class ValidationError(AppError):
    """Raised when user input or files fail validation rules."""
