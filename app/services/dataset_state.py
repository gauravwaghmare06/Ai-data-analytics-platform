"""Session-state helpers for managing original/current datasets and history."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

import pandas as pd
import streamlit as st

_ORIGINAL_DATAFRAME_KEY = "original_dataset"
_CURRENT_DATAFRAME_KEY = "current_dataset"
_FILENAME_KEY = "current_dataset_filename"
_FILE_SIGNATURE_KEY = "current_dataset_signature"
_CLEANING_HISTORY_KEY = "cleaning_history"


def initialize_dataset_state(state: MutableMapping[str, Any] | None = None) -> None:
    """Ensure required dataset state keys are initialized."""
    target = _resolve_state(state)
    target.setdefault(_ORIGINAL_DATAFRAME_KEY, None)
    target.setdefault(_CURRENT_DATAFRAME_KEY, None)
    target.setdefault(_FILENAME_KEY, None)
    target.setdefault(_FILE_SIGNATURE_KEY, None)
    target.setdefault(_CLEANING_HISTORY_KEY, [])


def set_dataset(
    dataframe: pd.DataFrame,
    filename: str,
    signature: str,
    state: MutableMapping[str, Any] | None = None,
) -> None:
    """Store uploaded dataset as both original and current state."""
    target = _resolve_state(state)
    target[_ORIGINAL_DATAFRAME_KEY] = dataframe.copy()
    target[_CURRENT_DATAFRAME_KEY] = dataframe.copy()
    target[_FILENAME_KEY] = filename
    target[_FILE_SIGNATURE_KEY] = signature
    target[_CLEANING_HISTORY_KEY] = []


def update_current_dataset(
    dataframe: pd.DataFrame, state: MutableMapping[str, Any] | None = None
) -> None:
    """Update the current cleaned dataset without modifying original dataset."""
    target = _resolve_state(state)
    target[_CURRENT_DATAFRAME_KEY] = dataframe.copy()


def add_cleaning_history(
    operation_record: dict[str, Any], state: MutableMapping[str, Any] | None = None
) -> None:
    """Append a cleaning operation record to history."""
    target = _resolve_state(state)
    history = target.setdefault(_CLEANING_HISTORY_KEY, [])
    history.append(operation_record)


def get_cleaning_history(
    state: MutableMapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return cleaning operation history."""
    target = _resolve_state(state)
    return list(target.get(_CLEANING_HISTORY_KEY, []))


def reset_to_original(state: MutableMapping[str, Any] | None = None) -> bool:
    """Reset current dataset to original dataset, preserving original data."""
    target = _resolve_state(state)
    original = target.get(_ORIGINAL_DATAFRAME_KEY)
    if original is None:
        return False
    target[_CURRENT_DATAFRAME_KEY] = original.copy()
    target[_CLEANING_HISTORY_KEY] = []
    return True


def clear_dataset(state: MutableMapping[str, Any] | None = None) -> None:
    """Clear active dataset and history from session state."""
    target = _resolve_state(state)
    target[_ORIGINAL_DATAFRAME_KEY] = None
    target[_CURRENT_DATAFRAME_KEY] = None
    target[_FILENAME_KEY] = None
    target[_FILE_SIGNATURE_KEY] = None
    target[_CLEANING_HISTORY_KEY] = []


def get_dataset(state: MutableMapping[str, Any] | None = None) -> pd.DataFrame | None:
    """Return current dataset, if available."""
    target = _resolve_state(state)
    return target.get(_CURRENT_DATAFRAME_KEY)


def get_original_dataset(
    state: MutableMapping[str, Any] | None = None,
) -> pd.DataFrame | None:
    """Return original dataset, if available."""
    target = _resolve_state(state)
    return target.get(_ORIGINAL_DATAFRAME_KEY)


def get_dataset_filename(state: MutableMapping[str, Any] | None = None) -> str | None:
    """Return active dataset filename, if available."""
    target = _resolve_state(state)
    return target.get(_FILENAME_KEY)


def get_dataset_signature(state: MutableMapping[str, Any] | None = None) -> str | None:
    """Return active dataset file signature, if available."""
    target = _resolve_state(state)
    return target.get(_FILE_SIGNATURE_KEY)


def _resolve_state(state: MutableMapping[str, Any] | None) -> MutableMapping[str, Any]:
    """Resolve state mapping for production or tests."""
    if state is not None:
        return state
    return st.session_state
