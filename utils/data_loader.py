# utils/data_loader.py
import os
import sqlite3
import streamlit as st
import pandas as pd

def get_database_connection():
    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(__file__), '../data/maven_rewards.db')
    # Create a new connection with check_same_thread set to False
    return sqlite3.connect(db_path, check_same_thread=False)

@st.cache_data(ttl=3600)
def load_offer_events():
    conn = get_database_connection()
    try:
        return pd.read_sql_query("SELECT * FROM offer_events", conn)
    finally:
        conn.close()

@st.cache_data(ttl=3600)
def load_transaction_events():
    conn = get_database_connection()
    try:
        return pd.read_sql_query("SELECT * FROM transaction_events", conn)
    finally:
        conn.close()

@st.cache_data(ttl=3600)
def load_all_data():
    offer_events = load_offer_events()
    transaction_events = load_transaction_events()
    return offer_events, transaction_events
