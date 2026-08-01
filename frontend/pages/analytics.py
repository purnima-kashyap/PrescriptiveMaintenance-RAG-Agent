import streamlit as st
from components.style_loader import load_css


def render():
    load_css("analytics.css")

    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)