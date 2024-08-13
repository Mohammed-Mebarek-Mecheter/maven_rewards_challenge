# utils/pdf_generator.py
import pandas as pd
import plotly.io as pio
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import tempfile

def generate_pdf_report(filtered_transactions, basket_data, clv_data, cluster_stats):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Transaction Analysis Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Transaction Overview
    elements.append(Paragraph("Transaction Overview", styles['Heading2']))
    overview_data = [
        ["Total Transactions", f"{len(filtered_transactions):,}"],
        ["Total Revenue", f"${filtered_transactions['amount'].sum():,.2f}"],
        ["Average Transaction Value", f"${filtered_transactions['amount'].mean():.2f}"]
    ]
    overview_table = Table(overview_data)
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 12))

    # Customer Segments
    elements.append(Paragraph("Customer Segments", styles['Heading2']))
    segment_data = [cluster_stats.reset_index().columns.tolist()] + cluster_stats.reset_index().values.tolist()
    segment_table = Table(segment_data)
    segment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(segment_table)
    elements.append(Spacer(1, 12))

    # Top Customers by CLV
    elements.append(Paragraph("Top Customers by CLV", styles['Heading2']))
    top_customers = clv_data.sort_values(by='total_spend', ascending=False).head(10)
    top_customers_data = [top_customers.columns.tolist()] + top_customers.values.tolist()
    top_customers_table = Table(top_customers_data)
    top_customers_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(top_customers_table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_offer_performance_pdf(top_offer_type, top_segment, top_channel,
                                   offer_events_with_cluster, performance_df,
                                   success_rate_chart, channel_chart, performance_chart):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Offer Performance Analysis Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Key Insights
    elements.append(Paragraph("Key Insights", styles['Heading2']))
    insights_data = [
        ["Top Offer Type", top_offer_type, f"{offer_events_with_cluster.groupby('offer_type')['offer_success'].mean()[top_offer_type]:.2%}"],
        ["Best Responding Segment", f"Segment {top_segment}", f"{offer_events_with_cluster.groupby('cluster')['offer_success'].mean()[top_segment]:.2%}"],
        ["Most Effective Channel", top_channel, f"{offer_events_with_cluster.explode('channels').groupby('channels')['offer_success'].mean()[top_channel]:.2%}"]
    ]
    insights_table = Table(insights_data)
    insights_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(insights_table)
    elements.append(Spacer(1, 12))

    # Charts
    for title, chart in [("Offer Success Rate by Type", success_rate_chart),
                         ("Channel Effectiveness", channel_chart),
                         ("Offer Performance by Customer Segment", performance_chart)]:
        elements.append(Paragraph(title, styles['Heading2']))
        elements.append(Spacer(1, 12))
        img = tempfile.NamedTemporaryFile(suffix=".png")
        chart.save(img.name)
        elements.append(Image(img.name, width=400, height=200))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_customer_segments_pdf(rfm_data, segment_data, filtered_offers,
                                   rfm_chart, age_chart, income_chart, offer_response_chart, cohort_chart):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Customer Segmentation Analysis Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Key Metrics
    elements.append(Paragraph("Key Metrics", styles['Heading2']))
    metrics_data = [
        ["Total Customers", f"{len(rfm_data)}"],
        ["Average Recency (days)", f"{rfm_data['recency'].mean():.1f}"],
        ["Average Frequency", f"{rfm_data['frequency'].mean():.1f}"],
        ["Average Monetary Value", f"${rfm_data['monetary'].mean():.2f}"]
    ]
    metrics_table = Table(metrics_data)
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 12))

    # Charts
    for title, chart in [
        ("Customer Segments (RFM Analysis)", rfm_chart),
        ("Age Distribution", age_chart),
        ("Income Distribution by Gender", income_chart),
        ("Offer Success Rate by Customer Segment", offer_response_chart),
        ("Cohort Analysis by Customer Segment", cohort_chart)
    ]:
        elements.append(Paragraph(title, styles['Heading2']))
        elements.append(Spacer(1, 12))
        img = tempfile.NamedTemporaryFile(suffix=".png")
        chart.save(img.name)
        elements.append(Image(img.name, width=400, height=200))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf