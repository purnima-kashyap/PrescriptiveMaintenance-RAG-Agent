import streamlit as st


st.set_page_config(
    page_title="Prescriptive Maintenance RAG Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():

    with open("styles/style.css") as f:

        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


load_css()


with st.sidebar:

    st.markdown(
        """
        <div class="side-logo">
            🤖
            <h2>Maintenance AI</h2>
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown("---")


    menu = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Upload Manuals",
            "IoT Monitoring",
            "AI Search",
            "Analytics"
        ]
    )


    st.markdown("---")


    st.markdown(
        """
        <div class="side-status">
        🟢 System Online
        <br>
        Vector DB: ChromaDB
        <br>
        Models: RAG + LLM
        </div>
        """,
        unsafe_allow_html=True
    )



st.markdown("""
<div class="navbar">

<div class="logo">
🤖 
<span>
Prescriptive Maintenance AI
</span>
</div>


<div class="menu">

<span>Dashboard</span>
<span>Upload</span>
<span>IoT</span>
<span>Search</span>
<span>Analytics</span>

</div>


<div class="status">

🟢 Online

</div>


</div>

""", unsafe_allow_html=True)



# ==========================
# HERO
# ==========================


st.markdown(
"""
<div class="hero">


<div>

<h1>
🤖 Prescriptive Maintenance RAG Agent
</h1>


<p>
AI-powered predictive maintenance using
Retrieval-Augmented Generation
</p>

</div>


<div class="hero-status">

<h2>
🟢 ONLINE
</h2>

<p>
All systems operational
</p>

</div>


</div>
""",
unsafe_allow_html=True
)



st.markdown(
"### System Overview"
)


c1,c2,c3,c4 = st.columns(4)



kpis = [

("📄","Manuals","12"),

("⚙️","Machines","8"),

("📚","Knowledge Chunks","3842"),

("🤖","Agent Status","Healthy")

]


for col,item in zip(
    [c1,c2,c3,c4],
    kpis
):

    icon,title,value=item


    with col:

        st.markdown(
        f"""
        <div class="kpi">


        <div class="icon">
        {icon}
        </div>


        <h3>
        {title}
        </h3>


        <h2>
        {value}
        </h2>


        </div>
        """,
        unsafe_allow_html=True
        )



st.write("")


left,center,right = st.columns(3)



# -------- Upload --------


with left:

    st.markdown(
    """
    <div class="box">
    <h2>📄 Upload Manual</h2>
    """,
    unsafe_allow_html=True
    )


    pdf = st.file_uploader(
        "Upload machine PDF",
        type=["pdf"]
    )


    if st.button(
        "Process Manual",
        use_container_width=True
    ):

        if pdf:

            st.success(
                "Manual added to knowledge base"
            )

        else:

            st.warning(
                "Select PDF first"
            )


    st.markdown(
    "</div>",
    unsafe_allow_html=True
    )


with center:


    st.markdown(
    """
    <div class="box">

    <h2>⚙️ IoT Telemetry</h2>
    """,
    unsafe_allow_html=True
    )


    machine = st.text_input(
        "Machine ID",
        "MOTOR_001"
    )


    error = st.text_input(
        "Error Code",
        "E102"
    )


    temp = st.slider(
        "Temperature",
        0,
        150,
        95
    )


    if st.button(
        "Send Data",
        use_container_width=True
    ):

        st.success(
            "Telemetry received"
        )


    st.markdown(
    "</div>",
    unsafe_allow_html=True
    )



with right:


    st.markdown(
    """
    <div class="box">

    <h2>🤖 AI Search</h2>
    """,
    unsafe_allow_html=True
    )


    query = st.text_area(
        "Ask maintenance question",
        placeholder=
        "Why is compressor overheating?"
    )


    if st.button(
        "Ask AI",
        use_container_width=True
    ):


        if query:

            st.info(
                "Generating maintenance recommendation..."
            )

        else:

            st.warning(
                "Enter question"
            )


    st.markdown(
    "</div>",
    unsafe_allow_html=True
    )