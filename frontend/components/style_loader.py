"""
Small utility to load and inject a CSS file into the Streamlit app.

CSS files are explicitly read as UTF-8 so the app works correctly on
Windows as well as Linux/macOS.
"""

import streamlit as st
from pathlib import Path


STYLES_DIR = Path(__file__).parent.parent / "styles"


def load_css(filename: str):
    """
    Load a CSS file from the styles/ folder and inject it into Streamlit.
    """

    css_path = STYLES_DIR / filename

    try:

        # IMPORTANT:
        # Explicit UTF-8 prevents Windows cp1252 UnicodeDecodeError
        with open(
            css_path,
            "r",
            encoding="utf-8"
        ) as f:

            css = f.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

    except FileNotFoundError:

        st.warning(
            f"Missing stylesheet: {filename}"
        )

    except UnicodeDecodeError:

        st.error(
            f"Could not read CSS file '{filename}'. "
            "Please save the CSS file as UTF-8."
        )