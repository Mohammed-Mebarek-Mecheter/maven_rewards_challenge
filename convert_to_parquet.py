# scripts/convert_to_parquet.py
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/maven_rewards.db')

offer_events = pd.read_sql_query("SELECT * FROM offer_events", conn)
transaction_events = pd.read_sql_query("SELECT * FROM transaction_events", conn)

offer_events.to_parquet('data/offer_events.parquet')
transaction_events.to_parquet('data/transaction_events.parquet')

conn.close()
