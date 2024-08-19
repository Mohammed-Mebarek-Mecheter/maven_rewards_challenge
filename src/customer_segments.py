# src/customer_segments.py
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid

from utils.data_loader import load_all_data
from utils.data_processor import (
    preprocess_offer_data,
    preprocess_transaction_data,
    calculate_advanced_metrics, create_basket_data
)
from utils.model_handler import apply_customer_segmentation
from utils.visualizations import (
    plot_rfm_clusters,
    plot_segment_distribution,
    plot_customer_segments_interactive,
    plot_segment_characteristics,
    plot_clv_distribution,
    create_correlation_heatmap
)
from utils.pdf_generator import generate_customer_segments_pdf
from utils.styles import load_css


@st.cache_resource
def get_filtered_data(offer_events, transaction_events, selected_offer_types, min_amount, max_amount):
    """Filters and preprocesses the data based on user input."""
    filtered_offers = preprocess_offer_data(offer_events, selected_offer_types)
    filtered_transactions = preprocess_transaction_data(transaction_events, min_amount, max_amount)
    rfm_data = apply_customer_segmentation(filtered_transactions)
    advanced_metrics = calculate_advanced_metrics(rfm_data, filtered_offers)
    basket_data = create_basket_data(filtered_transactions)
    cluster_stats = basket_data.groupby('cluster')[['transaction_count', 'avg_basket_size']].mean().round(2)
    return filtered_offers, filtered_transactions, rfm_data, advanced_metrics, cluster_stats


def display_metric_card(value, label):
    return f'''
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    '''

def customer_segments_page():
    # st.markdown('<h1 class="title">Customer Segmentation Analysis</h1>', unsafe_allow_html=True)

    # Load CSS
    st.markdown(load_css(), unsafe_allow_html=True)

    # Load Data
    offer_events, transaction_events = load_all_data()

    # Sidebar filters
    st.sidebar.header("⚙️ Filters")
    min_amount, max_amount = st.sidebar.slider("Transaction Amount Range ($)", 0,
                                               int(transaction_events['amount'].max()),
                                               (0, int(transaction_events['amount'].max())))
    selected_offer_types = st.sidebar.multiselect("Offer Types", offer_events['offer_type'].unique(),
                                                  default=offer_events['offer_type'].unique())

    # Get filtered data
    filtered_offers, filtered_transactions, rfm_data, advanced_metrics, cluster_stats = get_filtered_data(
        offer_events, transaction_events, selected_offer_types, min_amount, max_amount
    )

    # Display key metrics
    cols = st.columns(4)  # Create 4 columns
    metrics = [
        (f'{len(offer_events["customer_id"].unique()):,}', 'Total Customers'),
        (f'{rfm_data["recency"].mean():.1f} days', 'Average Recency'),
        (f'{rfm_data["frequency"].mean():.1f}', 'Average Frequency'),
        (f'${rfm_data["monetary"].mean():.2f}', 'Average Monetary Value')
    ]
    for col, (value, label) in zip(cols, metrics):
        col.markdown(display_metric_card(value, label), unsafe_allow_html=True)

    # Display advanced metrics
    cols = st.columns(3)  # Create 3 columns for advanced metrics
    advanced_metric_display = [
        ('Customer Lifetime Value', f'${advanced_metrics["clv"]:.2f}'),
        ('Churn Rate', f'{advanced_metrics["churn_rate"]:.2%}'),
        ('Customer Acquisition Cost', f'${advanced_metrics["cac"]:.2f}')
    ]
    for col, (label, value) in zip(cols, advanced_metric_display):
        col.markdown(display_metric_card(value, label), unsafe_allow_html=True)

    # Segment Explorer
    st.markdown('<h3 class="header">Interactive Segment Explorer</h3>', unsafe_allow_html=True)
    selected_cluster = st.selectbox("Select a Segment", rfm_data['cluster'].unique())
    segment_data = rfm_data[rfm_data['cluster'] == selected_cluster]

    if segment_data.empty:
        st.warning("No data available for the selected segment.")
    else:
        st.write(f"Exploring Segment: {selected_cluster}")
        col1, col2 = st.columns(2)
        col1.markdown(display_metric_card(f'{len(segment_data)}', 'Segment Size'), unsafe_allow_html=True)
        col2.markdown(display_metric_card(f'${segment_data["monetary"].mean():.2f}', 'Avg. Monetary Value'),
                      unsafe_allow_html=True)

    # RFM Cluster Visualization
    st.markdown('<h3 class="sub-header">RFM Clusters</h3>', unsafe_allow_html=True)
    view_type = st.radio("Select View", ("2D", "3D"), key="view_type_radio")
    if view_type == "2D":
        st.altair_chart(plot_rfm_clusters(rfm_data), use_container_width=True)
    else:
        st.plotly_chart(plot_customer_segments_interactive(rfm_data), use_container_width=True)

    # AgGrid table
    gb = GridOptionsBuilder.from_dataframe(segment_data)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
    gb.configure_grid_options(
        rowStyle={"color": "#6f4f28", "background-color": "#dcd6c7"},
        headerStyle={"color": "#000", "background-color": "#dcd6c7"},
    )
    gridOptions = gb.build()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        AgGrid(segment_data, gridOptions=gridOptions, theme="streamlit", height=300, enable_enterprise_modules=True)

    # Segment Distribution Chart
    with col2:
        segment_distribution_chart = plot_segment_distribution(rfm_data)
        st.altair_chart(segment_distribution_chart, use_container_width=True)

    # Segment Distribution
    st.markdown('<h3 class="sub-header">Demographics vs RFM Metrics</h3>', unsafe_allow_html=True)
    correlation_heatmap = create_correlation_heatmap(filtered_offers, rfm_data)
    st.altair_chart(correlation_heatmap, use_container_width=True)

    st.markdown('<h3 class="sub-header">Segment Characteristics</h3>', unsafe_allow_html=True)
    st.altair_chart(plot_segment_characteristics(segment_data), use_container_width=True)

    # Export options
    st.sidebar.header("📤 Export Option")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    if st.sidebar.button("Generate PDF Report"):
        pdf_buffer = generate_customer_segments_pdf(rfm_data, segment_data, filtered_offers)
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="customer_segments_report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    customer_segments_page()
