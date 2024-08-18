# utils/pdf_generator.py
import pandas as pd
import plotly.io as pio
from pygments.lexers import go
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

def generate_offer_performance_pdf(insights):
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
        ["Metric", "Value"],
        ["Top Offer Type", f"{insights['top_offer_type']} ({insights['top_offer_type_rate']:.2%})"],
        ["Best Responding Segment", f"Segment {insights['top_segment']} ({insights['top_segment_rate']:.2%})"],
        ["Most Effective Channel", f"{insights['top_channel']} ({insights['top_channel_rate']:.2%})"],
        ["Total Revenue", f"${insights['total_revenue']:,.2f}"],
        ["Average Transaction Value", f"${insights['avg_transaction_value']:.2f}"],
        ["Total Offers", f"{insights['total_offers']:,}"],
        ["Offer Completion Rate", f"{insights['offer_completion_rate']:.2%}"]
    ]
    insights_table = Table(insights_data)
    insights_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(insights_table)
    elements.append(Spacer(1, 12))

    # Additional Analysis
    elements.append(Paragraph("Additional Analysis", styles['Heading2']))
    elements.append(Paragraph(f"1. Offer Type Performance: The {insights['top_offer_type']} offer type shows the highest success rate at {insights['top_offer_type_rate']:.2%}.", styles['BodyText']))
    elements.append(Paragraph(f"2. Customer Segmentation: Segment {insights['top_segment']} shows the highest response rate to offers at {insights['top_segment_rate']:.2%}.", styles['BodyText']))
    elements.append(Paragraph(f"3. Channel Optimization: The {insights['top_channel']} channel is the most effective for offer distribution with a success rate of {insights['top_channel_rate']:.2%}.", styles['BodyText']))
    elements.append(Paragraph(f"4. Overall Performance: The campaign achieved a total revenue of ${insights['total_revenue']:,.2f} with an average transaction value of ${insights['avg_transaction_value']:.2f}. The overall offer completion rate was {insights['offer_completion_rate']:.2%}.", styles['BodyText']))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_customer_segments_pdf(rfm_data, segment_data, filtered_offers):
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

    # Segment Summary
    elements.append(Paragraph("Segment Summary", styles['Heading2']))
    segment_summary = rfm_data.groupby('cluster').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean'
    }).reset_index()
    segment_summary_data = [['Segment', 'Avg. Recency', 'Avg. Frequency', 'Avg. Monetary']] + \
                           segment_summary.values.tolist()
    segment_summary_table = Table(segment_summary_data)
    segment_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(segment_summary_table)
    elements.append(Spacer(1, 12))

    # Demographic Summary
    elements.append(Paragraph("Demographic Summary", styles['Heading2']))
    age_summary = filtered_offers['age'].describe().reset_index()
    age_summary_data = age_summary.values.tolist()
    age_summary_table = Table(age_summary_data)
    age_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(age_summary_table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf