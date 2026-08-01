import streamlit as st

from components.navbar import render_navbar
from components.hero import render_hero
from components.kpi_cards import render_kpis
from components.upload_widget import render_upload
from components.telemetry_form import render_telemetry
from components.search_widget import render_search

def show_dashboard():

    render_navbar()

    render_hero()

    st.subheader("System Overview")

    render_kpis()

    left,center,right = st.columns(3)

    with left:
        render_upload()

    with center:
        render_telemetry()

    with right:
        render_search()