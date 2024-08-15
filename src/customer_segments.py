# src/customer_segments.py
import streamlit as st
from utils.data_loader import load_all_data
from utils.data_processor import (
    create_customer_segments,
    preprocess_offer_data,
    preprocess_transaction_data
)
from utils.visualizations import (
    plot_age_distribution,
    plot_income_distribution,
    plot_rfm_clusters,
    plot_segment_distribution
)
from utils.pdf_generator import generate_customer_segments_pdf
from st_aggrid import AgGrid, GridOptionsBuilder


@st.cache_data
def get_filtered_data(offer_events, transaction_events, selected_offer_types, min_amount, max_amount):
    filtered_offers = preprocess_offer_data(offer_events, selected_offer_types)
    filtered_transactions = preprocess_transaction_data(transaction_events, min_amount, max_amount)
    rfm_data = create_customer_segments(filtered_offers, filtered_transactions)
    return filtered_offers, filtered_transactions, rfm_data

def customer_segments_page():
    st.markdown('<h1 class="title">Customer Segmentation Analysis</h1>', unsafe_allow_html=True)

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
        /* Sidebar Styling */
        .sidebar .sidebar-content {
            background-color: #f9f5f0;
            padding: 1.5rem;
            border-radius: 10px;
        }
        .sidebar h2 {
            color: #3e2a1e; /* Deep Coffee */
        }
        /* Metric Card Styling */
        .metric-card {
            background-color: #f9f5f0; /* Ivory */
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-align: center;
            cursor: pointer;
            transform-origin: center;
        }
        .metric-card:hover {
            transform: scale(1.1);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #3e2a1e; /* Deep Coffee */
            margin-bottom: 0.5rem;
        }
        .metric-label {
            font-size: 1.1rem;
            color: #3e2a1e; /* Deep Coffee */
            margin-top: 0.5rem;
        }
        /* AgGrid Table Styling */
        .ag-theme-streamlit {
            --ag-row-hover-color: #f0e6db;
            --ag-alpine-border-color: #3e2a1e;
            --ag-header-foreground-color: #3e2a1e;
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

    # Load Data
    offer_events, transaction_events = load_all_data()

    # Sidebar filters
    st.sidebar.header("⚙️ Filters")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    min_amount, max_amount = st.sidebar.slider("Transaction Amount Range ($)", 0,
                                               int(transaction_events['amount'].max()),
                                               (0, int(transaction_events['amount'].max())))
    selected_offer_types = st.sidebar.multiselect("Offer Types", offer_events['offer_type'].unique(),
                                                  default=offer_events['offer_type'].unique())
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Get filtered data
    filtered_offers, filtered_transactions, rfm_data = get_filtered_data(
        offer_events, transaction_events, selected_offer_types, min_amount, max_amount
    )

    # Display key metrics
    #st.markdown('<h2 class="header">📊 Key Metrics</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f'{len(rfm_data)}' +
                    '</div><div class="metric-label">Total Customers</div></div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f'{rfm_data["recency"].mean():.1f} days' +
                    '</div><div class="metric-label">Average Recency</div></div>',
                    unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f'{rfm_data["frequency"].mean():.1f}' +
                    '</div><div class="metric-label">Average Frequency</div></div>',
                    unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f'${rfm_data["monetary"].mean():.2f}' +
                    '</div><div class="metric-label">Average Monetary Value</div></div>',
                    unsafe_allow_html=True)

    # RFM Cluster Visualization
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    #st.markdown('<h2 class="header">🎯 Customer Segments</h2>', unsafe_allow_html=True)
    rfm_chart = plot_rfm_clusters(rfm_data)
    st.altair_chart(rfm_chart, use_container_width=True)

    # Segment Explorer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h3 class="header">🔍 Interactive Segment Explorer</h3>', unsafe_allow_html=True)
    selected_cluster = st.selectbox("Select a Segment", rfm_data['cluster'].unique())
    segment_data = rfm_data[rfm_data['cluster'] == selected_cluster]

    if segment_data.empty:
        st.warning("No data available for the selected segment.")
    else:
        st.write(f"Exploring Segment: {selected_cluster}")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown('<div class="metric-card"><div class="metric-value">' +
                        f'{len(segment_data)}' +
                        '</div><div class="metric-label">Segment Size</div></div>',
                        unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card"><div class="metric-value">' +
                        f'${segment_data["monetary"].mean():.2f}' +
                        '</div><div class="metric-label">Avg. Monetary Value</div></div>',
                        unsafe_allow_html=True)

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

    # Demographic Insights
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    #st.markdown('<h2 class="header">👥 Demographic Insights</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        age_chart = plot_age_distribution(filtered_offers)
        st.altair_chart(age_chart, use_container_width=True)

    with col2:
        income_chart = plot_income_distribution(filtered_offers)
        st.altair_chart(income_chart, use_container_width=True)

    # Export options in the sidebar
    st.sidebar.header("📤 Export Options")
    if st.sidebar.button("Generate PDF Report"):
        pdf_buffer = generate_customer_segments_pdf(
            rfm_data,
            segment_data,
            filtered_offers
        )
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="customer_segments_report.pdf",
            mime="application/pdf"
        )


if __name__ == "__main__":
    customer_segments_page()
