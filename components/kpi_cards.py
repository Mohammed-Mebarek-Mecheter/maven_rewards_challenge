# app/components/kpi_cards.py

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

def render_kpis(df):
    """
    Render the KPI cards at the top of the dashboard.

    :param df: The DataFrame containing the necessary data.
    """

    # Calculate KPIs
    total_revenue = df['Amount'].sum()
    avg_transaction_value = df[df['Event'] == 'Transaction']['Amount'].mean()
    customer_acquisition_cost = 10  # Assuming a fixed value for CAC, replace with actual calculation if available
    offer_completion_rate = df[df['Event'] == 'Offer Completed'].shape[0] / df[df['Event'] == 'Offer Received'].shape[0]
    active_customers = df['Customer_Id'].nunique()

    # Display KPIs in the first row
    col1, col2, col3 = st.columns([1, 1, 1])

    col1.metric(label="Avg. Transaction Value", value=f"${avg_transaction_value:,.2f}")
    col2.metric(label="Customer Acquisition Cost", value=f"${customer_acquisition_cost:.2f}")
    col3.metric(label="Offer Completion Rate", value=f"{offer_completion_rate:.2%}")

    # Display KPIs in the second row
    col4, col5 = st.columns([2, 2])

    col4.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
    col5.metric(label="Active Customers", value=f"{active_customers:,}")

    # Style the KPI cards
    style_metric_cards(border_left_color='#1f77b4')
