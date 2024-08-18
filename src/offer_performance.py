# src/offer_performance.py

import streamlit as st
from datetime import timedelta
from utils.data_loader import load_all_data
from utils.data_processor import (
    analyze_offer_performance,
    preprocess_transaction_events,
    preprocess_offer_events,
    preprocess_channels
)
from utils.model_handler import apply_customer_segmentation
from utils.visualizations import (
    plot_success_rate_by_offer_type,
    plot_offer_completion_by_channel,
    plot_segment_distribution,
    plot_channel_success_over_time,
    plot_offer_age_heatmap,
    create_correlation_heatmap,
    plot_income_distribution
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
def generate_insights(offer_events, transaction_events):
    """Generate insights based on offer events and transaction data."""
    rfm_data = apply_customer_segmentation(transaction_events)
    offer_events_with_cluster = offer_events.merge(rfm_data[['cluster']], left_on='customer_id', right_index=True, how='left')

    # Calculate the success rate for each offer type and identify the top one
    success_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean().sort_values(ascending=False)
    top_offer_type = success_rate.idxmax()
    avg_success_rate = success_rate.mean()

    # Calculate the best responding customer segment
    conversion_by_segment = offer_events_with_cluster.groupby('cluster')['offer_success'].mean().sort_values(ascending=False)
    top_segment = conversion_by_segment.idxmax()
    avg_conversion_rate = conversion_by_segment.mean()

    # Identify the most effective channel
    channel_success = offer_events_with_cluster.groupby('channels')['offer_success'].mean().sort_values(ascending=False)
    top_channel = channel_success.idxmax()
    avg_channel_success = channel_success.mean()

    return {
        "top_offer_type": top_offer_type,
        "avg_success_rate": avg_success_rate,
        "top_segment": top_segment,
        "avg_conversion_rate": avg_conversion_rate,
        "top_channel": top_channel,
        "avg_channel_success": avg_channel_success,
        "offer_events_with_cluster": offer_events_with_cluster
    }

@st.cache_data
def filter_data(offer_events, transaction_events, start_date, end_date, selected_offer_types):
    """Filter offer and transaction events based on date range and offer types."""
    filtered_offers = offer_events[(offer_events['time'].dt.date.between(start_date, end_date)) &
                                   (offer_events['offer_type'].isin(selected_offer_types))]
    filtered_transactions = transaction_events[transaction_events['time'].dt.date.between(start_date, end_date)]
    return filtered_offers, filtered_transactions

def offer_performance_page():
    st.markdown('<h1 class="title">Offer Performance Analysis</h1>', unsafe_allow_html=True)
    st.markdown(load_css(), unsafe_allow_html=True)  # Load custom CSS for styling

    # Load and preprocess data
    offer_events, transaction_events = get_preprocessed_data()

    # Sidebar for filters
    st.sidebar.header("⚙️ Filters")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    time_range = st.sidebar.slider("Select Time Range (days)", min_value=1, max_value=30, value=(1, 30))
    selected_offer_types = st.sidebar.multiselect(
        "Select Offer Types",
        options=offer_events['offer_type'].unique(),
        default=offer_events['offer_type'].unique()
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Convert time_range to datetime objects
    min_date = offer_events['time'].min().date()
    start_date = min_date + timedelta(days=time_range[0] - 1)
    end_date = min_date + timedelta(days=time_range[1] - 1)

    # Filter data based on time range and selected offer types
    filtered_offers, filtered_transactions = filter_data(
        offer_events, transaction_events, start_date, end_date, selected_offer_types
    )

    # Check if filtered data is available
    if filtered_offers.empty:
        st.warning("No offer events found for the selected filters. Please adjust the filters and try again.")
        return
    if filtered_transactions.empty:
        st.warning("No transactions found for the selected filters. Please adjust the filters and try again.")
        return

    # Generate dynamic insights
    insights = generate_insights(filtered_offers, filtered_transactions)
    offer_events_with_cluster = insights["offer_events_with_cluster"]

    # Display Key Insights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    insights["top_offer_type"] +
                    '</div><div class="metric-label">Top Offer Type</div></div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f"Segment {insights['top_segment'].astype('int64')}" +
                    '</div><div class="metric-label">Best Responding Segment</div></div>',
                    unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    insights["top_channel"] +
                    '</div><div class="metric-label">Most Effective Channel</div></div>',
                    unsafe_allow_html=True)

    # Offer Success Rate by Type
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 class="sub-header">Channel Success Rate Over Time</h3>', unsafe_allow_html=True)
        channel_success_chart = plot_channel_success_over_time(offer_events_with_cluster)
        st.altair_chart(channel_success_chart, use_container_width=True)

    with col2:
        st.markdown('<h3 class="sub-header">Channel Effectiveness</h3>', unsafe_allow_html=True)
        channel_chart = plot_offer_completion_by_channel(offer_events_with_cluster)
        st.altair_chart(channel_chart, use_container_width=True)

    # Additional Analysis
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown('<h3 class="sub-header">Customer Segment Distribution</h3>', unsafe_allow_html=True)
    segment_distribution_chart = plot_segment_distribution(offer_events_with_cluster)
    st.altair_chart(segment_distribution_chart, use_container_width=True)

    # Demographic Analysis
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown('<h3 class="sub-header">Offer Type Distribution by Age Group</h3>', unsafe_allow_html=True)
    offer_distribution = plot_offer_age_heatmap(filtered_offers)
    st.altair_chart(offer_distribution, use_container_width=True)

    # st.markdown('<h3 class="sub-header">Income Distribution by Gender</h3>', unsafe_allow_html=True)
    # correlation_heatmap = create_correlation_heatmap(offer_data, rfm_data)
    # st.altair_chart(correlation_heatmap, use_container_width=True)

    # Export options
    st.sidebar.header("📤 Export Option")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    if st.sidebar.button("Generate PDF Report"):
        pdf_buffer = generate_offer_performance_pdf(
            insights["top_offer_type"], insights["top_segment"], insights["top_channel"],
            offer_events_with_cluster,
            channel_chart
        )
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="offer_performance_report.pdf",
            mime="application/pdf"
        )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    offer_performance_page()
