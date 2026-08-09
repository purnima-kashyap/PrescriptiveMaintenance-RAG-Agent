import streamlit as st

from components.sidebar import render_sidebar
from components.style_loader import load_css
from pages import dashboard, alert_history, iot_monitoring, manual_library, analytics, maintenance_workspace

st.set_page_config(
    page_title="Smart Maintenance Assistant",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    load_css("base.css")
    load_css("sidebar.css")

    selected_page = render_sidebar()

    if selected_page == "Dashboard":
        dashboard.render()
    elif selected_page == "Maintenance Workspace":
        maintenance_workspace.render()
    elif selected_page == "Alert History":
        alert_history.render()
    elif selected_page == "IoT Monitoring":
        iot_monitoring.render()
    elif selected_page == "Manual Library":
        manual_library.render()
    elif selected_page == "Analytics":
        analytics.render()


if __name__ == "__main__":
    main()