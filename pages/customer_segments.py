# pages/customer_segments.py
import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder
from utils.data_processor import create_customer_segments
from utils.data_loader import load_all_data
from utils.pdf_generator import generate_customer_segments_pdf

def preprocess_offer_data(offer_events, selected_offer_types):
    return offer_events.query("offer_type in @selected_offer_types")

def preprocess_transaction_data(transaction_events, min_amount, max_amount):
    return transaction_events.query("amount >= @min_amount and amount <= @max_amount")

def plot_age_distribution(filtered_data):
    return alt.Chart(filtered_data).mark_bar().encode(
        x=alt.X('age:Q', bin=alt.Bin(maxbins=20), title='Age'),
        y=alt.Y('count()', title='Number of Customers'),
        color=alt.value('#3d2c1f')
    ).properties(title='Age Distribution')

def plot_income_distribution(filtered_data):
    return alt.Chart(filtered_data).mark_boxplot(size=50).encode(
        y=alt.Y('income:Q', title='Income'),
        x=alt.X('gender:N', title='Gender'),
        color=alt.Color('gender:N', scale=alt.Scale(scheme='viridis'))
    ).properties(title='Income Distribution by Gender')

def plot_rfm_clusters(rfm_data):
    return alt.Chart(rfm_data).mark_circle(size=60).encode(
        x=alt.X('recency:Q', title='Recency (days)'),
        y=alt.Y('frequency:Q', title='Frequency (transactions)'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='category10'), title='Customer Segment'),
        size=alt.Size('monetary:Q', title='Monetary Value'),
        tooltip=['recency', 'frequency', 'monetary', 'cluster']
    ).properties(title='RFM Clusters')

def customer_segments_page():
    st.title("Customer Segmentation Dashboard")

    # Load Data
    offer_events, transaction_events = load_all_data()

    # Sidebar filters
    st.sidebar.header("⚙️ Filters")
    min_amount, max_amount = st.sidebar.slider("Transaction Amount Range ($)", 0, int(transaction_events['amount'].max()), (0, int(transaction_events['amount'].max())))
    selected_offer_types = st.sidebar.multiselect("Offer Types", offer_events['offer_type'].unique(), default=offer_events['offer_type'].unique())

    # Filter data
    filtered_transactions = preprocess_transaction_data(transaction_events, min_amount, max_amount)

    # Create customer segments
    rfm_data = create_customer_segments(preprocess_offer_data(offer_events, selected_offer_types), filtered_transactions)

    # Display key metrics
    st.header("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", len(rfm_data))
    col2.metric("Average Recency (days)", f"{rfm_data['recency'].mean():.1f}")
    col3.metric("Average Frequency", f"{rfm_data['frequency'].mean():.1f}")
    col4.metric("Average Monetary Value", f"${rfm_data['monetary'].mean():.2f}")

    # RFM Cluster Visualization
    st.header("🎯 Customer Segments")
    rfm_chart = plot_rfm_clusters(rfm_data)
    st.altair_chart(rfm_chart, use_container_width=True)

    # Segment Explorer
    st.subheader("🔍 Interactive Segment Explorer")
    selected_cluster = st.selectbox("Select a Segment", rfm_data['cluster'].unique())
    segment_data = rfm_data[rfm_data['cluster'] == selected_cluster]

    if segment_data.empty:
        st.warning("No data available for the selected segment.")
    else:
        st.write(f"Exploring Segment: {selected_cluster}")
        col1, col2 = st.columns(2)
        col1.metric("Segment Size", len(segment_data))
        col2.metric("Avg. Monetary Value", f"${segment_data['monetary'].mean():.2f}")

        gb = GridOptionsBuilder.from_dataframe(segment_data)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
        gridOptions = gb.build()
        AgGrid(segment_data, gridOptions=gridOptions, theme="streamlit", height=300, enable_enterprise_modules=True)

    # Demographic Insights
    st.header("👥 Demographic Insights")
    col1, col2 = st.columns(2)

    with col1:
        age_chart = plot_age_distribution(preprocess_offer_data(offer_events, selected_offer_types))
        st.altair_chart(age_chart, use_container_width=True)

    with col2:
        income_chart = plot_income_distribution(preprocess_offer_data(offer_events, selected_offer_types))
        st.altair_chart(income_chart, use_container_width=True)

    # Export options
    st.sidebar.header("📤 Export Options")
    if st.sidebar.button("Generate PDF Report"):
        pdf_buffer = generate_customer_segments_pdf(
            rfm_data, segment_data, preprocess_offer_data(offer_events, selected_offer_types),
            plot_rfm_clusters(rfm_data), plot_age_distribution(preprocess_offer_data(offer_events, selected_offer_types)),
            plot_income_distribution(preprocess_offer_data(offer_events, selected_offer_types))
        )
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="customer_segments_report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    customer_segments_page()
