# utils/data_processor.py
import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_all_data
from utils.model_handler import apply_customer_segmentation


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
