"""Reusable dataset profiling service for dataframe analytics summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from app.utils.exceptions import DataProcessingError


@dataclass(frozen=True)
class DatasetProfile:
    """Structured profile output for UI rendering."""

    overview: dict[str, Any]
    column_info: pd.DataFrame
    data_quality: dict[str, Any]
    numeric_summary: pd.DataFrame
    categorical_summary: pd.DataFrame


class DataProfilerService:
    """Service providing overview and statistics for uploaded datasets."""

    def generate_profile(self, dataframe: pd.DataFrame) -> DatasetProfile:
        """Generate full profiling summary for a dataset."""
        if dataframe is None:
            raise DataProcessingError("Cannot profile a missing dataset.")

        overview = self._dataset_overview(dataframe)
        column_info = self._column_information(dataframe)
        data_quality = self._data_quality(dataframe)
        numeric_summary = self._numeric_summary(dataframe)
        categorical_summary = self._categorical_summary(dataframe)

        return DatasetProfile(
            overview=overview,
            column_info=column_info,
            data_quality=data_quality,
            numeric_summary=numeric_summary,
            categorical_summary=categorical_summary,
        )

    def _dataset_overview(self, dataframe: pd.DataFrame) -> dict[str, Any]:
        """Compute dataset-level overview metrics."""
        memory_usage_bytes = int(dataframe.memory_usage(deep=True).sum())
        return {
            "rows": int(dataframe.shape[0]),
            "columns": int(dataframe.shape[1]),
            "memory_usage_bytes": memory_usage_bytes,
            "memory_usage_mb": round(memory_usage_bytes / (1024 * 1024), 3),
        }

    def _column_information(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Compute column-level structure and missing-value information."""
        rows = max(int(dataframe.shape[0]), 1)
        missing_counts = dataframe.isna().sum()

        column_info = pd.DataFrame(
            {
                "Column": dataframe.columns,
                "Data Type": [str(dtype) for dtype in dataframe.dtypes],
                "Non-Null Count": dataframe.notna().sum().values,
                "Missing Count": missing_counts.values,
                "Missing %": ((missing_counts / rows) * 100).round(2).values,
                "Unique Values": dataframe.nunique(dropna=True).values,
            }
        )

        return column_info

    def _data_quality(self, dataframe: pd.DataFrame) -> dict[str, Any]:
        """Compute quality diagnostics for missing, duplicate, and constant data."""
        total_rows = int(dataframe.shape[0])
        total_cells = int(dataframe.shape[0] * dataframe.shape[1])
        total_missing_cells = int(dataframe.isna().sum().sum())
        duplicate_rows = int(dataframe.duplicated().sum()) if total_rows else 0

        columns_with_missing = [
            str(column) for column in dataframe.columns[dataframe.isna().any()]
        ]

        constant_columns = [
            str(column)
            for column in dataframe.columns
            if dataframe[column].nunique(dropna=False) <= 1
        ]

        duplicate_percentage = (
            round((duplicate_rows / total_rows) * 100, 2) if total_rows else 0.0
        )

        return {
            "total_cells": total_cells,
            "total_missing_cells": total_missing_cells,
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": duplicate_percentage,
            "columns_with_missing": columns_with_missing,
            "constant_columns": constant_columns,
        }

    def _numeric_summary(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Generate numeric summary statistics for numeric columns."""
        numeric_df = dataframe.select_dtypes(include="number")
        if numeric_df.empty:
            return pd.DataFrame(
                columns=["Column", "Count", "Mean", "Median", "Std", "Min", "Max"]
            )

        summary = numeric_df.agg(["count", "mean", "median", "std", "min", "max"]).T
        summary = summary.reset_index().rename(
            columns={
                "index": "Column",
                "count": "Count",
                "mean": "Mean",
                "median": "Median",
                "std": "Std",
                "min": "Min",
                "max": "Max",
            }
        )
        return summary

    def _categorical_summary(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Generate categorical summary for non-numeric categorical columns."""
        categorical_df = dataframe.select_dtypes(include=["object", "category", "bool"])
        if categorical_df.empty:
            return pd.DataFrame(
                columns=["Column", "Unique Count", "Top Value", "Top Value Frequency"]
            )

        rows: list[dict[str, Any]] = []
        for column in categorical_df.columns:
            series = categorical_df[column]
            value_counts = series.value_counts(dropna=False)
            top_value = value_counts.index[0] if not value_counts.empty else None
            top_frequency = int(value_counts.iloc[0]) if not value_counts.empty else 0
            if pd.isna(top_value):
                top_value = "<MISSING>"

            rows.append(
                {
                    "Column": str(column),
                    "Unique Count": int(series.nunique(dropna=True)),
                    "Top Value": str(top_value),
                    "Top Value Frequency": top_frequency,
                }
            )

        return pd.DataFrame(rows)
