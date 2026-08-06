import streamlit as st
import plotly.graph_objects as go
import numpy as np
import requests
import random
from streamlit_autorefresh import st_autorefresh
from components.style_loader import load_css

def create_sensor_chart(title, values, unit, color):

    x = list(range(len(values)))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=values,
            mode="lines+markers",
            line=dict(
                color=color,
                width=3,
                shape="spline",
            ),
            marker=dict(
                size=5,
                color=color,
            ),
            fill="tozeroy",
            fillcolor=color.replace("1)", "0.15)") if "rgba" in color else "rgba(124,58,237,.15)",
        )
    )

    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20,
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,.08)"),
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

def render():

    load_css("iot_monitoring.css")
    st_autorefresh(interval=1000, key="iot_refresh")

    try:
        response = requests.get(
            "http://127.0.0.1:8000/iot/live",
            timeout=2,
        )

        data = response.json()

    except Exception:

        data = {
            "temperature": 72,
            "rpm": 1450,
            "pressure": 5.2,
            "vibration": 0.20,
            "health": 100,
            "fault": "Healthy",
        }

        # Store history for all sensors
    history_keys = {
        "temperature_history": data["temperature"],
        "rpm_history": data["rpm"],
        "pressure_history": data["pressure"],
        "vibration_history": data["vibration"],
    }

    for key, value in history_keys.items():
        if key not in st.session_state:
            st.session_state[key] = []

        st.session_state[key].append(value)

        if len(st.session_state[key]) > 30:
            st.session_state[key].pop(0)

    st.markdown('<div class="iot-page">', unsafe_allow_html=True)

        # =====================================================
    # HERO SECTION
    # =====================================================

    left, right = st.columns([3.5, 1.5], vertical_alignment="center")

    with left:
        st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">
                🏭 Industrial IoT Monitoring
            </h1>
        </div>
        """, unsafe_allow_html=True)

    with right:

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("""
            <div class="status-pill online">
                <span class="dot"></span>
                Online
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="status-pill">
                24 Devices
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown("""
            <div class="status-pill">
                Live
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    # =====================================================
    # KPI CARDS
    # =====================================================

    cards = [
    ("🌡", "Temperature", f'{data["temperature"]}°C', data["fault"]),
    ("⚙", "RPM", str(data["rpm"]), "Running"),
    ("📊", "Pressure", f'{data["pressure"]} Bar', "Live"),
    ("❤️", "AI Health", f'{data["health"]}%', data["fault"]),
    ]

    cols = st.columns(4)

    for col, (icon, title, value, status) in zip(cols, cards):

        with col:
            with st.container(border=True):
                st.markdown(f"## {icon}")
                st.caption(title)
                st.markdown(f"### {value}")
                st.success(status)

    # =====================================================
    # LIVE MONITORING
    # =====================================================

    left, right = st.columns([3, 1])

    # ===========================
    # LIVE SENSOR MONITORING
    # ===========================

    with left:

        # Initialize history
        if "temperature_history" not in st.session_state:
            st.session_state.temperature_history = []

        # Add latest temperature
        st.session_state.temperature_history.append(data["temperature"])

        # Keep only last 30 readings
        if len(st.session_state.temperature_history) > 30:
            st.session_state.temperature_history.pop(0)

        temperature = st.session_state.temperature_history
        x = list(range(len(temperature)))

        # Dynamic line color
        if data["temperature"] < 75:
            line_color = "#22C55E"      # Green
            fill_color = "rgba(34,197,94,0.15)"
        elif data["temperature"] < 85:
            line_color = "#F59E0B"      # Yellow
            fill_color = "rgba(245,158,11,0.15)"
        else:
            line_color = "#EF4444"      # Red
            fill_color = "rgba(239,68,68,0.15)"

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=x,
                y=temperature,
                mode="lines+markers",
                line=dict(
                    color=line_color,
                    width=4,
                    shape="spline",
                ),
                marker=dict(
                    size=6,
                    color=line_color,
                ),
                fill="tozeroy",
                fillcolor=fill_color,
            )
        )

        fig.update_layout(
            title="📈 Live Temperature Monitoring",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=420,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(
                title="Time",
                showgrid=False,
            ),
            yaxis=dict(
                title="Temperature (°C)",
                gridcolor="rgba(255,255,255,.08)",
            ),
            showlegend=False,
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="live_sensor_chart",
        )
    # ===========================
    # MACHINE HEALTH GAUGE
    # ===========================

    with right:

        # Set gauge color based on health
        if data["health"] >= 85:
            gauge_color = "#22C55E"      # Green
        elif data["health"] >= 60:
            gauge_color = "#F59E0B"      # Yellow
        else:
            gauge_color = "#EF4444"      # Red

        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=data["health"],
                title={"text": "Machine Health"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": gauge_color},
                    "steps": [
                        {"range": [0, 60], "color": "#3f1d5a"},
                        {"range": [60, 85], "color": "#5b4b18"},
                        {"range": [85, 100], "color": "#114b2f"},
                    ],
                },
            )
        )

        gauge.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=420,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            gauge,
            width="stretch",
            key="machine_health_gauge",
        )

        st.markdown("<br>", unsafe_allow_html=True)       
    # =====================================================
    # DEVICE STATUS & ACTIVE ALERTS
    # =====================================================

    left, right = st.columns([1.2, 1.8])

    # ===========================
    # DEVICE STATUS
    # ===========================

    with left:

        status = go.Figure(
            go.Pie(
                labels=["Healthy", "Warning", "Critical"],
                values=[18, 4, 2],
                hole=0.65,
            )
        )

        status.update_layout(
            title="🟢 Device Status",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            showlegend=True,
        )

        st.plotly_chart(
            status,
            width="stretch",
        )

    # ===========================
    # ACTIVE ALERTS
    # ===========================

    with right:

        st.subheader("🚨 Active Alerts")

        alerts = []

        if data["temperature"] > 85:
            alerts.append({
                "Machine": "Motor-07",
                "Alert": "High Temperature",
                "Priority": "🔴 High",
            })

        if data["vibration"] > 0.70:
            alerts.append({
                "Machine": "Motor-07",
                "Alert": "High Vibration",
                "Priority": "🟠 Medium",
            })

        if data["pressure"] < 4.8:
            alerts.append({
                "Machine": "Motor-07",
                "Alert": "Pressure Drop",
                "Priority": "🟡 Low",
            })

        if not alerts:
            alerts.append({
                "Machine": "Motor-07",
                "Alert": "No Active Alerts",
                "Priority": "🟢 Healthy",
            })

        st.dataframe(
            alerts,
            width="stretch",
            hide_index=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)  

        # =====================================================
    # AI PREDICTION & RECENT EVENTS
    # =====================================================

    left, right = st.columns([1.2, 1.8])

    with left:
        with st.container(border=True):

            st.subheader("🤖 AI Prediction")

            st.divider()

            st.write("**Equipment:** Motor-07")
            st.write(f"**Current Status:** {data['fault']}")
            st.write(f"**Health Score:** {data['health']}%")

            # AI Prediction
            if data["health"] >= 90:
                confidence = "99%"
                rul = "120 Hours"
                recommendation = "No maintenance required."
                risk = "🟢 Low"

            elif data["health"] >= 75:
                confidence = "95%"
                rul = "72 Hours"
                recommendation = "Monitor machine during next inspection."
                risk = "🟡 Medium"

            elif data["health"] >= 50:
                confidence = "92%"
                rul = "36 Hours"
                recommendation = "Schedule preventive maintenance."
                risk = "🟠 High"

            else:
                confidence = "98%"
                rul = "12 Hours"
                recommendation = "Immediate maintenance required."
                risk = "🔴 Critical"

            st.write(f"**Prediction Confidence:** {confidence}")
            st.write(f"**Remaining Useful Life:** {rul}")
            st.write(f"**Risk Level:** {risk}")

            st.divider()

            if data["health"] >= 90:
                st.success(recommendation)

            elif data["health"] >= 50:
                st.warning(recommendation)

            else:
                st.error(recommendation)
    # ===========================
    # RECENT EVENTS
    # ===========================

    with right:

        st.subheader("🕒 Recent Events")

        events = [
            ("10:02", "✅ Scheduled Maintenance Completed"),
            ("10:10", "🟢 Machine Started"),
            ("10:15", "⚠ Temperature Rising"),
            ("10:18", "⚠ Vibration Threshold Exceeded"),
            ("10:21", "🔴 Critical Alert Generated"),
            ("10:28", "🤖 AI Recommendation Generated"),
        ]

        for time, event in events:
            st.markdown(f"**{time}** &nbsp;&nbsp; {event}")

    st.markdown("<br>", unsafe_allow_html=True) 

        # =====================================================
    # EQUIPMENT OVERVIEW
    # =====================================================

    st.subheader("🏭 Equipment Overview")

    machines = [
        "Motor-01",
        "Pump-02",
        "Boiler-03",
        "Compressor-04",
        "Fan-05",
        "Conveyor-06",
    ]

    equipment = []

    for machine in machines:

        temp = round(data["temperature"] + random.uniform(-8, 8), 1)
        rpm = int(data["rpm"] + random.randint(-80, 80))
        pressure = round(data["pressure"] + random.uniform(-0.4, 0.4), 2)
        health = max(20, min(100, data["health"] + random.randint(-20, 10)))

        if health >= 85:
            status = "🟢 Healthy"
        elif health >= 60:
            status = "🟡 Warning"
        else:
            status = "🔴 Critical"

        equipment.append(
            {
                "Machine": machine,
                "Temperature": f"{temp}°C",
                "RPM": rpm,
                "Pressure": f"{pressure} Bar",
                "Health": f"{health}%",
                "Status": status,
            }
        )

    st.dataframe(
        equipment,
        width="stretch",
        hide_index=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    healthy = sum(1 for item in equipment if "Healthy" in item["Status"])
    warning = sum(1 for item in equipment if "Warning" in item["Status"])
    critical = sum(1 for item in equipment if "Critical" in item["Status"])

    if critical > 0:
        st.error(
            f"🚨 {critical} machine(s) require immediate attention."
        )
    elif warning > 0:
        st.warning(
            f"⚠️ {warning} machine(s) need preventive maintenance."
        )
    else:
        st.success("✅ All Industrial IoT Systems Operating Normally")

    st.markdown("</div>", unsafe_allow_html=True)