import joblib
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

@st.cache_resource
def load_model(model_path: str):
    """
    Load a machine learning model from the specified file path.

    Args:
        model_path (str): Path to the model file.

    Returns:
        The loaded model.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    return joblib.load(model_path)


@st.cache_data
def apply_customer_segmentation(transaction_df: pd.DataFrame, scaler_path: str = 'models/scaler.joblib',
                                kmeans_path: str = 'models/kmeans_model.joblib') -> pd.DataFrame:
    """
    Apply customer segmentation based on RFM (Recency, Frequency, Monetary) metrics using KMeans clustering.

    Args:
        transaction_df (pd.DataFrame): DataFrame containing transaction data.
        scaler_path (str): Path to the pre-trained scaler model.
        kmeans_path (str): Path to the pre-trained KMeans model.

    Returns:
        pd.DataFrame: DataFrame with an additional 'cluster' column indicating customer segment.
    """
    scaler = load_model(scaler_path)
    kmeans = load_model(kmeans_path)

    # Ensure 'time' is converted to datetime format
    transaction_df['time'] = pd.to_datetime(transaction_df['time'], unit='h')

    # Calculate RFM metrics
    rfm = transaction_df.groupby('customer_id').agg({
        'time': lambda x: (transaction_df['time'].max() - x.max()).days,
        'event': 'count',
        'amount': 'sum'
    }).rename(columns={'time': 'recency', 'event': 'frequency', 'amount': 'monetary'})

    # Ensure monetary value is non-negative
    rfm['monetary'] = rfm['monetary'].apply(lambda x: max(x, 0))

    # Normalize RFM data and predict clusters
    rfm_normalized = scaler.transform(rfm)
    rfm['cluster'] = kmeans.predict(rfm_normalized)

    return rfm


def train_and_save_models(rfm_data: pd.DataFrame, n_clusters: int = 4,
                          model_dir: str = 'models', random_state: int = 42):
    """
    Train a KMeans model based on RFM data and save the model along with the scaler.

    Args:
        rfm_data (pd.DataFrame): DataFrame containing RFM data.
        n_clusters (int): Number of clusters for KMeans.
        model_dir (str): Directory to save the trained models.
        random_state (int): Random seed for reproducibility.
    """
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    scaler = StandardScaler()
    rfm_normalized = scaler.fit_transform(rfm_data)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init='auto')
    kmeans.fit(rfm_normalized)

    joblib.dump(kmeans, os.path.join(model_dir, 'kmeans_model.joblib'))
    joblib.dump(scaler, os.path.join(model_dir, 'scaler.joblib'))
