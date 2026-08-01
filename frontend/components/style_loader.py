"""
Small utility to load and inject a CSS file into the Streamlit app.
Every page calls load_css() with its own stylesheet path, keeping each
page's styling isolated in its own file.
"""
import streamlit as st
from pathlib import Path

STYLES_DIR = Path(__file__).parent.parent / "styles"


def load_css(filename: str):
    """Load a CSS file from the styles/ folder and inject it into the page."""
    css_path = STYLES_DIR / filename
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Missing stylesheet: {filename}")