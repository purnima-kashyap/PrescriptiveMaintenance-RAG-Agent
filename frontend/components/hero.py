import streamlit as st

def render_hero():

    st.markdown("""
    <div class="hero">

        <div>

        <h1>
        🤖 Prescriptive Maintenance RAG Agent
        </h1>

        <p>
        AI-powered predictive maintenance using RAG
        </p>

        </div>

        <div class="hero-status">

        <h2>🟢 ONLINE</h2>

        <p>All systems operational</p>

        </div>

    </div>
    """, unsafe_allow_html=True)