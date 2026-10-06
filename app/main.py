"""Streamlit entry point for the AI Data Analytics Platform."""

from __future__ import annotations

import streamlit as st
from collections.abc import Callable

from app.config import get_config
from app.pages.data_profile import render_data_profiling_page
from app.utils.logger import get_logger, setup_logging


def render_overview() -> None:
    """Render project overview page content."""
    st.subheader("Platform Overview")
    st.write(
        "Phase 2 adds dataset upload and profiling capabilities while preserving "
        "the modular production foundation introduced in Phase 1."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Phase", "Phase 2")
    col2.metric("Status", "Upload + Profiling")
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
        "- Dataset upload and profiling services\n"
        "- Initial pytest test suite"
    )


def render_next_steps() -> None:
    """Render high-level roadmap without implementing later-phase features."""
    st.subheader("Planned Next Phases")
    st.info(
        "Upcoming phases will add cleaning workflows, richer EDA visualizations, "
        "and then AI/ML capabilities in sequence."
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
    st.caption("Portfolio Project | Phase 2")

    st.sidebar.header("Navigation")
    sections: dict[str, Callable[[], None]] = {
        "Overview": render_overview,
        "Data Profiling": lambda: render_data_profiling_page(config),
        "Foundation Status": render_foundation_status,
        "Roadmap": render_next_steps,
    }
    selected_section = st.sidebar.radio("Go to", list(sections.keys()))

    logger.info("Rendering section: %s", selected_section)
    sections[selected_section]()


if __name__ == "__main__":
    main()
