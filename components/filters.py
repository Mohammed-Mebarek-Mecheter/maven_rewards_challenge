# app/components/filters.py

import streamlit as st
import pandas as pd
from datetime import timedelta

def enhanced_filters(df):
    st.sidebar.header("Filters")

    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['time'].min(), df['time'].max()),
        min_value=df['time'].min(),
        max_value=df['time'].max()
    )

    # Customer segment filter
    selected_segments = st.sidebar.multiselect(
        "Select Customer Segments",
        options=df['cluster'].unique(),
        default=df['cluster'].unique()
    )

    # Offer type filter
    selected_offer_types = st.sidebar.multiselect(
        "Select Offer Types",
        options=df['offer_type'].unique(),
        default=df['offer_type'].unique()
    )

    return date_range, selected_segments, selected_offer_types
