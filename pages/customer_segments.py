# pages/customer_segments.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_processor import create_customer_segments
from utils.visualizations import plot_customer_segments_interactive
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(executive_summary):
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(pdf_file.name, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create the PDF content
    content = []
    content.append(Paragraph("Executive Summary", styles['Title']))
    content.append(Spacer(1, 12))
    for key, value in executive_summary.items():
        content.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
        content.append(Spacer(1, 6))

    # Build the PDF
    doc.build(content)
    return pdf_file.name


def generate_csv(dataframe):
    # Generate a CSV file from a DataFrame
    csv_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    dataframe.to_csv(csv_file.name, index=False)
    return csv_file.name


def download_report(executive_summary, report_type='PDF'):
    if report_type == 'PDF':
        pdf_path = generate_pdf(executive_summary)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Download Executive Summary as PDF",
                data=pdf_file,
                file_name="Executive_Summary.pdf",
                mime="application/pdf"
            )
        os.remove(pdf_path)
    elif report_type == 'CSV':
        summary_df = pd.DataFrame([executive_summary])
        csv_path = generate_csv(summary_df)
        with open(csv_path, "rb") as csv_file:
            st.download_button(
                label="Download Executive Summary as CSV",
                data=csv_file,
                file_name="Executive_Summary.csv",
                mime="text/csv"
            )
        os.remove(csv_path)


def customer_segments_page(offer_events, transaction_events):
    st.title("Customer Segmentation Analysis")

    # Sidebar for filters
    st.sidebar.header("Filters")
    min_transaction_amount = st.sidebar.slider("Min Transaction Amount", 0, int(transaction_events['amount'].max()), 0)
    max_transaction_amount = st.sidebar.slider("Max Transaction Amount", 0, int(transaction_events['amount'].max()),
                                               int(transaction_events['amount'].max()))
    selected_offer_types = st.sidebar.multiselect("Select Offer Types", options=offer_events['offer_type'].unique(),
                                                  default=offer_events['offer_type'].unique())

    # Filter data
    filtered_transactions = transaction_events[(transaction_events['amount'] >= min_transaction_amount) &
                                               (transaction_events['amount'] <= max_transaction_amount)]
    filtered_offers = offer_events[offer_events['offer_type'].isin(selected_offer_types)]

    # Create customer segments
    rfm_data = create_customer_segments(filtered_offers, filtered_transactions)

    # Plot customer segments
    fig_segments = plot_customer_segments_interactive(rfm_data)
    st.plotly_chart(fig_segments)

    # Combine datasets
    customer_data = pd.merge(offer_events, transaction_events[['customer_id', 'total_spend']], on='customer_id', how='left')
    customer_data = customer_data.drop_duplicates(subset='customer_id')

    if customer_data.empty:
        st.error("No data available to display.")
        return

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

    if filtered_data.empty:
        st.error("No data available for the selected filters.")
        return

    # Demographic Analysis
    st.header("Demographic Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Age Distribution")
        fig_age = px.histogram(filtered_data, x='age', nbins=20, color_discrete_sequence=['#1f77b4'])
        fig_age.update_layout(bargap=0.1)
        st.plotly_chart(fig_age)

    with col2:
        st.subheader("Income Distribution")
        fig_income = px.box(filtered_data, y='income', color='gender', color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
        st.plotly_chart(fig_income)

    # RFM Analysis
    st.header("RFM (Recency, Frequency, Monetary) Analysis")
    rfm_data = create_customer_segments(offer_events, transaction_events)

    if rfm_data.empty:
        st.error("No RFM data available.")
        return

    # Display RFM metrics
    st.write("RFM Metrics Summary:")
    st.write(rfm_data.describe())

    # Cluster Analysis
    st.header("Cluster Analysis of Customer Behavior")
    fig_clusters = plot_customer_segments_interactive(rfm_data)
    st.plotly_chart(fig_clusters)

    # Segment Profiles
    st.header("Customer Segment Profiles")
    segment_profiles = rfm_data.groupby('cluster').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean'
    }).round(2)
    st.write(segment_profiles)

    # Segment Size
    st.subheader("Segment Size Distribution")
    segment_size = rfm_data['cluster'].value_counts().sort_index()
    fig_segment_size = px.bar(x=segment_size.index, y=segment_size.values, labels={'x': 'Segment', 'y': 'Count'})
    fig_segment_size.update_layout(xaxis_title="Segment", yaxis_title="Number of Customers")
    st.plotly_chart(fig_segment_size)

    # Interactive Segment Explorer
    st.header("Interactive Segment Explorer")
    selected_segment = st.selectbox("Select a segment to explore", rfm_data['cluster'].unique())
    segment_data = filtered_data[filtered_data['customer_id'].isin(rfm_data[rfm_data['cluster'] == selected_segment].index)]

    if segment_data.empty:
        st.error(f"No data available for the selected segment ({selected_segment}).")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Age Distribution in Segment")
        fig_segment_age = px.histogram(segment_data, x='age', nbins=20, color_discrete_sequence=['#1f77b4'])
        fig_segment_age.update_layout(bargap=0.1)
        st.plotly_chart(fig_segment_age)

    with col2:
        st.subheader("Income Distribution in Segment")
        fig_segment_income = px.box(segment_data, y='income', color='gender', color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
        st.plotly_chart(fig_segment_income)

    # Offer Response by Segment
    st.subheader("Offer Response by Segment")
    offer_response = segment_data.groupby('offer_type')['offer_success'].mean().reset_index()
    fig_offer_response = px.bar(offer_response, x='offer_type', y='offer_success',
                                title=f"Offer Success Rate for Segment {selected_segment}",
                                labels={'offer_success': 'Success Rate', 'offer_type': 'Offer Type'},
                                color_discrete_sequence=['#1f77b4'])
    fig_offer_response.update_layout(xaxis_title="Offer Type", yaxis_title="Success Rate")
    st.plotly_chart(fig_offer_response)

    # Export options
    st.sidebar.header("Export Options")
    if st.sidebar.button("Export Filtered Data"):
        filtered_data.to_csv('filtered_data.csv', index=False)
        st.sidebar.success("Filtered data exported successfully.")

    if st.sidebar.button("Export Offer Response"):
        offer_response.to_csv('offer_response.csv', index=False)
        st.sidebar.success("Offer response data exported successfully.")

    # Download Executive Summary
    st.sidebar.header("Download Executive Summary")
    executive_summary = {
        'Segment': 'High-Value Customers',
        'Key Findings': 'Respond well to BOGO and discount offers.',
        'Recommendations': 'Increase the number of high-reward offers targeted at this segment.'
    }
    report_type = st.sidebar.radio("Choose report type:", ('PDF', 'CSV'))
    download_report(executive_summary, report_type)
