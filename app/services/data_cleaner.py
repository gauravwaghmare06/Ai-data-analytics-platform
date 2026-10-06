"""Reusable data cleaning and transformation service."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
from typing import Any

import pandas as pd

from app.utils.exceptions import DataProcessingError, ValidationError


@dataclass(frozen=True)
class CleaningOperation:
    """Metadata for a single cleaning operation."""

    operation_name: str
    columns: list[str]
    affected_rows: int
    affected_cells: int
    timestamp: str
    details: str

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation for UI/session history storage."""
        return asdict(self)


@dataclass(frozen=True)
class CleaningResult:
    """Result object containing transformed dataframe and operation metadata."""

    dataframe: pd.DataFrame
    operation: CleaningOperation


class DataCleanerService:
    """Service containing safe, reusable cleaning and transformation operations."""

    def handle_missing_values(
        self,
        dataframe: pd.DataFrame,
        *,
        strategy: str,
        column: str | None = None,
        custom_value: Any = None,
    ) -> CleaningResult:
        """Apply missing-value strategy and return transformed dataframe."""
        working_df = dataframe.copy()
        strategy_key = strategy.lower().strip()

        if strategy_key == "drop_rows":
            if column and column not in working_df.columns:
                raise ValidationError(f"Column '{column}' does not exist.")

            if column:
                mask = working_df[column].isna()
                affected_rows = int(mask.sum())
                result_df = working_df.loc[~mask].copy()
                details = f"Dropped rows with missing values in '{column}'."
                columns = [column]
            else:
                missing_by_row = working_df.isna().any(axis=1)
                affected_rows = int(missing_by_row.sum())
                result_df = working_df.dropna().copy()
                details = "Dropped rows containing missing values across all columns."
                columns = ["<all>"]

            return CleaningResult(
                dataframe=result_df,
                operation=self._operation(
                    "drop_missing_rows",
                    columns=columns,
                    affected_rows=affected_rows,
                    affected_cells=0,
                    details=details,
                ),
            )

        target_column = self._validated_column(working_df, column)
        missing_mask = working_df[target_column].isna()
        affected_cells = int(missing_mask.sum())

        if affected_cells == 0:
            return CleaningResult(
                dataframe=working_df,
                operation=self._operation(
                    "fill_missing_values",
                    columns=[target_column],
                    affected_rows=0,
                    affected_cells=0,
                    details=f"No missing values found in '{target_column}'.",
                ),
            )

        fill_value: Any
        details: str

        if strategy_key == "mean":
            if not pd.api.types.is_numeric_dtype(working_df[target_column]):
                raise ValidationError("Mean strategy is only valid for numeric columns.")
            fill_value = working_df[target_column].mean()
            if pd.isna(fill_value):
                raise ValidationError(
                    f"Column '{target_column}' contains only missing values; mean is unavailable."
                )
            details = f"Filled missing values in '{target_column}' using mean."
        elif strategy_key == "median":
            if not pd.api.types.is_numeric_dtype(working_df[target_column]):
                raise ValidationError("Median strategy is only valid for numeric columns.")
            fill_value = working_df[target_column].median()
            if pd.isna(fill_value):
                raise ValidationError(
                    f"Column '{target_column}' contains only missing values; median is unavailable."
                )
            details = f"Filled missing values in '{target_column}' using median."
        elif strategy_key == "mode":
            if pd.api.types.is_numeric_dtype(working_df[target_column]):
                raise ValidationError(
                    "Mode strategy is intended for categorical/non-numeric columns."
                )
            mode_series = working_df[target_column].mode(dropna=True)
            if mode_series.empty:
                raise ValidationError(
                    f"Column '{target_column}' contains only missing values; mode is unavailable."
                )
            fill_value = mode_series.iloc[0]
            details = f"Filled missing values in '{target_column}' using mode."
        elif strategy_key == "custom":
            fill_value = custom_value
            details = f"Filled missing values in '{target_column}' using custom value."
        else:
            raise ValidationError(f"Unsupported missing-value strategy '{strategy}'.")

        working_df[target_column] = working_df[target_column].fillna(fill_value)

        return CleaningResult(
            dataframe=working_df,
            operation=self._operation(
                "fill_missing_values",
                columns=[target_column],
                affected_rows=affected_cells,
                affected_cells=affected_cells,
                details=details,
            ),
        )

    def detect_duplicates(self, dataframe: pd.DataFrame) -> int:
        """Return duplicate row count."""
        return int(dataframe.duplicated().sum())

    def remove_duplicates(self, dataframe: pd.DataFrame) -> CleaningResult:
        """Remove duplicate rows and return transformed dataframe with metadata."""
        duplicate_count = self.detect_duplicates(dataframe)
        cleaned_df = dataframe.drop_duplicates().copy()
        return CleaningResult(
            dataframe=cleaned_df,
            operation=self._operation(
                "remove_duplicates",
                columns=["<all>"],
                affected_rows=duplicate_count,
                affected_cells=0,
                details="Removed duplicate rows.",
            ),
        )

    def rename_column(
        self, dataframe: pd.DataFrame, old_name: str, new_name: str
    ) -> CleaningResult:
        """Rename a column safely."""
        self._validated_column(dataframe, old_name)
        if not new_name.strip():
            raise ValidationError("New column name cannot be empty.")
        if new_name != old_name and new_name in dataframe.columns:
            raise ValidationError(f"Column '{new_name}' already exists.")

        cleaned_df = dataframe.rename(columns={old_name: new_name}).copy()
        return CleaningResult(
            dataframe=cleaned_df,
            operation=self._operation(
                "rename_column",
                columns=[old_name, new_name],
                affected_rows=0,
                affected_cells=0,
                details=f"Renamed column '{old_name}' to '{new_name}'.",
            ),
        )

    def drop_columns(self, dataframe: pd.DataFrame, columns: list[str]) -> CleaningResult:
        """Drop selected columns after validation."""
        if not columns:
            raise ValidationError("Select at least one column to remove.")

        missing = [col for col in columns if col not in dataframe.columns]
        if missing:
            raise ValidationError(f"Columns not found: {', '.join(missing)}")

        cleaned_df = dataframe.drop(columns=columns).copy()
        return CleaningResult(
            dataframe=cleaned_df,
            operation=self._operation(
                "drop_columns",
                columns=columns,
                affected_rows=0,
                affected_cells=0,
                details=f"Removed {len(columns)} column(s).",
            ),
        )

    def normalize_column_names(self, dataframe: pd.DataFrame) -> CleaningResult:
        """Normalize column names using lowercase snake_case rules."""
        cleaned_df = dataframe.copy()
        used_names: set[str] = set()
        name_mapping: dict[str, str] = {}

        for original in cleaned_df.columns:
            normalized = self._normalize_column_name(str(original))
            if normalized in used_names:
                counter = 2
                candidate = f"{normalized}_{counter}"
                while candidate in used_names:
                    counter += 1
                    candidate = f"{normalized}_{counter}"
                normalized = candidate
            used_names.add(normalized)
            name_mapping[str(original)] = normalized

        cleaned_df = cleaned_df.rename(columns=name_mapping)
        changed_count = sum(1 for key, value in name_mapping.items() if key != value)

        return CleaningResult(
            dataframe=cleaned_df,
            operation=self._operation(
                "normalize_column_names",
                columns=list(name_mapping.keys()),
                affected_rows=0,
                affected_cells=0,
                details=f"Normalized column names ({changed_count} changed).",
            ),
        )

    def convert_column_type(
        self, dataframe: pd.DataFrame, column: str, target_type: str
    ) -> CleaningResult:
        """Convert a column to a target type and report conversion failures."""
        target_column = self._validated_column(dataframe, column)
        converted_df = dataframe.copy()
        source_series = converted_df[target_column]
        non_null_before = int(source_series.notna().sum())

        normalized_type = target_type.lower().strip()
        if normalized_type == "numeric":
            converted_series = pd.to_numeric(source_series, errors="coerce")
        elif normalized_type == "datetime":
            converted_series = pd.to_datetime(source_series, errors="coerce")
        elif normalized_type == "string":
            converted_series = source_series.astype("string")
        elif normalized_type == "boolean":
            converted_series = self._to_boolean_series(source_series)
        else:
            raise ValidationError(f"Unsupported target type '{target_type}'.")

        non_null_after = int(converted_series.notna().sum())
        failed_conversions = max(non_null_before - non_null_after, 0)

        converted_df[target_column] = converted_series
        details = (
            f"Converted '{target_column}' to {normalized_type}. "
            f"Failed conversions: {failed_conversions}."
        )

        return CleaningResult(
            dataframe=converted_df,
            operation=self._operation(
                "convert_column_type",
                columns=[target_column],
                affected_rows=failed_conversions,
                affected_cells=failed_conversions,
                details=details,
            ),
        )

    def calculate_iqr_bounds(self, dataframe: pd.DataFrame, column: str) -> dict[str, float]:
        """Calculate IQR statistics and outlier bounds for a numeric column."""
        target_column = self._validated_column(dataframe, column)
        if not pd.api.types.is_numeric_dtype(dataframe[target_column]):
            raise ValidationError("IQR outlier detection requires a numeric column.")

        numeric_series = pd.to_numeric(dataframe[target_column], errors="coerce").dropna()
        if numeric_series.empty:
            raise ValidationError(
                f"Column '{target_column}' has no numeric values for IQR analysis."
            )

        q1 = float(numeric_series.quantile(0.25))
        q3 = float(numeric_series.quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_mask = (numeric_series < lower_bound) | (numeric_series > upper_bound)
        outlier_count = int(outlier_mask.sum())

        return {
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": outlier_count,
        }

    def get_outlier_mask(self, dataframe: pd.DataFrame, column: str) -> pd.Series:
        """Return boolean mask indicating outlier rows for a numeric column."""
        stats = self.calculate_iqr_bounds(dataframe, column)
        numeric_series = pd.to_numeric(dataframe[column], errors="coerce")
        return (numeric_series < stats["lower_bound"]) | (numeric_series > stats["upper_bound"])

    def remove_outliers(self, dataframe: pd.DataFrame, column: str) -> CleaningResult:
        """Remove rows identified as outliers by IQR bounds for selected column."""
        outlier_mask = self.get_outlier_mask(dataframe, column)
        removed_rows = int(outlier_mask.sum())
        cleaned_df = dataframe.loc[~outlier_mask].copy()

        return CleaningResult(
            dataframe=cleaned_df,
            operation=self._operation(
                "remove_outliers",
                columns=[column],
                affected_rows=removed_rows,
                affected_cells=0,
                details=f"Removed outlier rows based on '{column}' IQR bounds.",
            ),
        )

    def preview_filter_impact(
        self, dataframe: pd.DataFrame, column: str, operator: str, value: str
    ) -> tuple[int, int]:
        """Preview row retention/removal counts for a filter without applying it."""
        mask = self._build_filter_mask(dataframe, column, operator, value)
        kept_rows = int(mask.sum())
        removed_rows = int((~mask).sum())
        return kept_rows, removed_rows

    def apply_filter(
        self, dataframe: pd.DataFrame, column: str, operator: str, value: str
    ) -> CleaningResult:
        """Apply validated row filter using safe vectorized operations."""
        mask = self._build_filter_mask(dataframe, column, operator, value)
        cleaned_df = dataframe.loc[mask].copy()
        removed_rows = int((~mask).sum())

        return CleaningResult(
            dataframe=cleaned_df,
            operation=self._operation(
                "apply_filter",
                columns=[column],
                affected_rows=removed_rows,
                affected_cells=0,
                details=f"Applied filter: {column} {operator} {value}",
            ),
        )

    def _build_filter_mask(
        self, dataframe: pd.DataFrame, column: str, operator: str, value: str
    ) -> pd.Series:
        """Build boolean mask for supported filter operators."""
        target_column = self._validated_column(dataframe, column)
        op = operator.strip().lower()
        series = dataframe[target_column]

        if op in {"equals", "not equals", "greater than", "less than", "greater than or equal", "less than or equal"}:
            if pd.api.types.is_numeric_dtype(series):
                parsed_value = self._parse_numeric(value)
                compare_series = pd.to_numeric(series, errors="coerce")
            elif pd.api.types.is_datetime64_any_dtype(series):
                parsed_value = pd.to_datetime(value, errors="coerce")
                if pd.isna(parsed_value):
                    raise ValidationError("Invalid datetime filter value.")
                compare_series = pd.to_datetime(series, errors="coerce")
            else:
                parsed_value = value
                compare_series = series.astype("string")

            if op == "equals":
                return compare_series == parsed_value
            if op == "not equals":
                return compare_series != parsed_value
            if op == "greater than":
                return compare_series > parsed_value
            if op == "less than":
                return compare_series < parsed_value
            if op == "greater than or equal":
                return compare_series >= parsed_value
            return compare_series <= parsed_value

        if op == "contains":
            return series.astype("string").str.contains(value, case=False, na=False)

        raise ValidationError(f"Unsupported filter operator '{operator}'.")

    def _validated_column(self, dataframe: pd.DataFrame, column: str | None) -> str:
        """Validate that a column exists and return the normalized name."""
        if not column:
            raise ValidationError("Please select a column.")
        if column not in dataframe.columns:
            raise ValidationError(f"Column '{column}' does not exist.")
        return column

    def _operation(
        self,
        name: str,
        *,
        columns: list[str],
        affected_rows: int,
        affected_cells: int,
        details: str,
    ) -> CleaningOperation:
        """Build a standardized cleaning operation record."""
        return CleaningOperation(
            operation_name=name,
            columns=columns,
            affected_rows=affected_rows,
            affected_cells=affected_cells,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=details,
        )

    def _normalize_column_name(self, value: str) -> str:
        """Normalize a single column name into predictable snake_case."""
        normalized = value.strip().lower()
        normalized = re.sub(r"[^0-9a-zA-Z]+", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized).strip("_")
        return normalized or "column"

    def _parse_numeric(self, value: str) -> float:
        """Parse numeric input for numeric filter operations."""
        try:
            return float(value)
        except ValueError as exc:
            raise ValidationError("Invalid numeric filter value.") from exc

    def _to_boolean_series(self, series: pd.Series) -> pd.Series:
        """Convert series values to nullable boolean with safe coercion."""
        truthy = {"true", "1", "yes", "y", "on"}
        falsy = {"false", "0", "no", "n", "off"}

        def convert(value: Any) -> Any:
            if pd.isna(value):
                return pd.NA
            if isinstance(value, bool):
                return value
            normalized = str(value).strip().lower()
            if normalized in truthy:
                return True
            if normalized in falsy:
                return False
            return pd.NA

        converted = series.map(convert)
        try:
            return converted.astype("boolean")
        except Exception as exc:  # pragma: no cover - defensive fallback
            raise DataProcessingError("Failed to convert column to boolean type.") from exc
