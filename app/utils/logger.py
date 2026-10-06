"""Reusable logging setup for consistent application logging."""

from __future__ import annotations

import logging

_LOGGING_CONFIGURED = False


def setup_logging(level: str = "INFO") -> None:
    """Configure root logging once with a consistent formatter."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    resolved_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance using the shared application logging configuration."""
    if not _LOGGING_CONFIGURED:
        setup_logging()
    return logging.getLogger(name)
