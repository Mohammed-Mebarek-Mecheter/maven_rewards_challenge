# utils/data_processor.py
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

def preprocess_offer_events(df):
    """
    Preprocess the Offer Interaction Events Dataset.
    """
    # Convert time to datetime
    df['time'] = pd.to_datetime(df['time'], unit='h')

    # Create a flag for successful offers (viewed and completed)
    df['offer_success'] = ((df['event'] == 'offer completed') &
                           (df['time'] - df.groupby('offer_id')['time'].transform('first') <=
                            df['duration'].apply(lambda x: pd.Timedelta(days=x))))

    return df

def preprocess_transaction_events(df):
    """
    Preprocess the Customer Transaction Events Dataset.
    """
    # Convert time to datetime
    df['time'] = pd.to_datetime(df['time'], unit='h')

    # Calculate total spend per customer
    df['total_spend'] = df.groupby('customer_id')['amount'].transform('sum')

    return df

def create_customer_segments(offer_df, transaction_df, n_clusters=5):
    """
    Create customer segments based on RFM analysis and K-means clustering.
    """
    # Convert 'time' to datetime
    transaction_df['time'] = pd.to_datetime(transaction_df['time'], unit='h')

    # Recency
    max_date = transaction_df['time'].max()
    rfm = transaction_df.groupby('customer_id').agg({
        'time': lambda x: (max_date - x.max()).days,
        'event': 'count',
        'amount': 'sum'
    })
    rfm.columns = ['recency', 'frequency', 'monetary']

    # Normalize RFM values
    rfm_normalized = (rfm - rfm.mean()) / rfm.std()

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    rfm['cluster'] = kmeans.fit_predict(rfm_normalized)

    return rfm

def analyze_offer_performance(df):
    """
    Analyze offer performance by type and customer segment.
    """
    performance = df.groupby(['offer_type', 'cluster'])['offer_success'].agg(['mean', 'count'])
    performance.columns = ['conversion_rate', 'total_offers']
    return performance

# Add more data processing functions as needed

