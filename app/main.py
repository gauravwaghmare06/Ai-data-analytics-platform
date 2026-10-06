"""Streamlit entry point for the AI Data Analytics Platform."""

from __future__ import annotations

import streamlit as st

from app.config import get_config
from app.utils.logger import get_logger, setup_logging


def render_overview() -> None:
    """Render project overview page content."""
    st.subheader("Platform Overview")
    st.write(
        "This Phase 1 release establishes the production foundation for the AI "
        "Data Analytics Platform with configuration, validation, logging, and test-ready "
        "project structure."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Phase", "Phase 1")
    col2.metric("Status", "Foundation Ready")
    col3.metric("App Layer", "Streamlit")


def render_foundation_status() -> None:
    """Render implemented foundation capabilities."""
    st.subheader("Implemented in Phase 1")
    st.markdown(
        "- Modular project structure\n"
        "- Environment-based configuration\n"
        "- Centralized logging utilities\n"
        "- Custom exception hierarchy\n"
        "- Reusable input/config validators\n"
        "- Initial pytest test suite"
    )


def render_next_steps() -> None:
    """Render high-level roadmap without implementing later-phase features."""
    st.subheader("Planned Next Phases")
    st.info(
        "Phase 2+ will introduce ingestion workflows, profiling, cleaning, EDA, "
        "visualization, insights, and ML modules incrementally."
    )


def main() -> None:
    """Run Streamlit app with foundation-ready navigation shell."""
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
    st.caption("Production Foundation | AI Data Analytics Platform")

    st.sidebar.header("Navigation")
    sections = {
        "Overview": render_overview,
        "Foundation Status": render_foundation_status,
        "Roadmap": render_next_steps,
    }
    selected_section = st.sidebar.radio("Go to", list(sections.keys()))

    logger.info("Rendering section: %s", selected_section)
    sections[selected_section]()


if __name__ == "__main__":
    main()
