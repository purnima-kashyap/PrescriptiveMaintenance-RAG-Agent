"""
Standalone preview harness for Step 3 (AI Repair Plan).

Step 2 (the IoT alert simulator) is being built separately, so this script
exists purely so the repair plan section can be run and styled on its own. It is
NOT part of the app — app.py never imports it, and it can be deleted once Step 2
lands and the section is rendered from dashboard.py.

Run it from the frontend/ folder:

    streamlit run demo_repair_plan.py

"Sample response" needs nothing running. "Live backend" calls POST /iot-alert on
localhost:8000, which requires the FastAPI server and Ollama to be up.
"""
import requests
import streamlit as st

from components.repair_plan import render_repair_plan
from components.style_loader import load_css

API_URL = "http://localhost:8000"

# A response shaped exactly like POST /iot-alert returns, with the plan text
# following the section order from backend/app/prompts/repair_prompt.py.
SAMPLE_RESULT = {
    "status": "success",
    "received_alert": {
        "machine_id": "M1234",
        "error_code": "E-404",
        "temperature": 85.0,
        # Display-only extras Step 2 may pass through; the backend ignores them.
        "vibration": 7.5,
        "pressure": 120,
        "severity": "High",
    },
    "generated_query": "M1234 error E-404 high temperature 85C cooling fault",
    "repair_plan": """SECTION 0 — Error Code Verification
The exact error code "E-404" WAS found in the retrieved manual context.

SECTION 0B — System/Subsystem Variant Check
Only one cooling system variant (forced-air) is present in the retrieved
context, so the plan below applies directly.

SECTION 0C — Equipment Scope Check
The machine identifier "M1234" was found in the manual, confirming this manual
covers the reported equipment.

1. Problem Diagnosis
Abnormally high operating temperature detected. The equipment may be
experiencing cooling system failure or restricted airflow.

2. Step-by-Step Repair Procedure
1. Inspect cooling fan and ventilation system
2. Check coolant level
3. Inspect temperature sensor
4. Clean air filters
5. Restart equipment after inspection

3. Required Tools
- Torque wrench (10-50 Nm)
- Infrared thermometer
- Phillips screwdriver set

4. Required Spare Parts
- Air filter cartridge, part no. AF-2210
- Coolant, 2 L

5. Safety Precautions
- Power off the equipment before opening the maintenance panel.
- Allow the unit to cool below 40 °C before touching internal components.

6. Manual References
Compressor_Manual.pdf, Page 42 — Cooling system maintenance.
""",
}


def _send_live_alert(machine_id, error_code, temperature, vibration, pressure, severity):
    """IoTAlert requires all six fields — omitting any of them returns a 422."""
    response = requests.post(
        f"{API_URL}/iot-alert",
        json={
            "machine_id": machine_id,
            "error_code": error_code,
            "temperature": temperature,
            "vibration": vibration,
            "pressure": pressure,
            "severity": severity,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()


def main():
    st.set_page_config(page_title="Repair Plan Preview", page_icon="🛠", layout="wide")
    load_css("base.css")
    load_css("maintenance_workspace.css")

    st.markdown(
        '<div class="maintenance-page-title">🛠️ Repair Plan — Preview</div>',
        unsafe_allow_html=True,
    )
    st.caption("Standalone harness for Step 3. Not wired into the app.")

    source = st.radio(
        "Data source",
        ["Sample response", "Live backend"],
        horizontal=True,
        key="demo_source",
    )

    if source == "Sample response":
        st.session_state["demo_result"] = SAMPLE_RESULT
    else:
        col_id, col_code, col_temp = st.columns(3)
        with col_id:
            machine_id = st.text_input("Machine ID", value="M1234", key="demo_machine")
        with col_code:
            # IoTAlert rejects codes without a hyphen (see iot_models.py).
            error_code = st.text_input("Error Code", value="E-404", key="demo_code")
        with col_temp:
            temperature = st.number_input("Temperature (°C)", value=85.0, key="demo_temp")

        col_vib, col_press, col_sev, col_send = st.columns([1, 1, 1, 1])
        with col_vib:
            vibration = st.number_input("Vibration (mm/s)", value=7.5, key="demo_vib")
        with col_press:
            pressure = st.number_input("Pressure (psi)", value=120.0, key="demo_press")
        with col_sev:
            severity = st.selectbox(
                "Severity", ["Low", "Medium", "High", "Critical"], index=2, key="demo_sev"
            )
        with col_send:
            st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
            send = st.button("🔔 Send Alert", type="primary", use_container_width=True)

        if send:
            with st.spinner("Running the agent (retrieval + LLM)…"):
                try:
                    st.session_state["demo_result"] = _send_live_alert(
                        machine_id, error_code, temperature, vibration, pressure, severity
                    )
                except Exception as exc:
                    st.session_state["demo_result"] = None
                    st.error(f"Request failed: {exc}")

    st.divider()

    with st.container(border=True):
        render_repair_plan(st.session_state.get("demo_result"), key_prefix="demo_plan")

    with st.expander("Raw /iot-alert response"):
        st.json(st.session_state.get("demo_result") or {})


if __name__ == "__main__":
    main()
