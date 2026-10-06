"""Tests for dataset profiling service."""

from __future__ import annotations

import pandas as pd
import pytest

from app.services.data_profiler import DataProfilerService
from app.utils.exceptions import DataProcessingError


def test_profile_overview_and_quality_metrics() -> None:
    """Profiler should compute accurate overview and quality metrics."""
    dataframe = pd.DataFrame(
        {
            "category": ["A", "A", None],
            "value": [10, 10, 20],
            "constant": [1, 1, 1],
        }
    )

    profile = DataProfilerService().generate_profile(dataframe)

    assert profile.overview["rows"] == 3
    assert profile.overview["columns"] == 3
    assert profile.data_quality["total_missing_cells"] == 1
    assert profile.data_quality["duplicate_rows"] == 0
    assert "category" in profile.data_quality["columns_with_missing"]
    assert "constant" in profile.data_quality["constant_columns"]


def test_profile_detects_duplicates() -> None:
    """Duplicate row metrics should be correctly computed."""
    dataframe = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})

    profile = DataProfilerService().generate_profile(dataframe)

    assert profile.data_quality["duplicate_rows"] == 1
    assert profile.data_quality["duplicate_percentage"] == pytest.approx(33.33, abs=0.01)


def test_numeric_summary_contains_expected_columns() -> None:
    """Numeric summary should include required statistics."""
    dataframe = pd.DataFrame({"n": [1, 2, 3]})

    numeric = DataProfilerService().generate_profile(dataframe).numeric_summary

    assert list(numeric.columns) == ["Column", "Count", "Mean", "Median", "Std", "Min", "Max"]
    row = numeric.iloc[0]
    assert row["Column"] == "n"
    assert row["Count"] == 3
    assert row["Mean"] == pytest.approx(2.0)


def test_categorical_summary_contains_top_value() -> None:
    """Categorical summary should expose top value and frequency."""
    dataframe = pd.DataFrame({"city": ["NY", "SF", "NY", None]})

    categorical = DataProfilerService().generate_profile(dataframe).categorical_summary

    row = categorical.iloc[0]
    assert row["Column"] == "city"
    assert row["Unique Count"] == 2
    assert row["Top Value"] == "NY"
    assert row["Top Value Frequency"] == 2


def test_empty_dataframe_is_handled() -> None:
    """Empty dataframes should still produce structured profile outputs."""
    dataframe = pd.DataFrame(columns=["a", "b"])

    profile = DataProfilerService().generate_profile(dataframe)

    assert profile.overview["rows"] == 0
    assert profile.overview["columns"] == 2
    assert profile.numeric_summary.empty
    assert profile.categorical_summary.empty


def test_none_dataframe_raises_error() -> None:
    """None input should raise a domain processing error."""
    with pytest.raises(DataProcessingError):
        DataProfilerService().generate_profile(None)  # type: ignore[arg-type]
