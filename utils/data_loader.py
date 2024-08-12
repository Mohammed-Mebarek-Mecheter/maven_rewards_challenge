# utils/data_loader.py
import pandas as pd
import streamlit as st

@st.cache_data
def load_offer_events():
    """
    Load the Offer Interaction Events Dataset.
    """
    return pd.read_csv('data/cleaned_offer_events.csv')

@st.cache_data
def load_transaction_events():
    """
    Load the Customer Transaction Events Dataset.
    """
    return pd.read_csv('data/cleaned_transaction_events.csv')

def load_all_data():
    """
    Load both datasets and return them as a tuple.
    """
    offer_events = load_offer_events()
    transaction_events = load_transaction_events()
    return offer_events, transaction_events