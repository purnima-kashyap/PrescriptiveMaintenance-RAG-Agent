import streamlit as st
from components.style_loader import load_css
from api_client import get_alert_history


def render():
    load_css("alert_history.css")

    st.markdown(
        """
        <h1>🕒 Alert History</h1>
        <p class="page-subtitle">
        Historical IoT alerts received by the system.
        </p>
        """,
        unsafe_allow_html=True,
    )

    try:
        alerts = get_alert_history()
    except Exception as e:
        st.error(f"Could not load alert history: {e}")
        return

    if not alerts:
        st.info("No alerts available.")
        return

    total_alerts = len(alerts)
    max_temp = max(alert["temperature"] for alert in alerts)
    latest = alerts[0]

    st.markdown("### Factory Overview")

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        ("Total Alerts", total_alerts),
        ("Highest Temp", f"{max_temp:.1f} °C"),
        ("Latest Machine", latest["machine_id"]),
        ("Latest Error", latest["error_code"]),
    ]

    for col, (title, value) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-title">{title}</div>
                    <div class="summary-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    search = st.text_input(
        "Search Machine",
        placeholder="Enter Machine ID..."
    )

    if search:
        alerts = [
            alert
            for alert in alerts
            if search.lower() in alert["machine_id"].lower()
        ]

    st.divider()

    for alert in alerts:
        # NOTE: no blank lines inside this HTML block. Streamlit dedents the
        # string, and a blank line followed by an indented line makes Markdown
        # treat the rest as a code block, showing the HTML source instead.
        st.markdown(
            f"""
            <div class="alert-card">
                <div class="alert-header">
                    <span class="machine">{alert["machine_id"]}</span>
                    <span class="status-badge">Logged</span>
                </div>
                <div class="alert-grid">
                    <div>
                        <div class="label">Error Code</div>
                        <div class="value">{alert["error_code"]}</div>
                    </div>
                    <div>
                        <div class="label">Temperature</div>
                        <div class="temp-badge">
                            🌡 {alert["temperature"]:.1f} °C
                        </div>
                    </div>
                    <div>
                        <div class="label">Timestamp</div>
                        <div class="value">{alert["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )