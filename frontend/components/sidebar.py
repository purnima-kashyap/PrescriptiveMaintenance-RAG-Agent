import streamlit as st

def render_sidebar():

    with st.sidebar:

        st.markdown("""
        <div class="side-logo">
            🤖
            <h2>Maintenance AI</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Upload Manuals",
                "IoT Monitoring",
                "Knowledge Base",
                "Alert History",
                "Analytics"
            ]
        )

        st.markdown("---")

        st.markdown("""
        <div class="side-status">
        🟢 System Online<br>
        Vector DB: ChromaDB<br>
        Models: RAG + LLM
        </div>
        """, unsafe_allow_html=True)

    return page