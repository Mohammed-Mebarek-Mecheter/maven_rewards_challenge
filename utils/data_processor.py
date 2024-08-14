# utils/data_processor.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import ast

@st.cache_data
def preprocess_offer_data(offer_events, selected_offer_types):
    return offer_events.query("offer_type in @selected_offer_types")


@st.cache_data
def preprocess_transaction_data(transaction_events, min_amount, max_amount):
    return transaction_events.query("amount >= @min_amount and amount <= @max_amount")


@st.cache_data
def preprocess_offer_events(df):
    df['time'] = pd.to_datetime(df['time'], unit='h')
    df['offer_success'] = ((df['event'] == 'offer completed') &
                           (df['time'] - df.groupby('offer_id')['time'].transform('first') <=
                            df['duration'].apply(lambda x: pd.Timedelta(days=x))))
    return df


@st.cache_data
def preprocess_transaction_events(df):
    df['time'] = pd.to_datetime(df['time'], unit='h')
    df['total_spend'] = df.groupby('customer_id')['amount'].transform('sum')
    return df


@st.cache_data
def create_customer_segments(offer_df, transaction_df, n_clusters=4):
    transaction_df['time'] = pd.to_datetime(transaction_df['time'], unit='h')
    max_date = transaction_df['time'].max()

    rfm = transaction_df.groupby('customer_id').agg({
        'time': lambda x: (max_date - x.max()).days,
        'event': 'count',
        'amount': 'sum'
    })
    rfm.columns = ['recency', 'frequency', 'monetary']

    rfm['monetary'] = np.log1p(rfm['monetary'])

    scaler = StandardScaler()
    rfm_normalized = pd.DataFrame(scaler.fit_transform(rfm), columns=rfm.columns, index=rfm.index)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm['cluster'] = kmeans.fit_predict(rfm_normalized)

    return rfm


@st.cache_data
def analyze_offer_performance(df):
    performance = df.groupby(['offer_type', 'cluster'])['offer_success'].agg(['mean', 'count'])
    performance.columns = ['conversion_rate', 'total_offers']
    return performance


@st.cache_data
def analyze_customer_lifetime_value(transaction_df):
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

    # Cluster customers based on transaction count and average basket size
    kmeans = KMeans(n_clusters=4, random_state=42)
    basket_data['cluster'] = kmeans.fit_predict(basket_data[['transaction_count', 'avg_basket_size']])

    return basket_data


@st.cache_data
def preprocess_channels(transaction_df):
    """
    Preprocess the channels column by converting string representations of lists to actual lists,
    and then exploding the DataFrame to have one channel per row.
    """
    # Convert string representation of lists to actual lists
    transaction_df['channels'] = transaction_df['channels'].apply(ast.literal_eval)

    # Explode the channels column to have one channel per row
    exploded_df = transaction_df.explode('channels')

    return exploded_df


@st.cache_data
def get_channel_success_rate(transaction_df):
    """
    Calculate the success rate for each channel by grouping the exploded channels.
    """
    exploded_df = preprocess_channels(transaction_df)

    # Calculate success rate for each channel
    channel_success_rate = exploded_df.groupby('channels')['offer_success'].mean().reset_index()
    channel_success_rate.columns = ['channel', 'success_rate']

    return channel_success_rate

