"""Streamlit page for dataset upload and profiling."""

from __future__ import annotations

import streamlit as st

from app.config import AppConfig
from app.services.data_loader import DataLoaderService
from app.services.data_profiler import DataProfilerService
from app.services.dataset_state import (
    clear_dataset,
    get_dataset,
    get_dataset_filename,
    get_dataset_signature,
    initialize_dataset_state,
    set_dataset,
)
from app.utils.exceptions import AppError
from app.utils.logger import get_logger


def render_data_profiling_page(config: AppConfig) -> None:
    """Render dataset upload and profiling UI."""
    logger = get_logger(__name__)
    initialize_dataset_state()

    st.subheader("Data Profiling")
    st.caption("Upload a CSV or XLSX dataset to view profile and quality diagnostics.")

    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=[ext.replace(".", "") for ext in config.allowed_upload_extensions],
        help=(
            "Supported formats: "
            f"{', '.join(config.allowed_upload_extensions)} | "
            f"Max size: {config.max_upload_size_mb} MB"
        ),
    )

    if uploaded_file is None:
        clear_dataset()
        st.info("Upload a dataset file to begin profiling.")
        return

    current_signature = f"{uploaded_file.name}:{uploaded_file.size}"
    if current_signature != get_dataset_signature() or get_dataset() is None:
        loader = DataLoaderService()
        try:
            loaded = loader.load_uploaded_file(
                uploaded_file,
                allowed_extensions=config.allowed_upload_extensions,
                max_size_mb=config.max_upload_size_mb,
            )
            set_dataset(loaded.dataframe, loaded.filename, current_signature)
            st.success(f"Loaded dataset: {loaded.filename}")
        except AppError as exc:
            logger.warning("Dataset upload failed: %s", exc)
            clear_dataset()
            st.error(str(exc))
            return

    dataframe = get_dataset()
    if dataframe is None:
        st.error("Unable to access dataset in session state.")
        return

    profiler = DataProfilerService()
    profile = profiler.generate_profile(dataframe)

    filename = get_dataset_filename() or "uploaded dataset"
    st.markdown(f"### Dataset Summary — `{filename}`")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", profile.overview["rows"])
    col2.metric("Columns", profile.overview["columns"])
    col3.metric("Missing Values", profile.data_quality["total_missing_cells"])
    col4.metric("Duplicate Rows", profile.data_quality["duplicate_rows"])

    st.markdown("### Preview")
    st.dataframe(dataframe.head(10), use_container_width=True)

    st.markdown("### Column Information")
    st.dataframe(
        profile.column_info[
            [
                "Column",
                "Data Type",
                "Non-Null Count",
                "Missing Count",
                "Missing %",
            ]
        ],
        use_container_width=True,
    )

    st.markdown("### Data Quality")
    if profile.data_quality["columns_with_missing"]:
        st.warning(
            "Columns with missing values: "
            + ", ".join(profile.data_quality["columns_with_missing"])
        )
    else:
        st.success("No missing values detected.")

    if profile.data_quality["duplicate_rows"] > 0:
        st.warning(
            f"Duplicate rows: {profile.data_quality['duplicate_rows']} "
            f"({profile.data_quality['duplicate_percentage']}%)"
        )
    else:
        st.success("No duplicate rows detected.")

    if profile.data_quality["constant_columns"]:
        st.warning(
            "Constant columns detected: "
            + ", ".join(profile.data_quality["constant_columns"])
        )
    else:
        st.success("No constant columns detected.")

    st.markdown("### Numeric Statistical Summary")
    if profile.numeric_summary.empty:
        st.info("No numeric columns found.")
    else:
        st.dataframe(profile.numeric_summary, use_container_width=True)

    st.markdown("### Categorical Summary")
    if profile.categorical_summary.empty:
        st.info("No categorical columns found.")
    else:
        st.dataframe(profile.categorical_summary, use_container_width=True)
