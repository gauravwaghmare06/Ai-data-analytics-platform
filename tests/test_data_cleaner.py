"""Tests for data cleaning and transformation services."""

from __future__ import annotations

import pandas as pd
import pytest

from app.services.data_cleaner import DataCleanerService
from app.services.dataset_state import (
    get_cleaning_history,
    get_dataset,
    get_original_dataset,
    initialize_dataset_state,
    reset_to_original,
    set_dataset,
    update_current_dataset,
)
from app.utils.exceptions import ValidationError


@pytest.fixture
def cleaner() -> DataCleanerService:
    """Return cleaner service instance for tests."""
    return DataCleanerService()


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Return a reusable synthetic dataframe for cleaning tests."""
    return pd.DataFrame(
        {
            "Age": [20, None, 30, 1000, 20],
            "City": ["NY", "NY", None, "SF", "NY"],
            "Score": [1, 1, 2, 3, 1],
            "Customer Name": ["Alice", "Alice", "Bob", "Carol", "Alice"],
        }
    )


def test_missing_mean(cleaner: DataCleanerService, sample_df: pd.DataFrame) -> None:
    """Numeric missing values should fill with mean."""
    result = cleaner.handle_missing_values(sample_df, strategy="mean", column="Age")
    assert result.dataframe["Age"].isna().sum() == 0
    assert result.operation.affected_cells == 1


def test_missing_median(cleaner: DataCleanerService, sample_df: pd.DataFrame) -> None:
    """Numeric missing values should fill with median."""
    result = cleaner.handle_missing_values(sample_df, strategy="median", column="Age")
    assert result.dataframe["Age"].isna().sum() == 0


def test_missing_mode(cleaner: DataCleanerService, sample_df: pd.DataFrame) -> None:
    """Categorical missing values should fill with mode."""
    result = cleaner.handle_missing_values(sample_df, strategy="mode", column="City")
    assert result.dataframe["City"].isna().sum() == 0
    assert result.dataframe.loc[2, "City"] == "NY"


def test_missing_custom(cleaner: DataCleanerService, sample_df: pd.DataFrame) -> None:
    """Missing values should fill using custom value."""
    result = cleaner.handle_missing_values(
        sample_df,
        strategy="custom",
        column="City",
        custom_value="Unknown",
    )
    assert "Unknown" in result.dataframe["City"].values


def test_missing_drop_rows(cleaner: DataCleanerService, sample_df: pd.DataFrame) -> None:
    """Rows with missing values should be removed."""
    result = cleaner.handle_missing_values(sample_df, strategy="drop_rows", column="City")
    assert len(result.dataframe) == len(sample_df) - 1


def test_all_missing_column_edge_case(cleaner: DataCleanerService) -> None:
    """All-missing column should raise meaningful strategy errors."""
    dataframe = pd.DataFrame({"metric": [None, None, None]})
    with pytest.raises(ValidationError):
        cleaner.handle_missing_values(dataframe, strategy="mean", column="metric")


def test_duplicate_detection_and_removal(
    cleaner: DataCleanerService, sample_df: pd.DataFrame
) -> None:
    """Duplicate detection and removal should be accurate."""
    assert cleaner.detect_duplicates(sample_df) == 1
    result = cleaner.remove_duplicates(sample_df)
    assert len(result.dataframe) == len(sample_df) - 1


def test_column_rename_drop_and_normalize(
    cleaner: DataCleanerService, sample_df: pd.DataFrame
) -> None:
    """Column operations should rename, drop, and normalize safely."""
    renamed = cleaner.rename_column(sample_df, "City", "city_name").dataframe
    assert "city_name" in renamed.columns

    dropped = cleaner.drop_columns(renamed, ["Score"]).dataframe
    assert "Score" not in dropped.columns

    normalized = cleaner.normalize_column_names(sample_df).dataframe
    assert "customer_name" in normalized.columns


def test_numeric_and_datetime_conversion(cleaner: DataCleanerService) -> None:
    """Data type conversion should support numeric and datetime targets."""
    dataframe = pd.DataFrame({"amount": ["1", "2", "bad"], "date": ["2024-01-01", "bad", "2024-01-03"]})

    numeric = cleaner.convert_column_type(dataframe, "amount", "numeric")
    assert pd.api.types.is_numeric_dtype(numeric.dataframe["amount"])
    assert numeric.dataframe["amount"].isna().sum() == 1

    date_conv = cleaner.convert_column_type(dataframe, "date", "datetime")
    assert pd.api.types.is_datetime64_any_dtype(date_conv.dataframe["date"])
    assert date_conv.dataframe["date"].isna().sum() == 1


def test_invalid_conversion_type(cleaner: DataCleanerService, sample_df: pd.DataFrame) -> None:
    """Unsupported conversion types should raise validation errors."""
    with pytest.raises(ValidationError):
        cleaner.convert_column_type(sample_df, "Age", "uuid")


def test_iqr_detection_and_outlier_removal(cleaner: DataCleanerService) -> None:
    """IQR stats should detect and remove outlier rows."""
    dataframe = pd.DataFrame({"value": [10, 11, 12, 13, 999]})
    stats = cleaner.calculate_iqr_bounds(dataframe, "value")
    assert stats["outlier_count"] == 1

    result = cleaner.remove_outliers(dataframe, "value")
    assert len(result.dataframe) == 4


def test_filtering_numeric_and_contains(cleaner: DataCleanerService) -> None:
    """Filtering should support numeric comparisons and text contains."""
    dataframe = pd.DataFrame(
        {
            "amount": [10, 20, 30],
            "city": ["New York", "San Francisco", "Yorktown"],
        }
    )

    gt_filtered = cleaner.apply_filter(dataframe, "amount", "greater than", "15")
    assert len(gt_filtered.dataframe) == 2

    contains_filtered = cleaner.apply_filter(dataframe, "city", "contains", "york")
    assert len(contains_filtered.dataframe) == 2


def test_filtering_invalid_column_and_operator(cleaner: DataCleanerService) -> None:
    """Invalid filtering inputs should raise validation errors."""
    dataframe = pd.DataFrame({"a": [1, 2]})

    with pytest.raises(ValidationError):
        cleaner.apply_filter(dataframe, "missing", "equals", "1")

    with pytest.raises(ValidationError):
        cleaner.apply_filter(dataframe, "a", "between", "1")


def test_original_dataset_unchanged_and_reset_functionality() -> None:
    """Dataset state should preserve original data and support reset behavior."""
    state: dict[str, object] = {}
    initialize_dataset_state(state)

    original = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
    set_dataset(original, "demo.csv", "demo:3", state)

    mutated = get_dataset(state).copy()  # type: ignore[union-attr]
    mutated = mutated.drop(columns=["y"])  # type: ignore[assignment]
    update_current_dataset(mutated, state)

    assert list(get_original_dataset(state).columns) == ["x", "y"]  # type: ignore[union-attr]
    assert list(get_dataset(state).columns) == ["x"]  # type: ignore[union-attr]

    reset_ok = reset_to_original(state)
    assert reset_ok is True
    assert list(get_dataset(state).columns) == ["x", "y"]  # type: ignore[union-attr]
    assert get_cleaning_history(state) == []
