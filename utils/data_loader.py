# utils/data_loader.py
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def load_offer_events():
    return pd.read_csv('data/cleaned_offer_events.csv')

@st.cache_data(ttl=3600)
def load_transaction_events():
    return pd.read_csv('data/cleaned_transaction_events.csv')

@st.cache_data(ttl=3600)
def load_all_data():
    offer_events = load_offer_events()
    transaction_events = load_transaction_events()
    return offer_events, transaction_events