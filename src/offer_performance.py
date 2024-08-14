# src/offer_performance.py
import streamlit as st
from datetime import timedelta
from utils.data_loader import load_all_data
from utils.data_processor import (
    analyze_offer_performance,
    create_customer_segments,
    preprocess_transaction_events,
    preprocess_offer_events
)
from utils.visualizations import (
    plot_success_rate_by_offer_type,
    plot_channel_effectiveness
)
from utils.pdf_generator import generate_offer_performance_pdf
from st_aggrid import AgGrid, GridOptionsBuilder

@st.cache_data
def get_preprocessed_data():
    offer_events, transaction_events = load_all_data()
    offer_events = preprocess_offer_events(offer_events)
    transaction_events = preprocess_transaction_events(transaction_events)
    return offer_events, transaction_events

@st.cache_data
def generate_insights(offer_events, transaction_events):
    rfm_data = create_customer_segments(offer_events, transaction_events)
    offer_events_with_cluster = offer_events.merge(rfm_data[['cluster']], left_on='customer_id', right_index=True, how='left')

    success_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean().sort_values(ascending=False)
    top_offer_type = success_rate.idxmax()

    conversion_by_segment = offer_events_with_cluster.groupby('cluster')['offer_success'].mean().sort_values(ascending=False)
    top_segment = conversion_by_segment.idxmax()

    channel_success = offer_events_with_cluster.explode('channels').groupby('channels')['offer_success'].mean().sort_values(ascending=False)
    top_channel = channel_success.idxmax()

    return top_offer_type, top_segment, top_channel, offer_events_with_cluster

@st.cache_data
def filter_data(offer_events, transaction_events, start_date, end_date, selected_offer_types):
    filtered_offers = offer_events[(offer_events['time'].dt.date.between(start_date, end_date)) &
                                   (offer_events['offer_type'].isin(selected_offer_types))]
    filtered_transactions = transaction_events[transaction_events['time'].dt.date.between(start_date, end_date)]
    return filtered_offers, filtered_transactions

def offer_performance_page():
    st.title("Offer Performance Analysis")

    # Load and preprocess data
    offer_events, transaction_events = get_preprocessed_data()

    # Sidebar for customizations
    st.sidebar.header("⚙️ Filters")
    time_range = st.sidebar.slider("Select Time Range (days)", min_value=1, max_value=30, value=(1, 30))
    selected_offer_types = st.sidebar.multiselect("Select Offer Types", options=offer_events['offer_type'].unique(),
                                                  default=offer_events['offer_type'].unique())

    # Convert time_range to datetime objects
    min_date = offer_events['time'].min().date()
    start_date = min_date + timedelta(days=time_range[0] - 1)
    end_date = min_date + timedelta(days=time_range[1] - 1)

    # Filter data based on time range and selected offer types
    filtered_offers, filtered_transactions = filter_data(offer_events, transaction_events, start_date, end_date, selected_offer_types)

    # Generate dynamic insights
    top_offer_type, top_segment, top_channel, offer_events_with_cluster = generate_insights(filtered_offers, filtered_transactions)

    # Display the insights
    st.header("📊 Key Insights")
    col1, col2, col3 = st.columns(3)
    col1.metric("Top Offer Type", top_offer_type,
                f"{offer_events_with_cluster.groupby('offer_type')['offer_success'].mean()[top_offer_type]:.2%}")
    col2.metric("Best Responding Segment", f"Segment {top_segment}",
                f"{offer_events_with_cluster.groupby('cluster')['offer_success'].mean()[top_segment]:.2%}")
    col3.metric("Most Effective Channel", top_channel,
                f"{offer_events_with_cluster.explode('channels').groupby('channels')['offer_success'].mean()[top_channel]:.2%}")

    # Offer Success Rate by Type
    st.header("📈 Offer Performance Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Success Rate by Offer Type")
        success_rate_chart = plot_success_rate_by_offer_type(offer_events_with_cluster)
        st.altair_chart(success_rate_chart, use_container_width=True)

    with col2:
        st.subheader("Channel Effectiveness")
        channel_chart = plot_channel_effectiveness(offer_events_with_cluster)
        st.altair_chart(channel_chart, use_container_width=True)

    # Display filtered data with AgGrid
    st.header("🔍 Detailed Data View")
    # Update the 'time' column in offer_events_with_cluster to show hours only
    offer_events_with_cluster['time'] = offer_events_with_cluster['time'].dt.hour

    gb = GridOptionsBuilder.from_dataframe(offer_events_with_cluster)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
    gridOptions = gb.build()
    AgGrid(offer_events_with_cluster, gridOptions=gridOptions, theme="streamlit", height=400,
           enable_enterprise_modules=True)

    # Export options
    st.sidebar.header("📤 Export Options")
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

if __name__ == "__main__":
    offer_performance_page()