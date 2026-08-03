
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "backend" / "telemetry.db"

@st.cache_data(ttl=2) 
def load_real_data():
    if not DB_PATH.exists():
        # If the database doesn't exist yet, return an empty dataframe
        return pd.DataFrame(columns=["timestamp", "machine_id", "error_code", "temperature"])
    
    # Connect to the DB and pull everything directly into Pandas
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM alerts", conn)
    conn.close()
    
    if not df.empty:
        # Ensure pandas understands the timestamp column is a date, not just text
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
    return df


def render():
    st.markdown(
        """
        <style>
        /* This targets the large number/value in the metric */
        [data-testid="stMetricValue"] {
            color: #FFFFFF !important; /* Pure white */
        }
        /* This targets the smaller label above the number */
        [data-testid="stMetricLabel"] {
            color: #A0AEC0 !important; /* Light gray */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("📈 System Analytics")
    st.markdown("Historical IoT Telemetry & Alert Trends across the factory floor.")

    # --- 1. CHANGED LINE: Fetch real data from SQLite database instead of mock data ---
    df = load_real_data()

    # --- 2. NEW SAFETY CHECK: If no alerts exist yet, gracefully warn the user ---
    if df.empty:
        st.warning("⚠️ No telemetry data received in the database yet. Send a test alert from FastAPI (http://127.0.0.1:8000/docs) to populate this page!")
        return

    st.subheader("Factory Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Alerts", value=len(df))
    with col2:
        highest_temp = df['temperature'].max()
        st.metric(label="Max Temp Recorded", value=f"{highest_temp} °C")
    with col3:
        most_common_error = df['error_code'].mode()[0]
        st.metric(label="Most Frequent Error", value=most_common_error)
    with col4:
        most_problematic_machine = df['machine_id'].mode()[0]
        st.metric(label="Highest Alert Machine", value=most_problematic_machine)

    st.divider()

    # --- Charts ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Alerts by Error Code")
        error_counts = df['error_code'].value_counts()
        st.bar_chart(error_counts, color="#ff4b4b")

    with col_chart2:
        st.subheader("Alerts by Machine")
        machine_counts = df['machine_id'].value_counts()
        st.bar_chart(machine_counts, color="#1f77b4")

    st.divider()

    st.subheader("Temperature History over Time")
    temp_df = df.set_index("timestamp")[["temperature"]]
    st.line_chart(temp_df, color="#ff7f0e")

    st.divider()

    st.subheader("Raw Telemetry Logs")
    with st.expander("Click to view raw historical data"):
        st.dataframe(df, use_container_width=True)