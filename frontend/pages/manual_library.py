import streamlit as st
from components.style_loader import load_css


def render():
    load_css("manual_library.css")

    st.markdown('<div class="section-title">Manual Library</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
