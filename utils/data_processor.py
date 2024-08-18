# utils/data_processor.py
import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_all_data
from utils.model_handler import apply_customer_segmentation
from statsmodels.tsa.arima.model import ARIMA

@st.cache_data
def load_and_preprocess_data():
    offer_events, transaction_events = load_all_data()
    offer_events = preprocess_offer_events(offer_events)
    transaction_events = preprocess_transaction_events(transaction_events)
    return offer_events, transaction_events

@st.cache_data
def preprocess_offer_data(offer_events, selected_offer_types):
    return offer_events.query("offer_type in @selected_offer_types")

@st.cache_data
def preprocess_transaction_data(transaction_events, min_amount, max_amount):
    return transaction_events.query("amount >= @min_amount and amount <= @max_amount")

@st.cache_data
def preprocess_offer_events(df):
    # Convert 'time' column
    df['time'] = pd.to_datetime(df['time'], unit='h')

    # Define success condition
    df['offer_success'] = ((df['event'] == 'offer completed') &
                           (df['time'] - df.groupby('offer_id')['time'].transform('first') <=
                            df['duration'].apply(lambda x: pd.Timedelta(days=x))))

    # Remove outliers in 'age' column
    if 'age' in df.columns:
        q1 = df['age'].quantile(0.25)
        q3 = df['age'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        df = df[(df['age'] >= lower_bound) & (df['age'] <= upper_bound)]

    return df

@st.cache_data
def preprocess_and_filter_transactions(transaction_events, start_date, end_date, transaction_amount_range):
    """Preprocess and filter transaction events based on date range and transaction amount."""
    filtered_transactions = transaction_events[
        (transaction_events['time'].dt.date.between(start_date, end_date)) &
        (transaction_events['amount'].between(transaction_amount_range[0], transaction_amount_range[1]))
        ]
    return filtered_transactions

@st.cache_data
def preprocess_transaction_events(df):
    df['time'] = pd.to_datetime(df['time'], unit='h')
    df['total_spend'] = df.groupby('customer_id')['amount'].transform('sum')
    return df


@st.cache_data
def analyze_offer_performance(df):
    performance = df.groupby(['offer_type', 'cluster'])['offer_success'].agg(['mean', 'count'])
    performance.columns = ['conversion_rate', 'total_offers']
    return performance

@st.cache_data
def generate_forecast(daily_transactions, steps=30):
    """
    Generate a forecast for future transaction amounts based on historical daily transaction data.

    Parameters:
    - daily_transactions (pd.Series): A time series of daily transaction amounts.
    - steps (int): The number of future steps (days) to forecast.

    Returns:
    - forecast_df (pd.DataFrame): DataFrame containing the forecasted transaction amounts.
    - historical_df (pd.DataFrame): DataFrame containing the historical transaction amounts.
    """
    # Ensure the index is a datetime index (this should already be the case, but it's good to confirm)
    if not isinstance(daily_transactions.index, pd.DatetimeIndex):
        daily_transactions.index = pd.to_datetime(daily_transactions.index)

    # Fit an ARIMA model on the historical data
    model = ARIMA(daily_transactions, order=(1, 1, 1))  # (p, d, q) order can be adjusted based on the data
    results = model.fit()

    # Forecast future values
    forecast = results.get_forecast(steps=steps)
    forecast_index = pd.date_range(start=daily_transactions.index[-1] + pd.Timedelta(days=1), periods=steps, freq='D')
    forecast_df = pd.DataFrame({'date': forecast_index, 'forecast': forecast.predicted_mean})

    # Historical data for plotting
    historical_df = pd.DataFrame({'date': daily_transactions.index, 'actual': daily_transactions.values})

    return forecast_df, historical_df

@st.cache_data
def analyze_customer_lifetime_value(transaction_df):
    """Calculate customer lifetime value (CLV) based on transaction data."""
    clv = transaction_df.groupby('customer_id').agg({
        'amount': 'sum',
        'age': 'mean'
    })
    clv.columns = ['total_spend', 'customer_age']
    clv['annual_value'] = clv['total_spend'] / clv['customer_age']
    return clv


@st.cache_data
def create_basket_data(filtered_transactions):
    transaction_counts = filtered_transactions.groupby('customer_id').size().reset_index(name='transaction_count')
    transaction_amounts = filtered_transactions.groupby('customer_id')['amount'].sum().reset_index()
    basket_data = pd.merge(transaction_counts, transaction_amounts, on='customer_id')
    basket_data['avg_basket_size'] = basket_data['amount'] / basket_data['transaction_count']

    rfm_data = apply_customer_segmentation(filtered_transactions)
    basket_data = basket_data.merge(rfm_data[['cluster']], left_on='customer_id', right_index=True)

    return basket_data


@st.cache_data
def preprocess_channels(transaction_df):
    transaction_df['channels'] = transaction_df['channels'].apply(eval)
    exploded_df = transaction_df.explode('channels')
    return exploded_df


@st.cache_data
def get_channel_success_rate(transaction_df):
    exploded_df = preprocess_channels(transaction_df)
    channel_success_rate = exploded_df.groupby('channels')['offer_success'].mean().reset_index()
    channel_success_rate.columns = ['channel', 'success_rate']
    return channel_success_rate

@st.cache_data
def calculate_advanced_metrics(rfm_data, offer_data):
    """Calculate advanced metrics for customer segmentation."""
    # Calculate Customer Lifetime Value (CLV)
    rfm_data['clv'] = rfm_data['monetary'] * rfm_data['frequency']
    avg_clv = rfm_data['clv'].mean()

    # Calculate Churn Rate (assuming churn if no transaction in last 30 days)
    churn_threshold = 30
    churn_rate = (rfm_data['recency'] > churn_threshold).mean()

    # Calculate Customer Acquisition Cost (CAC)
    # This is a simplified calculation and might need adjustment based on actual data
    total_marketing_spend = offer_data['reward'].sum()
    new_customers = len(rfm_data[rfm_data['frequency'] == 1])
    cac = total_marketing_spend / new_customers if new_customers > 0 else 0

    # Create clv_data with index as customer_id
    clv_data = rfm_data['clv'].reset_index()
    clv_data.columns = ['customer_id', 'clv']

    return {
        "clv": avg_clv,
        "churn_rate": churn_rate,
        "cac": cac,
        "clv_data": clv_data
    }

@st.cache_data
def calculate_roi(offer_events):
    roi = offer_events.groupby('offer_type').apply(
        lambda x: (x['reward'].sum() - x['difficulty'].sum()) / x['difficulty'].sum()
    )
    return roi

@st.cache_data
def calculate_segment_stats(basket_data):
    cluster_stats = basket_data.groupby('cluster')[['transaction_count', 'avg_basket_size']].mean().round(2)
    cluster_stats.columns = ['Avg. Transactions', 'Avg. Basket Size ($)']
    cluster_stats.index.name = 'Segment'
    return cluster_stats


@st.cache_data
def calculate_advanced_offer_metrics(offer_events_with_cluster, transaction_events):
    """Calculate advanced offer metrics such as redemption rate, churn rate, etc."""

    # Redemption Rate
    redemption_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean()

    # Customer Retention Rate
    retention_rate = transaction_events.groupby(transaction_events['time'].dt.date).size().pct_change().fillna(0)

    # Time to Redemption (Assume 'time' is in hours, convert to days)
    offer_events_with_cluster['time_to_redemption'] = offer_events_with_cluster['time'] / 24
    time_to_redemption = offer_events_with_cluster[offer_events_with_cluster['offer_success']].groupby('offer_type')['time_to_redemption'].mean()

    # Churn Rate (Customers who did not return)
    churn_rate = 1 - retention_rate

    # Offer Response Time Distribution
    response_time_distribution = offer_events_with_cluster.groupby(['cluster', 'offer_type'])['time_to_redemption'].median()

    return {
        "redemption_rate": redemption_rate,
        "retention_rate": retention_rate,
        "time_to_redemption": time_to_redemption,
        "churn_rate": churn_rate,
        "response_time_distribution": response_time_distribution
    }
