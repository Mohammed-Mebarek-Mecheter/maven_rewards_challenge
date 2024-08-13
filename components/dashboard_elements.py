# app/components/dashboard_elements.py

import streamlit as st
from streamlit_elements import elements, mui, nivo
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

from components.kpi_cards import render_kpis


def render_modular_dashboard(df):
    with elements("dashboard"):
        with mui.Accordion():
            with mui.AccordionSummary(expandIcon=mui.Icon("expand_more")):
                st.markdown("<h3>Key Metrics</h3>", unsafe_allow_html=True)
            with mui.AccordionDetails():
                render_kpis(df)

        with mui.Accordion():
            with mui.AccordionSummary(expandIcon=mui.Icon("expand_more")):
                st.markdown("<h3>Offer Analysis</h3>", unsafe_allow_html=True)
            with mui.AccordionDetails():
                render_charts(df)

        with mui.Accordion():
            with mui.AccordionSummary(expandIcon=mui.Icon("expand_more")):
                st.markdown("<h3>Customer Segments</h3>", unsafe_allow_html=True)
            with mui.AccordionDetails():
                render_tables(df)
