"""Streamlit entry point for the AI Data Analytics Platform."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from app.config import get_config
from app.pages.data_cleaning import render_data_cleaning_page
from app.pages.data_profile import render_data_profiling_page
from app.utils.logger import get_logger, setup_logging


def render_overview() -> None:
    """Render project overview page content."""
    st.subheader("Platform Overview")
    st.write(
        "Phase 3 introduces dataset cleaning and transformation workflows while "
        "preserving separation between UI and reusable data services."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Phase", "Phase 3")
    col2.metric("Status", "Profiling + Cleaning")
    col3.metric("App Layer", "Streamlit")


def render_foundation_status() -> None:
    """Render implemented foundation capabilities."""
    st.subheader("Implemented Foundation")
    st.markdown(
        "- Modular project structure\n"
        "- Environment-based configuration\n"
        "- Centralized logging utilities\n"
        "- Custom exception hierarchy\n"
        "- Reusable validators\n"
        "- Dataset upload/profiling services\n"
        "- Dataset cleaning/transformation service\n"
        "- Initial and expanded pytest coverage"
    )


def render_next_steps() -> None:
    """Render high-level roadmap without implementing later-phase features."""
    st.subheader("Planned Next Phases")
    st.info(
        "Upcoming phases will focus on richer EDA visualizations, then AI/ML "
        "capabilities in sequence."
    )


def main() -> None:
    """Run Streamlit app with modular navigation and page rendering."""
    config = get_config()
    setup_logging(config.log_level)
    logger = get_logger(__name__)

    st.set_page_config(
        page_title=config.app_name,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title(config.app_name)
    st.caption("Portfolio Project | Phase 3")

    st.sidebar.header("Navigation")
    sections: dict[str, Callable[[], None]] = {
        "Overview": render_overview,
        "Data Profiling": lambda: render_data_profiling_page(config),
        "Data Cleaning": lambda: render_data_cleaning_page(config),
        "Foundation Status": render_foundation_status,
        "Roadmap": render_next_steps,
    }
    selected_section = st.sidebar.radio("Go to", list(sections.keys()))

    logger.info("Rendering section: %s", selected_section)
    sections[selected_section]()


if __name__ == "__main__":
    main()
