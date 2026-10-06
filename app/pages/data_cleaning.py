"""Streamlit page for dataset cleaning and transformation operations."""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from app.config import AppConfig
from app.services.data_cleaner import DataCleanerService
from app.services.data_loader import DataLoaderService
from app.services.dataset_state import (
    add_cleaning_history,
    get_cleaning_history,
    get_dataset,
    get_dataset_filename,
    get_dataset_signature,
    get_original_dataset,
    initialize_dataset_state,
    reset_to_original,
    set_dataset,
    update_current_dataset,
)
from app.utils.exceptions import AppError, ValidationError
from app.utils.logger import get_logger

_FILTER_OPERATORS = [
    "equals",
    "not equals",
    "greater than",
    "less than",
    "greater than or equal",
    "less than or equal",
    "contains",
]



def render_data_cleaning_page(config: AppConfig) -> None:
    """Render dataset cleaning workflow UI for current session dataset."""
    logger = get_logger(__name__)
    initialize_dataset_state()

    st.subheader("Data Cleaning")
    st.caption("Apply validated cleaning operations to a working copy of your dataset.")

    _ensure_dataset_loaded(config, logger)
    current_df = get_dataset()
    original_df = get_original_dataset()

    if current_df is None or original_df is None:
        st.info("Upload a dataset to start cleaning.")
        return

    cleaner = DataCleanerService()
    _render_dataset_status(original_df, current_df)

    _render_missing_values_section(cleaner, current_df)
    _render_duplicates_section(cleaner, current_df)
    _render_column_management_section(cleaner, current_df)
    _render_data_type_section(cleaner, current_df)
    _render_outlier_section(cleaner, current_df)
    _render_filter_section(cleaner, current_df)
    _render_history_section()
    _render_reset_section()
    _render_export_section(current_df)


def _ensure_dataset_loaded(config: AppConfig, logger: object) -> None:
    """Load or refresh dataset in session state from uploader input."""
    uploaded_file = st.file_uploader(
        "Upload or replace dataset",
        type=[ext.replace(".", "") for ext in config.allowed_upload_extensions],
        help=(
            "Supported formats: "
            f"{', '.join(config.allowed_upload_extensions)} | "
            f"Max size: {config.max_upload_size_mb} MB"
        ),
        key="cleaning_uploader",
    )

    if uploaded_file is None:
        return

    signature = f"{uploaded_file.name}:{uploaded_file.size}"
    if signature == get_dataset_signature() and get_dataset() is not None:
        return

    try:
        loaded = DataLoaderService().load_uploaded_file(
            uploaded_file,
            allowed_extensions=config.allowed_upload_extensions,
            max_size_mb=config.max_upload_size_mb,
        )
        set_dataset(loaded.dataframe, loaded.filename, signature)
        st.success(f"Loaded dataset: {loaded.filename}")
    except AppError as exc:
        logger.warning("Cleaning dataset upload failed: %s", exc)
        st.error(str(exc))


def _render_dataset_status(original_df: pd.DataFrame, current_df: pd.DataFrame) -> None:
    """Render high-level dataset status metrics."""
    st.markdown("### Dataset Status")
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    original_rows, original_cols = original_df.shape
    current_rows, current_cols = current_df.shape

    col1.metric("Original Rows", original_rows)
    col2.metric("Original Columns", original_cols)
    col3.metric("Current Rows", current_rows)
    col4.metric("Current Columns", current_cols)
    col5.metric("Rows Removed", max(original_rows - current_rows, 0))
    col6.metric("Columns Removed", max(original_cols - current_cols, 0))


def _render_missing_values_section(cleaner: DataCleanerService, current_df: pd.DataFrame) -> None:
    """Render missing-value handling controls."""
    st.markdown("### Missing Values")
    missing_columns = [col for col in current_df.columns if current_df[col].isna().any()]

    if not missing_columns:
        st.success("No missing values detected in current dataset.")
        return

    st.write("Columns with missing values:", ", ".join(map(str, missing_columns)))

    strategy = st.selectbox(
        "Strategy",
        ["drop_rows", "mean", "median", "mode", "custom"],
        key="missing_strategy",
    )

    column_choices = ["<all>"] + [str(col) for col in missing_columns]
    selected_column = st.selectbox("Column", column_choices, key="missing_column")

    custom_value: str | None = None
    if strategy == "custom":
        custom_value = st.text_input("Custom value", key="missing_custom_value")

    if strategy in {"mean", "median", "mode", "custom"} and selected_column == "<all>":
        st.info("Select a specific column for this strategy.")

    if st.button("Apply Missing-Value Operation"):
        try:
            before_shape = current_df.shape
            target_col = None if selected_column == "<all>" else selected_column
            result = cleaner.handle_missing_values(
                current_df,
                strategy=strategy,
                column=target_col,
                custom_value=custom_value,
            )
            _commit_cleaning_result(result, before_shape)
        except AppError as exc:
            st.error(str(exc))


def _render_duplicates_section(cleaner: DataCleanerService, current_df: pd.DataFrame) -> None:
    """Render duplicate detection/removal controls."""
    st.markdown("### Duplicate Rows")
    duplicate_count = cleaner.detect_duplicates(current_df)
    st.write(f"Detected duplicate rows: {duplicate_count}")

    if st.button("Remove Duplicates", disabled=duplicate_count == 0):
        before_shape = current_df.shape
        result = cleaner.remove_duplicates(current_df)
        _commit_cleaning_result(result, before_shape)


def _render_column_management_section(
    cleaner: DataCleanerService, current_df: pd.DataFrame
) -> None:
    """Render column drop/rename/normalization controls."""
    st.markdown("### Column Management")

    removable_columns = st.multiselect(
        "Select columns to remove",
        [str(col) for col in current_df.columns],
        key="columns_to_remove",
    )
    if removable_columns:
        st.info(f"Columns to remove: {len(removable_columns)}")

    if st.button("Remove Selected Columns"):
        try:
            before_shape = current_df.shape
            result = cleaner.drop_columns(current_df, removable_columns)
            _commit_cleaning_result(result, before_shape)
        except AppError as exc:
            st.error(str(exc))

    rename_col1, rename_col2 = st.columns(2)
    with rename_col1:
        source_column = st.selectbox(
            "Column to rename",
            [str(col) for col in current_df.columns],
            key="rename_source",
        )
    with rename_col2:
        target_name = st.text_input("New name", key="rename_target")

    if st.button("Rename Column"):
        try:
            before_shape = current_df.shape
            result = cleaner.rename_column(current_df, source_column, target_name)
            _commit_cleaning_result(result, before_shape)
        except AppError as exc:
            st.error(str(exc))

    if st.button("Normalize Column Names"):
        before_shape = current_df.shape
        result = cleaner.normalize_column_names(current_df)
        _commit_cleaning_result(result, before_shape)


def _render_data_type_section(cleaner: DataCleanerService, current_df: pd.DataFrame) -> None:
    """Render type-conversion controls."""
    st.markdown("### Data Types")
    dtype_table = pd.DataFrame(
        {
            "Column": list(current_df.columns),
            "Current Type": [str(dtype) for dtype in current_df.dtypes],
        }
    )
    st.dataframe(dtype_table, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        column = st.selectbox(
            "Column to convert",
            [str(col) for col in current_df.columns],
            key="convert_column",
        )
    with col2:
        target_type = st.selectbox(
            "Target type",
            ["numeric", "string", "datetime", "boolean"],
            key="convert_target_type",
        )

    if st.button("Apply Type Conversion"):
        try:
            before_shape = current_df.shape
            result = cleaner.convert_column_type(current_df, column, target_type)
            _commit_cleaning_result(result, before_shape)
        except AppError as exc:
            st.error(str(exc))


def _render_outlier_section(cleaner: DataCleanerService, current_df: pd.DataFrame) -> None:
    """Render outlier inspection/removal controls using IQR."""
    st.markdown("### Outlier Detection (IQR)")
    numeric_columns = [
        str(col)
        for col in current_df.select_dtypes(include="number").columns.tolist()
    ]

    if not numeric_columns:
        st.info("No numeric columns available for outlier analysis.")
        return

    selected_column = st.selectbox("Numeric column", numeric_columns, key="outlier_column")

    try:
        stats = cleaner.calculate_iqr_bounds(current_df, selected_column)
    except ValidationError as exc:
        st.error(str(exc))
        return

    st.write(
        {
            "Q1": round(stats["q1"], 4),
            "Q3": round(stats["q3"], 4),
            "IQR": round(stats["iqr"], 4),
            "Lower Bound": round(stats["lower_bound"], 4),
            "Upper Bound": round(stats["upper_bound"], 4),
            "Outlier Count": stats["outlier_count"],
        }
    )

    remove_outliers = st.checkbox(
        "Remove detected outlier rows",
        key="remove_outliers_checkbox",
    )
    if remove_outliers and st.button("Apply Outlier Removal"):
        before_shape = current_df.shape
        result = cleaner.remove_outliers(current_df, selected_column)
        _commit_cleaning_result(result, before_shape)


def _render_filter_section(cleaner: DataCleanerService, current_df: pd.DataFrame) -> None:
    """Render safe row filtering controls."""
    st.markdown("### Row Filtering")

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_column = st.selectbox(
            "Column",
            [str(col) for col in current_df.columns],
            key="filter_column",
        )
    with col2:
        operator = st.selectbox("Operator", _FILTER_OPERATORS, key="filter_operator")
    with col3:
        filter_value = st.text_input("Value", key="filter_value")

    if filter_value:
        try:
            kept, removed = cleaner.preview_filter_impact(
                current_df, filter_column, operator, filter_value
            )
            st.info(f"Preview: {kept} rows kept, {removed} rows removed.")
        except AppError as exc:
            st.error(str(exc))

    if st.button("Apply Filter"):
        try:
            before_shape = current_df.shape
            result = cleaner.apply_filter(current_df, filter_column, operator, filter_value)
            _commit_cleaning_result(result, before_shape)
        except AppError as exc:
            st.error(str(exc))


def _render_history_section() -> None:
    """Render applied cleaning operation history."""
    st.markdown("### Cleaning History")
    history = get_cleaning_history()
    if not history:
        st.info("No cleaning operations applied yet.")
        return
    history_df = pd.DataFrame(history)
    st.dataframe(history_df, use_container_width=True)


def _render_reset_section() -> None:
    """Render reset-to-original controls with explicit confirmation."""
    st.markdown("### Reset")
    confirm_reset = st.checkbox(
        "I confirm I want to reset the cleaned dataset to the original upload.",
        key="confirm_reset",
    )
    if st.button("Reset to Original Dataset", disabled=not confirm_reset):
        if reset_to_original():
            st.success("Current cleaned dataset was reset to original dataset.")
        else:
            st.warning("No original dataset available to reset.")


def _render_export_section(current_df: pd.DataFrame) -> None:
    """Render cleaned dataset export actions (CSV / Excel)."""
    st.markdown("### Export Cleaned Dataset")
    filename = (get_dataset_filename() or "cleaned_dataset").rsplit(".", 1)[0]

    csv_data = current_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv_data,
        file_name=f"{filename}_cleaned.csv",
        mime="text/csv",
    )

    excel_buffer = BytesIO()
    current_df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)
    st.download_button(
        "Download Excel",
        data=excel_buffer.getvalue(),
        file_name=f"{filename}_cleaned.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def _commit_cleaning_result(result: object, before_shape: tuple[int, int]) -> None:
    """Persist cleaning result and show before/after summary."""
    if not hasattr(result, "dataframe") or not hasattr(result, "operation"):
        raise ValidationError("Invalid cleaning result payload.")

    cleaned_df = result.dataframe
    operation = result.operation
    update_current_dataset(cleaned_df)
    add_cleaning_history(operation.to_dict())

    after_shape = cleaned_df.shape
    st.success(
        f"{operation.details} | Rows: {before_shape[0]} → {after_shape[0]} | "
        f"Columns: {before_shape[1]} → {after_shape[1]}"
    )
