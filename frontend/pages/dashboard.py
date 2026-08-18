import streamlit as st
import requests
from datetime import datetime
from pathlib import Path


# =========================================================
# CONFIGURATION
# =========================================================

BACKEND_URL = "http://127.0.0.1:8000"


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Prescriptive AI",
    page_icon="⚙️",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL DASHBOARD
       ===================================================== */

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* Reduce excessive spacing */
    div[data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }

    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.7px;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        color: #718096;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    /* =====================================================
       SECTION TITLES
       ===================================================== */

    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
        letter-spacing: -0.2px;
    }

    /* =====================================================
       DEFAULT STREAMLIT CONTAINERS
       ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid rgba(128,128,128,0.20) !important;
        background: rgba(128,128,128,0.025) !important;
        padding: 4px !important;
        transition: all 0.2s ease;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(59,130,246,0.35) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.04);
    }

    /* =====================================================
       METRIC CARDS
       ===================================================== */

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.18);
        border-radius: 14px;
        padding: 15px 17px;
        background: rgba(128,128,128,0.025);
        min-height: 105px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.55rem;
        font-weight: 750;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 0.75rem;
    }

    /* =====================================================
       SUCCESS / WARNING / ERROR BOXES
       ===================================================== */

    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border-width: 1px !important;
    }

    /* =====================================================
       FORM
       ===================================================== */

    div[data-testid="stForm"] {
        border-radius: 16px !important;
        border: 1px solid rgba(128,128,128,0.20) !important;
        padding: 20px !important;
        background: rgba(128,128,128,0.025) !important;
    }

    /* =====================================================
       INPUT FIELDS
       ===================================================== */

    div[data-baseweb="input"] {
        border-radius: 9px;
    }

    div[data-baseweb="select"] > div {
        border-radius: 9px;
    }

    textarea {
        border-radius: 9px !important;
    }

    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
    }

    .stFormSubmitButton > button {
        border-radius: 10px;
        min-height: 48px;
        font-weight: 750;
        font-size: 0.95rem;
    }

    /* =====================================================
       FILE UPLOADER
       ===================================================== */

    section[data-testid="stFileUploaderDropzone"] {
        border-radius: 12px !important;
    }

    /* =====================================================
       EXPANDER
       ===================================================== */

    div[data-testid="stExpander"] {
        border-radius: 12px !important;
        border: 1px solid rgba(128,128,128,0.20) !important;
    }

    /* =====================================================
       AI REPAIR PLAN
       ===================================================== */

    /* Make AI result containers visually consistent */

    div[data-testid="stVerticalBlockBorderWrapper"] h3 {
        margin-top: 0.2rem;
        margin-bottom: 0.7rem;
        font-size: 1rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] p {
        line-height: 1.65;
    }

    /* =====================================================
       LATEST ALERT
       ===================================================== */

    .small-label {
        color: #718096;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 2px;
    }

    /* =====================================================
       INVENTORY
       ===================================================== */

    /* Native metric styling makes inventory cards consistent */

    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {
        margin-top: 1.4rem !important;
        margin-bottom: 1.4rem !important;
        opacity: 0.25;
    }

    /* =====================================================
       CAPTION
       ===================================================== */

    .stCaption {
        color: #718096 !important;
    }

    /* =====================================================
       IMAGE
       ===================================================== */

    img {
        border-radius: 14px;
    }

    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 900px) {

        .main-title {
            font-size: 2rem;
        }

        .section-title {
            font-size: 1.2rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "latest_iot_alert" not in st.session_state:
    st.session_state["latest_iot_alert"] = None

if "latest_repair_plan" not in st.session_state:
    st.session_state["latest_repair_plan"] = None

if "alert_generated_at" not in st.session_state:
    st.session_state["alert_generated_at"] = None


# =========================================================
# MACHINE HEALTH
# =========================================================

def get_health_status(
    temperature,
    vibration,
    pressure,
    severity
):

    if severity == "Critical":
        return 25, "Critical", "critical"

    if severity == "High":
        return 42, "High Risk", "critical"

    if severity == "Medium":
        return 68, "Warning", "warning"

    if temperature >= 100:
        return 45, "High Risk", "critical"

    if vibration >= 7:
        return 50, "High Risk", "critical"

    if pressure >= 100:
        return 55, "Warning", "warning"

    return 92, "Healthy", "healthy"


# =========================================================
# MACHINE OVERVIEW
# =========================================================

def render_machine_overview():

    alert = st.session_state.get(
        "latest_iot_alert"
    )

    if alert:

        machine_id = alert.get(
            "machine_id",
            "PUMP-01"
        )

        error_code = alert.get(
            "error_code",
            "E-404"
        )

        temperature = alert.get(
            "temperature",
            105.0
        )

        vibration = alert.get(
            "vibration",
            7.5
        )

        pressure = alert.get(
            "pressure",
            120.0
        )

        severity = alert.get(
            "severity",
            "High"
        )

    else:

        machine_id = "PUMP-01"
        error_code = "E-404"
        temperature = 105.0
        vibration = 7.5
        pressure = 120.0
        severity = "High"

    health, health_text, health_class = get_health_status(
        temperature,
        vibration,
        pressure,
        severity
    )

    st.markdown(
        '<div class="section-title">🏭 Machine Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(
        [1, 2],
        gap="large"
    )

    # -----------------------------------------------------
    # MACHINE IMAGE
    # -----------------------------------------------------

    with col1:

        machine_image = Path(
            "assets/machine.png"
        )

        if machine_image.exists():

            st.image(
                str(machine_image),
                width="stretch"
            )

        else:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 🏭"
                )

                st.write(
                    "Machine image"
                )

    # -----------------------------------------------------
    # MACHINE INFORMATION
    # -----------------------------------------------------

    with col2:

        st.markdown(
            f"## ⚙️ {machine_id}"
        )

        if health_class == "healthy":

            st.success(
                f"🟢 {health_text}"
            )

        elif health_class == "warning":

            st.warning(
                f"🟡 {health_text}"
            )

        else:

            st.error(
                f"🔴 {health_text}"
            )

        info1, info2, info3 = st.columns(
            3,
            gap="medium"
        )

        with info1:

            st.metric(
                "Error Code",
                error_code
            )

        with info2:

            st.metric(
                "Severity",
                severity
            )

        with info3:

            st.metric(
                "AI Health",
                f"{health}%"
            )


# =========================================================
# SENSOR CARDS
# =========================================================

def render_sensor_cards():

    alert = st.session_state.get(
        "latest_iot_alert"
    )

    if alert:

        temperature = alert.get(
            "temperature",
            105.0
        )

        vibration = alert.get(
            "vibration",
            7.5
        )

        pressure = alert.get(
            "pressure",
            120.0
        )

        severity = alert.get(
            "severity",
            "High"
        )

    else:

        temperature = 105.0
        vibration = 7.5
        pressure = 120.0
        severity = "High"

    health, health_text, _ = get_health_status(
        temperature,
        vibration,
        pressure,
        severity
    )

    st.markdown(
        '<div class="section-title">📊 Live Equipment Metrics</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(
        4,
        gap="medium"
    )

    with col1:

        st.metric(
            "🌡️ Temperature",
            f"{temperature:.1f} °C",
            "High" if temperature >= 85 else "Normal"
        )

    with col2:

        st.metric(
            "〽️ Vibration",
            f"{vibration:.1f}",
            "High" if vibration >= 7 else "Normal"
        )

    with col3:

        st.metric(
            "💨 Pressure",
            f"{pressure:.1f}",
            "High" if pressure >= 100 else "Normal"
        )

    with col4:

        st.metric(
            "❤️ AI Health",
            f"{health}%",
            health_text
        )


# =========================================================
# MAINTENANCE MANUAL
# =========================================================

def render_manual_section():

    st.markdown(
        '<div class="section-title">📚 Maintenance Manual</div>',
        unsafe_allow_html=True
    )

    with st.container(
        border=True
    ):

        st.write(
            "Upload equipment documentation for the "
            "maintenance knowledge base."
        )

        uploaded_file = st.file_uploader(
            "Upload Maintenance Manual",
            type=[
                "pdf",
                "txt",
                "docx"
            ],
            key="dashboard_manual"
        )

        if uploaded_file:

            st.success(
                f"✅ {uploaded_file.name} uploaded successfully."
            )


# =========================================================
# SIMULATE IoT ALERT
# =========================================================

def render_simulate_alert_section():

    st.markdown(
        '<div class="section-title">🚨 Simulate IoT Alert</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Send equipment sensor data to the AI maintenance "
        "workflow and generate a repair plan."
    )

    with st.container(
        border=True
    ):

        with st.form(
            "iot_alert_form"
        ):

            col1, col2, col3 = st.columns(
                3,
                gap="large"
            )

            # -------------------------------------------------
            # MACHINE
            # -------------------------------------------------

            with col1:

                machine_id = st.text_input(
                    "Machine ID",
                    value="PUMP-01"
                )

                error_code = st.text_input(
                    "Error Code",
                    value="E-003"
                )

            # -------------------------------------------------
            # SENSOR
            # -------------------------------------------------

            with col2:

                temperature = st.number_input(
                    "Temperature (°C)",
                    value=105.0,
                    format="%.2f"
                )

                vibration = st.number_input(
                    "Vibration",
                    value=7.5,
                    format="%.2f"
                )

            # -------------------------------------------------
            # PRESSURE + SEVERITY
            # -------------------------------------------------

            with col3:

                pressure = st.number_input(
                    "Pressure",
                    value=120.0,
                    format="%.2f"
                )

                severity = st.selectbox(
                    "Severity",
                    [
                        "Low",
                        "Medium",
                        "High",
                        "Critical"
                    ],
                    index=2
                )

            st.write("")

            submitted = st.form_submit_button(
                "🚨 Send Alert & Generate AI Repair Plan",
                use_container_width=True
            )

            # =================================================
            # SEND ALERT
            # =================================================

            if submitted:

                payload = {

                    "machine_id": machine_id,

                    "error_code": error_code,

                    "temperature": temperature,

                    "vibration": vibration,

                    "pressure": pressure,

                    "severity": severity

                }

                try:

                    with st.spinner(
                        "🤖 AI is analyzing equipment and technical manuals..."
                    ):

                        response = requests.post(
                            f"{BACKEND_URL}/iot-alert",
                            json=payload,
                            timeout=120
                        )

                    # =================================================
                    # SUCCESS
                    # =================================================

                    if response.status_code == 200:

                        result = response.json()

                        st.session_state[
                            "latest_repair_plan"
                        ] = result

                        st.session_state[
                            "latest_iot_alert"
                        ] = payload

                        st.session_state[
                            "alert_generated_at"
                        ] = datetime.now().strftime(
                            "%d %b %Y, %I:%M %p"
                        )

                        st.success(
                            "✅ Alert received successfully. "
                            "AI repair plan generated."
                        )

                        st.rerun()

                    # =================================================
                    # ERROR
                    # =================================================

                    else:

                        st.error(
                            f"❌ Backend rejected the alert "
                            f"({response.status_code})"
                        )

                        st.code(
                            response.text
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "⚠️ Could not connect to FastAPI."
                    )

                    st.info(
                        "Make sure FastAPI is running on "
                        "http://127.0.0.1:8000"
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "⏳ AI processing timed out."
                    )

                except Exception as e:

                    st.error(
                        f"❌ Unexpected error: {str(e)}"
                    )


# =========================================================
# RECENT ALERT
# =========================================================

def render_recent_alert():

    alert = st.session_state.get(
        "latest_iot_alert"
    )

    if not alert:
        return

    st.markdown(
        '<div class="section-title">🕒 Latest Alert</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(
        4,
        gap="medium"
    )

    with col1:

        st.markdown(
            '<div class="small-label">Machine</div>',
            unsafe_allow_html=True
        )

        st.write(
            alert.get(
                "machine_id",
                "-"
            )
        )

    with col2:

        st.markdown(
            '<div class="small-label">Error</div>',
            unsafe_allow_html=True
        )

        st.write(
            alert.get(
                "error_code",
                "-"
            )
        )

    with col3:

        st.markdown(
            '<div class="small-label">Severity</div>',
            unsafe_allow_html=True
        )

        st.write(
            alert.get(
                "severity",
                "-"
            )
        )

    with col4:

        st.markdown(
            '<div class="small-label">Generated</div>',
            unsafe_allow_html=True
        )

        st.write(
            st.session_state.get(
                "alert_generated_at",
                "Just now"
            )
        )


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_ai_text(text):

    if not text:
        return "Not specified."

    text = str(text).strip()

    text = text.replace(
        "**",
        ""
    )

    return text.strip()


# =========================================================
# EXTRACT AI SECTION
# =========================================================

def extract_section(
    text,
    start_marker,
    end_markers
):

    if not text:
        return ""

    if start_marker not in text:
        return ""

    content = text.split(
        start_marker,
        1
    )[1]

    positions = []

    for marker in end_markers:

        if marker in content:

            positions.append(
                content.index(marker)
            )

    if positions:

        content = content[
            :min(positions)
        ]

    return content.strip()


# =========================================================
# AI REPAIR PLAN
# =========================================================

def render_ai_repair_plan():

    result = st.session_state.get(
        "latest_repair_plan"
    )

    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(
        '<div class="section-title">🤖 AI Repair Plan</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Recommended maintenance actions generated from "
        "the equipment alert and technical manuals."
    )

    # =====================================================
    # NO RESULT
    # =====================================================

    if not result:

        with st.container(
            border=True
        ):

            st.info(
                "🚨 No AI repair plan generated yet."
            )

            st.write(
                "Send an IoT alert above to let the AI "
                "analyze the equipment and generate "
                "recommended maintenance actions."
            )

        return

    # =====================================================
    # BACKEND RESPONSE
    # =====================================================

    if isinstance(
        result,
        dict
    ):

        repair_plan = result.get(
            "repair_plan",
            ""
        )

        generated_query = result.get(
            "generated_query",
            ""
        )

    else:

        repair_plan = str(
            result
        )

        generated_query = ""

    # =====================================================
    # CHECK
    # =====================================================

    if not repair_plan:

        st.warning(
            "⚠️ The AI workflow completed, "
            "but no repair plan was returned."
        )

        return

    # =====================================================
    # STATUS
    # =====================================================

    with st.container(
        border=True
    ):

        st.success(
            "🤖 AI Repair Plan Generated"
        )

    # =====================================================
    # PARSE SECTIONS
    # =====================================================

    text = repair_plan

    # -----------------------------------------------------
    # ERROR VERIFICATION
    # -----------------------------------------------------

    error_verification = extract_section(
        text,
        "SECTION 0 — Error Code Verification",
        [
            "SECTION 0B",
            "SECTION 0C",
            "1. Problem Diagnosis"
        ]
    )

    # -----------------------------------------------------
    # VARIANT CHECK
    # -----------------------------------------------------

    variant_check = extract_section(
        text,
        "SECTION 0B — System/Subsystem Variant Check",
        [
            "SECTION 0C",
            "1. Problem Diagnosis"
        ]
    )

    if not variant_check:

        variant_check = extract_section(
            text,
            "SECTION 0B",
            [
                "SECTION 0C",
                "1. Problem Diagnosis"
            ]
        )

    # -----------------------------------------------------
    # EQUIPMENT SCOPE
    # -----------------------------------------------------

    equipment_scope = extract_section(
        text,
        "SECTION 0C — Equipment Scope Check",
        [
            "1. Problem Diagnosis"
        ]
    )

    if not equipment_scope:

        equipment_scope = extract_section(
            text,
            "SECTION 0C",
            [
                "1. Problem Diagnosis"
            ]
        )

    # -----------------------------------------------------
    # DIAGNOSIS
    # -----------------------------------------------------

    diagnosis = extract_section(
        text,
        "1. Problem Diagnosis",
        [
            "2. Step-by-Step Repair Procedure",
            "3. Required Tools"
        ]
    )

    # -----------------------------------------------------
    # PROCEDURE
    # -----------------------------------------------------

    procedure = extract_section(
        text,
        "2. Step-by-Step Repair Procedure",
        [
            "3. Required Tools",
            "4. Required Spare Parts"
        ]
    )

    # -----------------------------------------------------
    # TOOLS
    # -----------------------------------------------------

    tools = extract_section(
        text,
        "3. Required Tools",
        [
            "4. Required Spare Parts",
            "5. Safety Precautions"
        ]
    )

    # -----------------------------------------------------
    # SPARE PARTS
    # -----------------------------------------------------

    spare_parts = extract_section(
        text,
        "4. Required Spare Parts",
        [
            "5. Safety Precautions",
            "6. Manual References"
        ]
    )

    # -----------------------------------------------------
    # SAFETY
    # -----------------------------------------------------

    safety = extract_section(
        text,
        "5. Safety Precautions",
        [
            "6. Manual References"
        ]
    )

    # -----------------------------------------------------
    # REFERENCES
    # -----------------------------------------------------

    references = ""

    if "6. Manual References" in text:

        references = text.split(
            "6. Manual References",
            1
        )[1].strip()

    # =====================================================
    # ROW 1
    # =====================================================

    col1, col2 = st.columns(
        2,
        gap="medium"
    )

    # -----------------------------------------------------
    # ERROR VERIFICATION
    # -----------------------------------------------------

    with col1:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🔍 Error Code Verification"
            )

            st.markdown(
                clean_ai_text(
                    error_verification
                )
            )

    # -----------------------------------------------------
    # DIAGNOSIS
    # -----------------------------------------------------

    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🩺 Problem Diagnosis"
            )

            st.markdown(
                clean_ai_text(
                    diagnosis
                )
            )

    # =====================================================
    # ROW 2
    # =====================================================

    col1, col2 = st.columns(
        2,
        gap="medium"
    )

    # -----------------------------------------------------
    # SYSTEM VARIANT
    # -----------------------------------------------------

    with col1:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🔎 System / Subsystem Check"
            )

            st.markdown(
                clean_ai_text(
                    variant_check
                )
            )

    # -----------------------------------------------------
    # EQUIPMENT SCOPE
    # -----------------------------------------------------

    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🏭 Equipment Scope"
            )

            st.markdown(
                clean_ai_text(
                    equipment_scope
                )
            )

    # =====================================================
    # ROW 3
    # =====================================================

    col1, col2 = st.columns(
        2,
        gap="medium"
    )

    # -----------------------------------------------------
    # REPAIR PROCEDURE
    # -----------------------------------------------------

    with col1:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🔧 Step-by-Step Repair Procedure"
            )

            st.markdown(
                clean_ai_text(
                    procedure
                )
            )

    # -----------------------------------------------------
    # TOOLS
    # -----------------------------------------------------

    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🧰 Required Tools"
            )

            st.markdown(
                clean_ai_text(
                    tools
                )
            )

    # =====================================================
    # ROW 4
    # =====================================================

    col1, col2 = st.columns(
        2,
        gap="medium"
    )

    # -----------------------------------------------------
    # SPARE PARTS
    # -----------------------------------------------------

    with col1:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 📦 Required Spare Parts"
            )

            st.markdown(
                clean_ai_text(
                    spare_parts
                )
            )

    # -----------------------------------------------------
    # SAFETY
    # -----------------------------------------------------

    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                "### ⚠️ Safety Precautions"
            )

            st.markdown(
                clean_ai_text(
                    safety
                )
            )

    # =====================================================
    # MANUAL REFERENCES
    # =====================================================

    if references:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 📚 Manual References"
            )

            st.markdown(
                clean_ai_text(
                    references
                )
            )

    # =====================================================
    # AI QUERY
    # =====================================================

    if generated_query:

        with st.expander(
            "🔎 View AI Generated Search Query"
        ):

            st.code(
                generated_query
            )


# =========================================================
# INVENTORY
# =========================================================

def render_inventory():

    st.markdown(
        '<div class="section-title">📦 Spare Parts Inventory</div>',
        unsafe_allow_html=True
    )

    inventory = [

        (
            "Pump Bearing",
            12,
            "Available"
        ),

        (
            "Pressure Valve",
            8,
            "Available"
        ),

        (
            "Mechanical Seal",
            4,
            "Low Stock"
        ),

        (
            "Filter Assembly",
            23,
            "Available"
        ),

    ]

    cols = st.columns(
        4,
        gap="medium"
    )

    for col, (
        name,
        quantity,
        status
    ) in zip(
        cols,
        inventory
    ):

        with col:

            st.metric(
                name,
                quantity
            )

            if status == "Available":

                st.success(
                    status
                )

            else:

                st.warning(
                    status
                )


# =========================================================
# PDF REPORT
# =========================================================

def generate_pdf_report():

    try:

        from reportlab.lib.pagesizes import A4

        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
        )

        from reportlab.lib import colors

        from reportlab.lib.styles import (
            getSampleStyleSheet
        )

    except ImportError:

        st.error(
            "ReportLab is not installed. "
            "Run: pip install reportlab"
        )

        return None

    alert = st.session_state.get(
        "latest_iot_alert"
    )

    repair_result = st.session_state.get(
        "latest_repair_plan"
    )

    if not alert:

        return None

    # -----------------------------------------------------
    # REPAIR PLAN
    # -----------------------------------------------------

    if isinstance(
        repair_result,
        dict
    ):

        repair_plan = repair_result.get(
            "repair_plan",
            "No repair plan available."
        )

    else:

        repair_plan = str(
            repair_result
        )

    # -----------------------------------------------------
    # DIRECTORY
    # -----------------------------------------------------

    output_dir = Path(
        "generated_reports"
    )

    output_dir.mkdir(
        exist_ok=True
    )

    # -----------------------------------------------------
    # FILE NAME
    # -----------------------------------------------------

    filename = (
        "maintenance_report_"
        f"{alert.get('machine_id', 'machine')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    filepath = (
        output_dir / filename
    )

    # -----------------------------------------------------
    # DOCUMENT
    # -----------------------------------------------------

    document = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Prescriptive AI - Maintenance Report",
            styles["Title"]
        )
    )

    story.append(
        Spacer(
            1,
            20
        )
    )

    # -----------------------------------------------------
    # EQUIPMENT
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Equipment Information",
            styles["Heading2"]
        )
    )

    equipment_data = [

        [
            "Machine ID",
            alert.get(
                "machine_id",
                "-"
            )
        ],

        [
            "Error Code",
            alert.get(
                "error_code",
                "-"
            )
        ],

        [
            "Temperature",
            f"{alert.get('temperature', '-')} °C"
        ],

        [
            "Vibration",
            str(
                alert.get(
                    "vibration",
                    "-"
                )
            )
        ],

        [
            "Pressure",
            str(
                alert.get(
                    "pressure",
                    "-"
                )
            )
        ],

        [
            "Severity",
            alert.get(
                "severity",
                "-"
            )
        ],

    ]

    table = Table(
        equipment_data,
        colWidths=[
            150,
            300
        ]
    )

    table.setStyle(
        TableStyle(
            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.lightgrey
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

            ]
        )
    )

    story.append(
        table
    )

    story.append(
        Spacer(
            1,
            25
        )
    )

    # -----------------------------------------------------
    # AI REPAIR PLAN
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "AI Repair Plan",
            styles["Heading2"]
        )
    )

    clean_plan = (
        str(repair_plan)
        .replace(
            "**",
            ""
        )
        .replace(
            "\n",
            "<br/>"
        )
    )

    story.append(
        Paragraph(
            clean_plan,
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(
            1,
            20
        )
    )

    story.append(
        Paragraph(
            "Generated by Prescriptive AI",
            styles["BodyText"]
        )
    )

    document.build(
        story
    )

    return filepath


# =========================================================
# PDF SECTION
# =========================================================

def render_pdf_section():

    st.markdown(
        '<div class="section-title">📄 Maintenance Report</div>',
        unsafe_allow_html=True
    )

    if st.session_state.get(
        "latest_repair_plan"
    ):

        st.write(
            "Generate a downloadable PDF containing "
            "the equipment alert and AI repair plan."
        )

        if st.button(
            "📄 Generate Maintenance PDF",
            use_container_width=True
        ):

            pdf_path = generate_pdf_report()

            if pdf_path:

                with open(
                    pdf_path,
                    "rb"
                ) as pdf_file:

                    st.download_button(
                        "⬇️ Download Maintenance Report",
                        data=pdf_file,
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        use_container_width=True
                    )

    else:

        st.info(
            "Generate an AI Repair Plan first "
            "to create the maintenance PDF."
        )


# =========================================================
# MAIN DASHBOARD
# =========================================================

def render():

    # =====================================================
    # TITLE
    # =====================================================

    st.markdown(
        '<div class="main-title">⚙️ Prescriptive AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Industrial Monitoring & Maintenance Center'
        '</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # SYSTEM STATUS
    # =====================================================

    st.success(
        "🟢 System Online"
    )

    st.divider()

    # =====================================================
    # MACHINE
    # =====================================================

    render_machine_overview()

    st.divider()

    # =====================================================
    # METRICS
    # =====================================================

    render_sensor_cards()

    st.divider()

    # =====================================================
    # MANUAL
    # =====================================================

    render_manual_section()

    st.divider()

    # =====================================================
    # IoT ALERT
    # =====================================================

    render_simulate_alert_section()

    st.divider()

    # =====================================================
    # LATEST ALERT
    # =====================================================

    render_recent_alert()

    st.divider()

    # =====================================================
    # AI REPAIR PLAN
    # =====================================================

    render_ai_repair_plan()

    st.divider()

    # =====================================================
    # INVENTORY
    # =====================================================

    render_inventory()

    st.divider()

    # =====================================================
    # PDF
    # =====================================================

    render_pdf_section()


# =========================================================
# RUN DASHBOARD
# =========================================================

if __name__ == "__main__":
    render()