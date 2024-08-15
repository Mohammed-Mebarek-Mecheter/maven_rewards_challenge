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
    plot_channel_success_over_time
)
from utils.pdf_generator import generate_offer_performance_pdf
from st_aggrid import AgGrid, GridOptionsBuilder

@st.cache_data
def get_preprocessed_data():
    offer_events, transaction_events = load_all_data()
    offer_events = preprocess_offer_events(offer_events)
    transaction_events = preprocess_transaction_events(transaction_events)
    offer_events = preprocess_channels(offer_events)
    return offer_events, transaction_events

@st.cache_data
def generate_insights(offer_events, transaction_events):
    rfm_data = apply_customer_segmentation(transaction_events)
    offer_events_with_cluster = offer_events.merge(rfm_data[['cluster']], left_on='customer_id', right_index=True, how='left')

    success_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean().sort_values(ascending=False)
    top_offer_type = success_rate.idxmax()

    conversion_by_segment = offer_events_with_cluster.groupby('cluster')['offer_success'].mean().sort_values(
        ascending=False)
    top_segment = conversion_by_segment.idxmax()

    # Channels are already exploded via preprocess_channels, so we can directly group by 'channels'
    channel_success = offer_events_with_cluster.groupby('channels')['offer_success'].mean().sort_values(ascending=False)
    top_channel = channel_success.idxmax()

    return top_offer_type, top_segment, top_channel, offer_events_with_cluster


@st.cache_data
def filter_data(offer_events, transaction_events, start_date, end_date, selected_offer_types):
    filtered_offers = offer_events[(offer_events['time'].dt.date.between(start_date, end_date)) &
                                   (offer_events['offer_type'].isin(selected_offer_types))]
    filtered_transactions = transaction_events[transaction_events['time'].dt.date.between(start_date, end_date)]
    return filtered_offers, filtered_transactions

def offer_performance_page():
    st.markdown('<h1 class="title">Offer Performance Analysis</h1>', unsafe_allow_html=True)
    # Add CSS for custom styling
    st.markdown("""
                <style>
                /* Page Title Styling */
                .title {
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: #3e2a1e; /* Deep Coffee */
                    margin-bottom: 2rem;
                    text-align: center;
                    animation: fadeInDown 1s ease;
                }
                /* Header Styling */
                .header {
                    font-size: 1.8rem;
                    font-weight: 600;
                    color: #3e2a1e; /* Deep Coffee */
                    margin-bottom: 1rem;
                    text-align: center;
                    border-bottom: 2px solid #e0d9cf;
                    padding-bottom: 0.5rem;
                    animation: fadeInUp 1s ease;
                }
                .sidebar h2 {
                    color: #3e2a1e; /* Deep Coffee */
                }margin-bottom: 0.5rem;
                }
                /* Section Divider */
                .section-divider {
                    margin: 3rem 0;
                    border-bottom: 2px solid #e0d9cf;
                    animation: fadeIn 1s ease;
                }
                /* Fade-in Animations */
                @keyframes fadeInDown {
                    from { opacity: 0; transform: translateY(-20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                </style>
                """, unsafe_allow_html=True)

    # Load and preprocess data
    offer_events, transaction_events = get_preprocessed_data()

    # Sidebar for customizations
    st.sidebar.header("⚙️ Filters")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    time_range = st.sidebar.slider("Select Time Range (days)", min_value=1, max_value=30, value=(1, 30))
    selected_offer_types = st.sidebar.multiselect("Select Offer Types", options=offer_events['offer_type'].unique(),
                                                  default=offer_events['offer_type'].unique())
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Convert time_range to datetime objects
    min_date = offer_events['time'].min().date()
    start_date = min_date + timedelta(days=time_range[0] - 1)
    end_date = min_date + timedelta(days=time_range[1] - 1)

    # Filter data based on time range and selected offer types
    filtered_offers, filtered_transactions = filter_data(offer_events, transaction_events, start_date, end_date,
                                                         selected_offer_types)

    # Generate dynamic insights
    top_offer_type, top_segment, top_channel, offer_events_with_cluster = generate_insights(filtered_offers,
                                                                                            filtered_transactions)

    # Display the insights
    #st.markdown('<h2 class="header">📊 Key Insights</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    top_offer_type +
                    '</div><div class="metric-label">Top Offer Type</div></div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f"Segment {top_segment.astype('int64')}" +
                    '</div><div class="metric-label">Best Responding Segment</div></div>',
                    unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    top_channel +
                    '</div><div class="metric-label">Most Effective Channel</div></div>',
                    unsafe_allow_html=True)

    # Offer Success Rate by Type
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    #st.markdown('<h2 class="header">📈 Offer Performance Analysis</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 class="sub-header">Success Rate by Offer Type</h3>', unsafe_allow_html=True)
        success_rate_chart = plot_success_rate_by_offer_type(offer_events_with_cluster)
        st.altair_chart(success_rate_chart, use_container_width=True)

    with col2:
        st.markdown('<h3 class="sub-header">Channel Effectiveness</h3>', unsafe_allow_html=True)
        channel_chart = plot_offer_completion_by_channel(offer_events_with_cluster)
        st.altair_chart(channel_chart, use_container_width=True)

    # Replace the large AgGrid table with two efficient visualizations
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    #st.markdown('<h2 class="header">🔍 Detailed Data View</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 class="sub-header">Channel Success Rate Over Time</h3>', unsafe_allow_html=True)
        channel_success_chart = plot_channel_success_over_time(offer_events_with_cluster)
        st.altair_chart(channel_success_chart, use_container_width=True)

    with col2:
        st.markdown('<h3 class="sub-header">Customer Segment Distribution</h3>', unsafe_allow_html=True)
        segment_distribution_chart = plot_segment_distribution(offer_events_with_cluster)
        st.altair_chart(segment_distribution_chart, use_container_width=True)

    # Export options
    st.sidebar.header("📤 Export Option")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    if st.sidebar.button("Generate PDF Report"):
        pdf_buffer = generate_offer_performance_pdf(
            top_offer_type, top_segment, top_channel,
            offer_events_with_cluster,
            success_rate_chart, channel_chart
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
