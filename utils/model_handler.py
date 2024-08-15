# utils/model_handler.py
import joblib
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

@st.cache_resource
def load_kmeans_model():
    return joblib.load('models/kmeans_model.joblib')

@st.cache_resource
def load_scaler():
    return joblib.load('models/scaler.joblib')

@st.cache_data
def apply_customer_segmentation(transaction_df):

    scaler = load_scaler()
    kmeans = load_kmeans_model()

    # Ensure 'time' is converted to datetime format
    transaction_df['time'] = pd.to_datetime(transaction_df['time'], unit='h')

    rfm = transaction_df.groupby('customer_id').agg({
        'time': lambda x: (transaction_df['time'].max() - x.max()).days,
        'event': 'count',
        'amount': 'sum'
    })
    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm['monetary'] = rfm['monetary'].apply(lambda x: x if x > 0 else 0)

    rfm_normalized = scaler.transform(rfm)
    rfm['cluster'] = kmeans.predict(rfm_normalized)

    return rfm

def train_and_save_models(rfm_data):

    scaler = StandardScaler()
    rfm_normalized = scaler.fit_transform(rfm_data)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    kmeans.fit(rfm_normalized)

    joblib.dump(kmeans, 'models/kmeans_model.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')