import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
from utils.data_loader import load_all_data

# Step 1: Load and preprocess data
def load_and_prepare_data():
    offer_events, transaction_events = load_all_data()

    # Ensure 'time' is converted to datetime format
    transaction_events['time'] = pd.to_datetime(transaction_events['time'], unit='h')

    # Create RFM (Recency, Frequency, Monetary) dataframe
    rfm = transaction_events.groupby('customer_id').agg({
        'time': lambda x: (transaction_events['time'].max() - x.max()).days,
        'event': 'count',
        'amount': 'sum'
    })

    rfm.columns = ['recency', 'frequency', 'monetary']

    # Handle cases where monetary might be zero or negative
    rfm['monetary'] = rfm['monetary'].apply(lambda x: x if x > 0 else 0)

    return rfm

# Step 2: Train the KMeans model
def train_kmeans_model(rfm_data):
    scaler = StandardScaler()
    rfm_normalized = scaler.fit_transform(rfm_data)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    kmeans.fit(rfm_normalized)

    return kmeans, scaler

# Step 3: Save the trained models
def save_models(kmeans, scaler):
    joblib.dump(kmeans, '../models/kmeans_model.joblib')
    joblib.dump(scaler, '../models/scaler.joblib')

def main():
    rfm_data = load_and_prepare_data()
    kmeans, scaler = train_kmeans_model(rfm_data)
    save_models(kmeans, scaler)
    print("Models have been trained and saved successfully.")

if __name__ == "__main__":
    main()
