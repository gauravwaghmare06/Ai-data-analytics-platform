"""Session-state helpers for managing the active dataset in Streamlit."""

from __future__ import annotations

import pandas as pd
import streamlit as st

_DATAFRAME_KEY = "current_dataset"
_FILENAME_KEY = "current_dataset_filename"
_FILE_SIGNATURE_KEY = "current_dataset_signature"


def initialize_dataset_state() -> None:
    """Ensure required dataset state keys are initialized."""
    st.session_state.setdefault(_DATAFRAME_KEY, None)
    st.session_state.setdefault(_FILENAME_KEY, None)
    st.session_state.setdefault(_FILE_SIGNATURE_KEY, None)


def set_dataset(dataframe: pd.DataFrame, filename: str, signature: str) -> None:
    """Store dataset and metadata in session state."""
    st.session_state[_DATAFRAME_KEY] = dataframe
    st.session_state[_FILENAME_KEY] = filename
    st.session_state[_FILE_SIGNATURE_KEY] = signature


def clear_dataset() -> None:
    """Clear active dataset from session state."""
    st.session_state[_DATAFRAME_KEY] = None
    st.session_state[_FILENAME_KEY] = None
    st.session_state[_FILE_SIGNATURE_KEY] = None


def get_dataset() -> pd.DataFrame | None:
    """Return active dataset, if available."""
    return st.session_state.get(_DATAFRAME_KEY)


def get_dataset_filename() -> str | None:
    """Return active dataset filename, if available."""
    return st.session_state.get(_FILENAME_KEY)


def get_dataset_signature() -> str | None:
    """Return active dataset file signature, if available."""
    return st.session_state.get(_FILE_SIGNATURE_KEY)
