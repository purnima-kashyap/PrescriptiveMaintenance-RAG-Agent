import streamlit as st

def render_kpis():

    c1,c2,c3,c4 = st.columns(4)

    data = [

        ("📄","Manuals","12"),
        ("⚙️","Machines","8"),
        ("📚","Knowledge Chunks","3842"),
        ("🤖","Agent","Healthy")

    ]

    for col,item in zip([c1,c2,c3,c4],data):

        icon,title,value=item

        with col:

            st.markdown(f"""
            <div class="kpi">

            <div class="icon">{icon}</div>

            <h3>{title}</h3>

            <h2>{value}</h2>

            </div>
            """, unsafe_allow_html=True)