# utils/data_loader.py
import os
from pyspark.sql import SparkSession
import streamlit as st
import pandas as pd

@st.cache_resource
def get_spark_session():
    """Initialize and cache a Spark session."""
    return SparkSession.builder \
        .appName("MavenRewards") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()

@st.cache_data(ttl=3600)  # Cache with a time-to-live (TTL) of 1 hour
def load_parquet_data(file_path):
    """Load data from a Parquet file using Spark and convert to Pandas."""
    spark = get_spark_session()
    df = spark.read.parquet(file_path)
    return df.toPandas()  # Convert to Pandas DataFrame

@st.cache_data(ttl=3600)
def load_transaction_events():
    df = load_parquet_data("data/transaction_events.parquet")
    df['time'] = pd.to_datetime(df['time'], unit='h', origin='unix')  # Ensure datetime conversion is consistent
    return df

@st.cache_data(ttl=3600)
def load_offer_events():
    return load_parquet_data("data/offer_events.parquet")

@st.cache_data(ttl=3600)
def load_all_data():
    offer_events = load_offer_events()
    transaction_events = load_transaction_events()
    return offer_events, transaction_events
