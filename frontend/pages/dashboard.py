import streamlit as st
from components.style_loader import load_css
import requests

def render_simulate_alert_section():
    """Renders Section 2: Simulate IoT Alert"""
    
    st.markdown("### 2   Simulate IoT Alert")
    st.markdown("Test equipment anomalies and trigger the AI maintenance workflow.")
    
    # We use a container with a border to match the mock-up's boxed design
    with st.container(border=True):
        # We use a form so the page doesn't reload every time a user types a letter
        with st.form("iot_alert_form"):
            # Create columns for the input fields
            col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 1])
            
            with col1:
                machine_id = st.text_input("Machine ID", value="M1234")
            with col2:
                error_code = st.text_input("Error Code", value="E-404")
            with col3:
                temperature = st.number_input("Temperature (°C)", value=85.00, format="%.2f")
            
            # Empty column to push the button to the right, or to add more fields later
            with col4:
                st.write("") # Spacing
                st.write("") # Spacing
                submitted = st.form_submit_button("🚨 Send Alert", use_container_width=True)
                
            if submitted:
                # Prepare the exact JSON payload the backend expects
                payload = {
                    "machine_id": machine_id,
                    "error_code": error_code,
                    "temperature": temperature
                }
                
                try:
                    # Send the data to FastAPI endpoint
                    # Make sure backend server is running on port 8000!
                    response = requests.post("http://127.0.0.1:8000/iot-alert", json=payload)
                    
                    if response.status_code == 200:
                        st.success("✅ Alert received successfully. AI is analyzing...")
                        # can optionally store the response in st.session_state 
                        # so Section 3 (AI Repair Plan) can read and display it.
                        st.session_state['latest_repair_plan'] = response.json()
                    else:
                        st.error(f"❌ Backend rejected the data: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Could not connect to backend. Is FastAPI running?")

def render():
    st.title("Smart Maintenance Assistant")
    st.markdown("Monitor equipment, analyze IoT alerts, and generate intelligent maintenance plans.")
    
    # Section 1: Upload Manual 
    st.info("Section 1: Upload Manual (To be built)")
    
    # Section 2: Your Form
    render_simulate_alert_section()
    
    # Section 3: AI Repair Plan 
    st.info("Section 3: AI Repair Plan (To be built)")


