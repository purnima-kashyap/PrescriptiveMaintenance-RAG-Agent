import streamlit as st

PAGES = [
    ("Dashboard", "🏠"),
    ("Maintenance Workspace", "🛠️"),
    ("Alert History", "🕐"),
    ("IoT Monitoring", "📡"),
    ("Manual Library", "📁"),
    ("Analytics", "📊"),
]


def render_sidebar():
    valid_pages = [name for name, _ in PAGES]

    # Restore page from URL on first load / refresh
    if "selected_page" not in st.session_state:
        query_page = st.query_params.get("page")
        st.session_state.selected_page = (
            query_page if query_page in valid_pages else "Dashboard"
        )
        st.query_params["page"] = st.session_state.selected_page

    with st.sidebar:
        st.markdown(
            '<div class="sidebar-logo">'
            '<span class="logo-icon-badge">⚙</span>'
            '<span class="logo-text-wrap">'
            '<span class="logo-line1">Smart Maintenance</span>'
            '<span class="logo-line2">Assistant</span>'
            '</span>'
            '</div>'
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        for name, icon in PAGES:
            is_active = st.session_state.selected_page == name
            if st.button(
                f"{icon}  {name}",
                key=f"nav_{name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.selected_page = name
                st.query_params["page"] = name
                st.rerun()

    return st.session_state.selected_page