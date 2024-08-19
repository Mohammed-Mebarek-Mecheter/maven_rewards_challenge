# src/offer_performance.py
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from utils.data_loader import load_all_data
from utils.data_processor import (
    preprocess_transaction_events,
    preprocess_offer_events,
    preprocess_channels
)
from utils.model_handler import apply_customer_segmentation
from utils.visualizations import (
    plot_offer_completion_by_channel,
    plot_channel_success_over_time,
    plot_offer_age_heatmap,
    plot_offer_performance_heatmap,
    plot_offer_funnel
)
from utils.pdf_generator import generate_offer_performance_pdf
from utils.styles import load_css

@st.cache_data
def get_preprocessed_data():
    """Load and preprocess offer and transaction data."""
    offer_events, transaction_events = load_all_data()
    offer_events = preprocess_offer_events(offer_events)
    transaction_events = preprocess_transaction_events(transaction_events)
    offer_events = preprocess_channels(offer_events)
    return offer_events, transaction_events

@st.cache_data
def generate_insights(filtered_offers, filtered_transactions):
    """Generate insights based on offer events and transaction data."""
    rfm_data = apply_customer_segmentation(filtered_transactions)

    offer_events_with_cluster = filtered_offers.merge(
        rfm_data[['cluster']], left_on='customer_id', right_index=True, how='left'
    )

    offer_events_with_cluster['cluster'] = offer_events_with_cluster['cluster'].fillna(-1).astype(int)

    # Calculate the success rate for each offer type and identify the top one
    success_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean().sort_values(ascending=False)
    top_offer_type = success_rate.idxmax()

    # Calculate the best responding customer segment
    conversion_by_segment = offer_events_with_cluster.groupby('cluster')['offer_success'].mean().sort_values(ascending=False)
    top_segment = conversion_by_segment.idxmax()

    # Identify the most effective channel
    channel_success = offer_events_with_cluster.groupby('channels')['offer_success'].mean().sort_values(ascending=False)
    top_channel = channel_success.idxmax()

    return {
        "top_offer_type": top_offer_type,
        "top_offer_type_rate": success_rate[top_offer_type],
        "top_segment": top_segment,
        "top_segment_rate": conversion_by_segment[top_segment],
        "top_channel": top_channel,
        "top_channel_rate": channel_success[top_channel],
        "total_revenue": filtered_transactions['amount'].sum(),
        "avg_transaction_value": filtered_transactions['amount'].mean(),
        "total_offers": len(filtered_offers),
        "offer_completion_rate": filtered_offers['offer_success'].mean(),
        "total_customers_impacted": filtered_offers['customer_id'].nunique(),
    }

@st.cache_data
def filter_data(df, time_range=None, offer_types=None):
    """Filter the data based on time range and offer types."""
    if time_range:
        start_time, end_time = time_range
        df = df[(df['time'] >= pd.to_datetime(start_time)) & (df['time'] <= pd.to_datetime(end_time))]

    if offer_types:
        df = df[df['offer_type'].isin(offer_types)]

    return df

def display_metric_card(value, label):
    return f'''
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    '''

def offer_performance_page():
    # st.markdown('<h1 class="title">Offer Performance Analysis</h1>', unsafe_allow_html=True)
    st.markdown(load_css(), unsafe_allow_html=True)  # Load custom CSS for styling

    # Load and preprocess data
    offer_events, transaction_events = get_preprocessed_data()

    # Sidebar for filters
    st.sidebar.header("⚙️ Filters")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    time_range_days = st.sidebar.slider("Select Time Range (days)", min_value=1, max_value=30, value=(1, 30))
    time_range_hours = st.sidebar.slider("Select Time Range (hours)", min_value=0, max_value=30*24, value=(0, 30*24))
    selected_offer_types = st.sidebar.multiselect(
        "Select Offer Types",
        options=offer_events['offer_type'].unique(),
        default=offer_events['offer_type'].unique()
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Convert time_range_days to datetime objects
    min_date = offer_events['time'].min().date()
    start_date = min_date + timedelta(days=time_range_days[0] - 1)
    end_date = min_date + timedelta(days=time_range_days[1] - 1)

    # Filter data based on time range and selected offer types
    filtered_offers = filter_data(offer_events, (start_date, end_date), selected_offer_types)
    filtered_transactions = filter_data(transaction_events, (start_date, end_date))

    # Check if filtered data is available
    if filtered_offers.empty:
        st.warning("No offer events found for the selected filters. Please adjust the filters and try again.")
        return
    if filtered_transactions.empty:
        st.warning("No transactions found for the selected filters. Please adjust the filters and try again.")
        return

    # Generate dynamic insights
    insights = generate_insights(filtered_offers, filtered_transactions)

    # Display Key Insights
    cols = st.columns(4)  # Create 4 columns for key metrics
    metrics = [
        (insights["top_offer_type"], "Top Offer Type"),
        (f'{insights["offer_completion_rate"]:.2%}', "Offer Completion Rate"),
        (f'${insights["total_revenue"]:,.0f}', "Total Revenue from Offers"),
        (f'{insights["total_offers"]:,}', "Total Offers Sent")
    ]
    for col, (value, label) in zip(cols, metrics):
        col.markdown(display_metric_card(value, label), unsafe_allow_html=True)

    # Display Additional Metrics
    cols = st.columns(3)  # Create 3 columns for additional metrics
    additional_metrics = [
        (insights["top_channel"], "Most Effective Channel"),
        (f'${insights["avg_transaction_value"]:.2f}', "Average Transaction Value"),
        (f'{insights["total_customers_impacted"]:,}', "Total Customers Impacted")
    ]
    for col, (value, label) in zip(cols, additional_metrics):
        col.markdown(display_metric_card(value, label), unsafe_allow_html=True)

    # Offer Success Rate by Type
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 class="sub-header">Channel Success Rate Over Time</h3>', unsafe_allow_html=True)
        channel_success_chart = plot_channel_success_over_time(filtered_offers)
        st.altair_chart(channel_success_chart, use_container_width=True)

    with col2:
        st.markdown('<h3 class="sub-header">Channel Effectiveness</h3>', unsafe_allow_html=True)
        channel_chart = plot_offer_completion_by_channel(filtered_offers)
        st.altair_chart(channel_chart, use_container_width=True)

    # Additional Analysis
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 class="sub-header">Offer Success Rate</h3>', unsafe_allow_html=True)
        offer_performance_heatmap = plot_offer_performance_heatmap(filtered_offers)
        st.altair_chart(offer_performance_heatmap, use_container_width=True)

    with col2:
        st.markdown('<h3 class="sub-header">Customer Activity</h3>', unsafe_allow_html=True)
        offer_funnel = plot_offer_funnel(filtered_offers)
        st.plotly_chart(offer_funnel, use_container_width=True)

    # Demographic Analysis
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown('<h3 class="sub-header">Offer Type Distribution by Age Group</h3>', unsafe_allow_html=True)
    offer_distribution = plot_offer_age_heatmap(filtered_offers)
    st.altair_chart(offer_distribution, use_container_width=True)

    # Export options
    st.sidebar.header("📤 Export Option")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    if st.sidebar.button("Generate PDF Report"):
        pdf_buffer = generate_offer_performance_pdf(insights)
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="offer_performance_report.pdf",
            mime="application/pdf"
        )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    offer_performance_page()
