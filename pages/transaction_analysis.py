# pages/transaction_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from utils.visualizations import plot_transaction_time_series
from utils.data_processor import preprocess_transaction_events, analyze_customer_lifetime_value

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

    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    data = [dataframe.columns.tolist()] + dataframe.values.tolist()
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    st.download_button(
        label=f"Download {title}.pdf",
        data=pdf,
        file_name=f"{title}.pdf",
        mime='application/pdf'
    )

def transaction_analysis_page(offer_events, transaction_events):
    st.title("Transaction Analysis")

    # Sidebar for filters
    st.sidebar.header("Filters")
    min_transaction_amount = st.sidebar.slider("Min Transaction Amount", 0, int(transaction_events['amount'].max()), 0)
    max_transaction_amount = st.sidebar.slider("Max Transaction Amount", 0, int(transaction_events['amount'].max()), int(transaction_events['amount'].max()))
    min_transaction_frequency = st.sidebar.slider("Min Transaction Frequency", 0, int(transaction_events['customer_id'].value_counts().max()), 0)
    max_transaction_frequency = st.sidebar.slider("Max Transaction Frequency", 0, int(transaction_events['customer_id'].value_counts().max()), int(transaction_events['customer_id'].value_counts().max()))

    # Preprocess transaction events
    transaction_events = preprocess_transaction_events(transaction_events)

    # Filter data
    filtered_transactions = transaction_events[(transaction_events['amount'] >= min_transaction_amount) &
                                               (transaction_events['amount'] <= max_transaction_amount)]
    transaction_counts = filtered_transactions['customer_id'].value_counts()
    filtered_customers = transaction_counts[(transaction_counts >= min_transaction_frequency) &
                                            (transaction_counts <= max_transaction_frequency)].index
    filtered_transactions = filtered_transactions[filtered_transactions['customer_id'].isin(filtered_customers)]

    # Time series analysis of transactions
    st.header("Time Series Analysis of Transactions")
    fig_time_series = plot_transaction_time_series(filtered_transactions)
    st.plotly_chart(fig_time_series)

    # Weekly trend
    weekly_transactions = filtered_transactions.set_index('time').resample('W')['amount'].sum().reset_index()
    fig_weekly = px.line(weekly_transactions, x='time', y='amount', title='Weekly Transaction Trend')
    st.plotly_chart(fig_weekly)

    # Basket Analysis
    st.header("Basket Analysis")
    transaction_counts = filtered_transactions.groupby('customer_id').size().reset_index(name='transaction_count')
    transaction_amounts = filtered_transactions.groupby('customer_id')['amount'].sum().reset_index()
    basket_data = pd.merge(transaction_counts, transaction_amounts, on='customer_id')
    basket_data['avg_basket_size'] = basket_data['amount'] / basket_data['transaction_count']

    # Cluster customers based on transaction count and average basket size
    kmeans = KMeans(n_clusters=4, random_state=42)
    basket_data['cluster'] = kmeans.fit_predict(basket_data[['transaction_count', 'avg_basket_size']])

    fig_basket = px.scatter(basket_data, x='transaction_count', y='avg_basket_size', color='cluster',
                            title='Customer Segments based on Transaction Behavior',
                            labels={'transaction_count': 'Number of Transactions',
                                    'avg_basket_size': 'Average Basket Size ($)'},
                            color_discrete_sequence=px.colors.qualitative.Set1)
    st.plotly_chart(fig_basket)

    # Display cluster characteristics
    st.subheader("Cluster Characteristics:")
    cluster_stats = basket_data.groupby('cluster')[['transaction_count', 'avg_basket_size']].mean().round(2)
    st.write(cluster_stats)

    # Customer Lifetime Value (CLV) Analysis
    st.header("Customer Lifetime Value (CLV) Analysis")

    # Calculate CLV
    clv_data = analyze_customer_lifetime_value(filtered_transactions)

    # Display CLV distribution
    if not clv_data.empty:
        fig_clv = px.histogram(clv_data, x='total_spend', nbins=30, title='Distribution of Customer Lifetime Value')
        fig_clv.update_layout(xaxis_title="Total Spend ($)", yaxis_title="Frequency")
        st.plotly_chart(fig_clv)
    else:
        st.write("No data available for CLV analysis in the selected filters.")

    # Display top customers by CLV
    st.subheader("Top Customers by CLV")
    top_customers = clv_data.sort_values(by='total_spend', ascending=False).head(10)
    if 'customer_id' in top_customers.columns:
        st.write(top_customers[['customer_id', 'total_spend', 'annual_value']])
    else:
        st.write(top_customers)  # Just display the DataFrame if 'customer_id' is not available

    # Export options
    st.sidebar.header("Export Options")
    if st.sidebar.button("Export Transaction Data to CSV"):
        export_to_csv(filtered_transactions, "filtered_transactions.csv")

    if st.sidebar.button("Export Basket Data to CSV"):
        export_to_csv(basket_data, "basket_data.csv")

    if st.sidebar.button("Export CLV Data to CSV"):
        export_to_csv(clv_data, "clv_data.csv")

    if st.sidebar.button("Export Cluster Characteristics to PDF"):
        export_to_pdf(cluster_stats.reset_index(), "Cluster Characteristics")

    if st.sidebar.button("Export Top Customers by CLV to PDF"):
        export_to_pdf(top_customers[['customer_id', 'total_spend', 'annual_value']] if 'customer_id' in top_customers.columns else top_customers, "Top Customers by CLV")
