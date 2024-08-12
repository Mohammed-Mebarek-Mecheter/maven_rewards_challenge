# pages/transaction_analysis.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_data
from utils.data_processor import preprocess_transaction_events, preprocess_offer_events
from utils.visualizations import plot_transaction_time_series
from sklearn.cluster import KMeans
from lifetimes import BetaGeoFitter
from lifetimes.utils import summary_data_from_transaction_data

def transaction_analysis_page():
    st.title("Transaction Analysis")

    # Load and preprocess data
    offer_events, transaction_events = load_all_data()
    transaction_events = preprocess_transaction_events(transaction_events)
    offer_events = preprocess_offer_events(offer_events)

    # Time series analysis of transactions
    st.header("Time Series Analysis of Transactions")
    fig_time_series = plot_transaction_time_series(transaction_events)
    st.plotly_chart(fig_time_series)

    # Weekly trend
    weekly_transactions = transaction_events.set_index('time').resample('W')['amount'].sum().reset_index()
    fig_weekly = px.line(weekly_transactions, x='time', y='amount', title='Weekly Transaction Trend')
    st.plotly_chart(fig_weekly)

    # Basket Analysis
    st.header("Basket Analysis")

    # For this example, we'll use a simple approach. In a real scenario, you'd need more detailed transaction data.
    transaction_counts = transaction_events.groupby('customer_id').size().reset_index(name='transaction_count')
    transaction_amounts = transaction_events.groupby('customer_id')['amount'].sum().reset_index()
    basket_data = pd.merge(transaction_counts, transaction_amounts, on='customer_id')
    basket_data['avg_basket_size'] = basket_data['amount'] / basket_data['transaction_count']

    # Cluster customers based on transaction count and average basket size
    kmeans = KMeans(n_clusters=3, random_state=42)
    basket_data['cluster'] = kmeans.fit_predict(basket_data[['transaction_count', 'avg_basket_size']])

    fig_basket = px.scatter(basket_data, x='transaction_count', y='avg_basket_size', color='cluster',
                            title='Customer Segments based on Transaction Behavior')
    st.plotly_chart(fig_basket)

    # Display cluster characteristics
    st.write("Cluster Characteristics:")
    st.write(basket_data.groupby('cluster')[['transaction_count', 'avg_basket_size']].mean())

    # Customer Lifetime Value (CLV) Estimation
    st.header("Customer Lifetime Value (CLV) Estimation")

    # Prepare data for CLV calculation
    summary = summary_data_from_transaction_data(transaction_events, 'customer_id', 'time', 'amount', observation_period_end='2023-12-31')

    # Fit the BG/NBD model
    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(summary['frequency'], summary['recency'], summary['T'])

    # Predict future transactions
    t = 30  # Predict for the next 30 days
    summary['predicted_purchases'] = bgf.conditional_expected_number_of_purchases_up_to_time(t, summary['frequency'], summary['recency'], summary['T'])

    # Calculate CLV (assuming average transaction value remains constant)
    summary['clv'] = summary['predicted_purchases'] * summary['monetary_value']

    # Visualize CLV distribution
    fig_clv = px.histogram(summary, x='clv', nbins=50, title='Distribution of Customer Lifetime Value')
    st.plotly_chart(fig_clv)

    # Display top 10 customers by CLV
    st.write("Top 10 Customers by CLV:")
    st.write(summary.sort_values('clv', ascending=False).head(10))

    # Correlation between offer interactions and transaction behavior
    st.header("Correlation between Offer Interactions and Transaction Behavior")

    # Merge offer and transaction data
    merged_data = pd.merge(offer_events, transaction_events, on=['customer_id', 'time'], how='outer')
    merged_data['offer_received'] = merged_data['event_x'] == 'offer received'
    merged_data['offer_viewed'] = merged_data['event_x'] == 'offer viewed'
    merged_data['offer_completed'] = merged_data['event_x'] == 'offer completed'
    merged_data['transaction'] = merged_data['event_y'] == 'transaction'

    # Calculate correlation
    correlation_data = merged_data.groupby('customer_id').agg({
        'offer_received': 'sum',
        'offer_viewed': 'sum',
        'offer_completed': 'sum',
        'transaction': 'sum',
        'amount': 'sum'
    })

    correlation_matrix = correlation_data.corr()

    # Visualize correlation matrix
    fig_corr = px.imshow(correlation_matrix, title='Correlation between Offer Interactions and Transaction Behavior')
    st.plotly_chart(fig_corr)

    # Key insights
    st.header("Key Insights")
    st.write("1. The overall trend in transactions shows [insert insight about trend].")
    st.write("2. We identified [number] main customer segments based on their transaction behavior.")
    st.write("3. The average estimated Customer Lifetime Value is $", round(summary['clv'].mean(), 2))
    st.write("4. There is a [strong/weak] correlation between offer completions and transaction amounts.")
    st.write("5. [Insert any other key insights derived from the analysis]")

if __name__ == "__main__":
    transaction_analysis_page()