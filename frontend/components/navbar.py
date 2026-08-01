import streamlit as st

def render_navbar():

    st.markdown("""
    <div class="navbar">

        <div class="logo">
        🤖 Prescriptive Maintenance AI
        </div>

        <div class="status">
        🟢 Online
        </div>

    </div>
    """, unsafe_allow_html=True)