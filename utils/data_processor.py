# utils/data_processor.py
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def preprocess_offer_events(df):
    df['time'] = pd.to_datetime(df['time'], unit='h')
    df['offer_success'] = ((df['event'] == 'offer completed') &
                           (df['time'] - df.groupby('offer_id')['time'].transform('first') <=
                            df['duration'].apply(lambda x: pd.Timedelta(days=x))))
    return df

def preprocess_transaction_events(df):
    df['time'] = pd.to_datetime(df['time'], unit='h')
    df['total_spend'] = df.groupby('customer_id')['amount'].transform('sum')
    return df

def create_customer_segments(offer_df, transaction_df, n_clusters=4):
    transaction_df['time'] = pd.to_datetime(transaction_df['time'], unit='h')
    max_date = transaction_df['time'].max()

    rfm = transaction_df.groupby('customer_id').agg({
        'time': lambda x: (max_date - x.max()).days,
        'event': 'count',
        'amount': 'sum'
    })
    rfm.columns = ['recency', 'frequency', 'monetary']

    # Log transform monetary values
    rfm['monetary'] = np.log1p(rfm['monetary'])

    # Normalize RFM values
    scaler = StandardScaler()
    rfm_normalized = pd.DataFrame(scaler.fit_transform(rfm), columns=rfm.columns, index=rfm.index)

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm['cluster'] = kmeans.fit_predict(rfm_normalized)

    return rfm

def analyze_offer_performance(df):
    performance = df.groupby(['offer_type', 'cluster'])['offer_success'].agg(['mean', 'count'])
    performance.columns = ['conversion_rate', 'total_offers']
    return performance

def analyze_customer_lifetime_value(transaction_df):
    clv = transaction_df.groupby('customer_id').agg({
        'amount': 'sum',
        'age': 'mean'  # Use the 'age' column directly
    })
    clv.columns = ['total_spend', 'customer_age']
    clv['annual_value'] = clv['total_spend'] / clv['customer_age']
    return clv
