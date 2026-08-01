import streamlit as st
from components.style_loader import load_css


def render():
    load_css("alert_history.css")

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Alert History</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # api_client.get_alert_history()
   