# pages/customer_segments.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_data
from utils.data_processor import preprocess_offer_events, preprocess_transaction_events, create_customer_segments
from utils.visualizations import plot_customer_segments

def customer_segments_page():
    st.title("Customer Segmentation Analysis")

    # Load and preprocess data
    offer_events, transaction_events = load_all_data()
    offer_events = preprocess_offer_events(offer_events)
    transaction_events = preprocess_transaction_events(transaction_events)

    # Combine datasets
    customer_data = pd.merge(offer_events, transaction_events[['customer_id', 'total_spend']], on='customer_id', how='left')
    customer_data = customer_data.drop_duplicates(subset='customer_id')

    # Sidebar for interactive filters
    st.sidebar.header("Filters")
    age_range = st.sidebar.slider("Age Range", int(customer_data['age'].min()), int(customer_data['age'].max()), (25, 75))
    income_range = st.sidebar.slider("Income Range", int(customer_data['income'].min()), int(customer_data['income'].max()), (30000, 120000))
    selected_genders = st.sidebar.multiselect("Gender", customer_data['gender'].unique(), default=customer_data['gender'].unique())

    # Apply filters
    filtered_data = customer_data[
        (customer_data['age'].between(age_range[0], age_range[1])) &
        (customer_data['income'].between(income_range[0], income_range[1])) &
        (customer_data['gender'].isin(selected_genders))
        ]

    # Demographic Analysis
    st.header("Demographic Analysis")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Age Distribution")
        fig_age = px.histogram(filtered_data, x='age', nbins=20)
        st.plotly_chart(fig_age)

    with col2:
        st.subheader("Gender Distribution")
        fig_gender = px.pie(filtered_data, names='gender')
        st.plotly_chart(fig_gender)

    with col3:
        st.subheader("Income Distribution")
        fig_income = px.box(filtered_data, y='income')
        st.plotly_chart(fig_income)

    # RFM Analysis
    st.header("RFM (Recency, Frequency, Monetary) Analysis")
    rfm_data = create_customer_segments(offer_events, transaction_events)

    # Display RFM metrics
    st.write("RFM Metrics Summary:")
    st.write(rfm_data.describe())

    # Cluster Analysis
    st.header("Cluster Analysis of Customer Behavior")
    fig_clusters = plot_customer_segments(rfm_data)
    st.plotly_chart(fig_clusters)

    # Segment Profiles
    st.header("Customer Segment Profiles")
    segment_profiles = rfm_data.groupby('cluster').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean'
    })
    st.write(segment_profiles)

    # Segment Size
    fig_segment_size = px.pie(rfm_data, names='cluster', title="Segment Size Distribution")
    st.plotly_chart(fig_segment_size)

    # Interactive Segment Explorer
    st.header("Interactive Segment Explorer")
    selected_segment = st.selectbox("Select a segment to explore", rfm_data['cluster'].unique())
    segment_data = filtered_data[filtered_data['customer_id'].isin(rfm_data[rfm_data['cluster'] == selected_segment].index)]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Age Distribution in Segment")
        fig_segment_age = px.histogram(segment_data, x='age', nbins=20)
        st.plotly_chart(fig_segment_age)

    with col2:
        st.subheader("Income Distribution in Segment")
        fig_segment_income = px.box(segment_data, y='income')
        st.plotly_chart(fig_segment_income)

    # Offer Response by Segment
    st.subheader("Offer Response by Segment")
    offer_response = segment_data.groupby('offer_type')['offer_success'].mean().reset_index()
    fig_offer_response = px.bar(offer_response, x='offer_type', y='offer_success', title=f"Offer Success Rate for Segment {selected_segment}")
    st.plotly_chart(fig_offer_response)

if __name__ == "__main__":
    customer_segments_page()