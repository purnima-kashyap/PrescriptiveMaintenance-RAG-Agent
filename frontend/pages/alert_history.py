import streamlit as st
from components.style_loader import load_css
from api_client import get_alert_history

# Temperature thresholds used to colour the severity badge.
TEMP_CRITICAL = 90.0
TEMP_WARNING = 75.0


def _severity(temperature: float):
    """Map a temperature to a (badge class, label) pair."""
    if temperature >= TEMP_CRITICAL:
        return "badge-red", "Critical"
    if temperature >= TEMP_WARNING:
        return "badge-amber", "Warning"
    return "badge-green", "Normal"


def _kpi(label: str, value, key: str, tone: str = ""):
    """One KPI tile. The keyed container is what alert_history.css targets."""
    with st.container(border=True, key=f"kpi_card_{key}"):
        st.markdown(
            f"""
            <div class="kpi-label">{label}</div>
            <div class="kpi-value {tone}">{value}</div>
            """,
            unsafe_allow_html=True,
        )


def render():
    load_css("alert_history.css")

    st.markdown(
        '<div class="alert-page-title">🕒 Alert History</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-subtitle">Historical IoT alerts received by the system.</div>',
        unsafe_allow_html=True,
    )

    try:
        alerts = get_alert_history()
    except Exception as e:
        st.error(f"Could not load alert history: {e}")
        return

    if not alerts:
        with st.container(border=True):
            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-state-icon">🕒</div>
                    <div>No alerts recorded yet.</div>
                    <div style="font-size:0.8rem; margin-top:0.3rem;">
                        Alerts will appear here as machines report telemetry.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        return

    # ---------------- Factory Overview ----------------
    total_alerts = len(alerts)
    max_temp = max(alert["temperature"] for alert in alerts)
    critical_count = sum(1 for a in alerts if a["temperature"] >= TEMP_CRITICAL)
    latest = alerts[0]

    with st.container(border=True):
        st.markdown(
            '<div class="section-title">Factory Overview</div>',
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            _kpi("Total Alerts", total_alerts, "total")
        with c2:
            _kpi(
                "Highest Temp",
                f"{max_temp:.1f} °C",
                "temp",
                "is-red" if max_temp >= TEMP_CRITICAL else "is-amber",
            )
        with c3:
            _kpi("Critical", critical_count, "critical", "is-red" if critical_count else "")
        with c4:
            _kpi("Latest Machine", latest["machine_id"], "machine", "is-blue")

    # ---------------- Alert Log ----------------
    with st.container(border=True):
        col_title, col_count = st.columns([3, 1])
        with col_title:
            st.markdown(
                '<div class="section-title">Alert Log</div>',
                unsafe_allow_html=True,
            )

        search = st.text_input(
            "Search machines",
            placeholder="Filter by machine ID...",
            label_visibility="collapsed",
        )
        if search:
            alerts = [
                alert
                for alert in alerts
                if search.lower() in alert["machine_id"].lower()
            ]

        with col_count:
            st.markdown(
                f'<div class="alert-count" style="text-align:right;">'
                f"{len(alerts)} alert(s)</div>",
                unsafe_allow_html=True,
            )

        if not alerts:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <div>No machines match that filter.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        st.markdown("<hr style='border-color:#2a3f5a;'>", unsafe_allow_html=True)

        # NOTE: keep these HTML blocks free of blank lines. Streamlit dedents the
        # string, and a blank line followed by an indented line makes Markdown
        # treat the rest as a code block, showing the HTML source instead.
        for i, alert in enumerate(alerts):
            badge_class, badge_label = _severity(alert["temperature"])

            with st.container(border=True, key=f"alert_card_{i}"):
                col_info, col_error, col_temp, col_status = st.columns([3.4, 1.8, 1.8, 1.4])

                with col_info:
                    st.markdown(
                        f"""
                        <div class="alert-cell">
                            <div class="machine-name">📟 {alert["machine_id"]}</div>
                            <div class="alert-meta">{alert["timestamp"]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_error:
                    st.markdown(
                        f"""
                        <div class="alert-cell">
                            <div class="alert-label">Error Code</div>
                            <div class="alert-value">{alert["error_code"]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_temp:
                    st.markdown(
                        f"""
                        <div class="alert-cell">
                            <div class="alert-label">Temperature</div>
                            <div class="alert-value">🌡 {alert["temperature"]:.1f} °C</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_status:
                    st.markdown(
                        f"""
                        <div class="alert-cell is-right">
                            <span class="badge {badge_class}">{badge_label}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
