# pages/offer_performance.py
import streamlit as st
import plotly.express as px
from datetime import timedelta
import pandas as pd
from utils.data_processor import analyze_offer_performance, create_customer_segments
from utils.visualizations import plot_offer_performance, plot_channel_effectiveness
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def generate_insights(offer_events, transaction_events):
    # Create customer segments
    rfm_data = create_customer_segments(offer_events, transaction_events)

    # Merge cluster information with offer_events
    offer_events_with_cluster = offer_events.merge(rfm_data[['cluster']], left_on='customer_id', right_index=True, how='left')

    # Calculate success rates
    success_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean().sort_values(ascending=False)
    top_offer_type = success_rate.idxmax()

    conversion_by_segment = offer_events_with_cluster.groupby('cluster')['offer_success'].mean().sort_values(ascending=False)
    top_segment = conversion_by_segment.idxmax()

    channel_success = offer_events_with_cluster.explode('channels').groupby('channels')['offer_success'].mean().sort_values(ascending=False)
    top_channel = channel_success.idxmax()

    return top_offer_type, top_segment, top_channel, offer_events_with_cluster

def export_to_csv(dataframe, filename):
    csv = dataframe.to_csv(index=False)
    st.download_button(
        label=f"Download {filename}",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

def export_to_pdf(dataframe, title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Add title
    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    # Convert dataframe to a list of lists
    data = [dataframe.columns.tolist()] + dataframe.values.tolist()

    # Create the table
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)

    # Build the PDF
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    st.download_button(
        label=f"Download {title}.pdf",
        data=pdf,
        file_name=f"{title}.pdf",
        mime='application/pdf'
    )

def offer_performance_page(offer_events, transaction_events):
    st.title("Offer Performance Analysis")

    # Sidebar for customizations
    st.sidebar.header("Visualization Settings")
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart"])
    time_range = st.sidebar.slider("Select Time Range (days)", min_value=1, max_value=30, value=(1, 30))
    selected_offer_types = st.sidebar.multiselect("Select Offer Types", options=offer_events['offer_type'].unique(), default=offer_events['offer_type'].unique())

    # Convert time_range to datetime objects
    min_date = offer_events['time'].min().date()
    start_date = min_date + timedelta(days=time_range[0] - 1)
    end_date = min_date + timedelta(days=time_range[1] - 1)

    # Filter data based on time range and selected offer types
    filtered_offers = offer_events[(offer_events['time'].dt.date.between(start_date, end_date)) &
                                   (offer_events['offer_type'].isin(selected_offer_types))]
    filtered_transactions = transaction_events[transaction_events['time'].dt.date.between(start_date, end_date)]

    # Generate dynamic insights
    top_offer_type, top_segment, top_channel, offer_events_with_cluster = generate_insights(filtered_offers, filtered_transactions)

    # Display the insights
    st.subheader("Key Insights")
    st.write(f"1. The most successful offer type is **{top_offer_type}** with a conversion rate of **{offer_events_with_cluster.groupby('offer_type')['offer_success'].mean()[top_offer_type]:.2%}**.")
    st.write(f"2. Customer segment **{top_segment}** responds best to offers, with a conversion rate of **{offer_events_with_cluster.groupby('cluster')['offer_success'].mean()[top_segment]:.2%}**.")
    st.write(f"3. The most effective channel for offer distribution is **{top_channel}**, with a success rate of **{offer_events_with_cluster.explode('channels').groupby('channels')['offer_success'].mean()[top_channel]:.2%}**.")

    # Generate and display selected chart type
    if chart_type == "Bar Chart":
        success_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean().sort_values(ascending=False)
        fig = px.bar(x=success_rate.index, y=success_rate.values, title="Offer Success Rate by Type")
        fig.update_layout(xaxis_title="Offer Type", yaxis_title="Success Rate")

        # Drill-down by clicking on the chart
        st.write("Click on a bar to see details.")
        st.plotly_chart(fig, use_container_width=True)

        if 'selected_points' in st.session_state and st.session_state['selected_points']:
            selected_offer_type = st.session_state['selected_points']['points'][0]['x']
            st.write(f"Details for **{selected_offer_type}**:")
            st.write(offer_events_with_cluster[offer_events_with_cluster['offer_type'] == selected_offer_type])

    elif chart_type == "Pie Chart":
        offer_type_counts = offer_events_with_cluster['offer_type'].value_counts()
        fig = px.pie(values=offer_type_counts.values, names=offer_type_counts.index, title="Distribution of Offer Types")
        st.plotly_chart(fig)

    # Conversion Rates by Offer Type and Customer Segment
    st.header("Conversion Rates by Offer Type and Customer Segment")
    performance_df = analyze_offer_performance(offer_events_with_cluster)
    fig_performance = plot_offer_performance(performance_df)
    st.plotly_chart(fig_performance)

    # Channel Effectiveness Analysis
    st.header("Channel Effectiveness Analysis")
    fig_channel = plot_channel_effectiveness(offer_events_with_cluster)
    st.plotly_chart(fig_channel)

    # Average Spend by Offer Type
    st.header("Average Spend by Offer Type")
    offer_transactions = pd.merge(
        filtered_offers[filtered_offers['event'] == 'offer completed'],
        filtered_transactions[['customer_id', 'time', 'amount']],
        on=['customer_id', 'time'],
        how='inner'
    )

    avg_spend = offer_transactions.groupby('offer_type')['amount'].mean().sort_values(ascending=False)

    if not avg_spend.empty:
        fig_avg_spend = px.bar(x=avg_spend.index, y=avg_spend.values, title="Average Transaction Amount by Offer Type")
        fig_avg_spend.update_layout(xaxis_title="Offer Type", yaxis_title="Average Transaction Amount")
        st.plotly_chart(fig_avg_spend)
    else:
        st.write("No data available for average spend by offer type in the selected time range.")

    # Export options
    st.sidebar.header("Export Options")

    if st.sidebar.button("Export Insights to CSV"):
        insights_df = pd.DataFrame({
            "Metric": ["Top Offer Type", "Top Segment", "Top Channel"],
            "Value": [top_offer_type, top_segment, top_channel],
            "Success Rate": [
                f"{offer_events_with_cluster.groupby('offer_type')['offer_success'].mean()[top_offer_type]:.2%}",
                f"{offer_events_with_cluster.groupby('cluster')['offer_success'].mean()[top_segment]:.2%}",
                f"{offer_events_with_cluster.explode('channels').groupby('channels')['offer_success'].mean()[top_channel]:.2%}"
            ]
        })
        export_to_csv(insights_df, "insights_summary.csv")
        st.sidebar.success("CSV exported successfully!")

    if st.sidebar.button("Export Insights to PDF"):
        insights_df = pd.DataFrame({
            "Metric": ["Top Offer Type", "Top Segment", "Top Channel"],
            "Value": [top_offer_type, top_segment, top_channel],
            "Success Rate": [
                f"{offer_events_with_cluster.groupby('offer_type')['offer_success'].mean()[top_offer_type]:.2%}",
                f"{offer_events_with_cluster.groupby('cluster')['offer_success'].mean()[top_segment]:.2%}",
                f"{offer_events_with_cluster.explode('channels').groupby('channels')['offer_success'].mean()[top_channel]:.2%}"
            ]
        })
        export_to_pdf(insights_df, "Offer Performance Insights Summary")
        st.sidebar.success("PDF exported successfully!")
