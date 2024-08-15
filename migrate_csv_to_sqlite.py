import sqlite3
import pandas as pd

def migrate_csv_to_sqlite():
    # Connect to SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect('data/maven_rewards.db')
    cursor = conn.cursor()

    # Load CSV data into Pandas DataFrames
    offer_events_df = pd.read_csv('data/cleaned_offer_events.csv')
    transaction_events_df = pd.read_csv('data/cleaned_transaction_events.csv')

    # Migrate DataFrames to SQLite tables
    offer_events_df.to_sql('offer_events', conn, if_exists='replace', index=False)
    transaction_events_df.to_sql('transaction_events', conn, if_exists='replace', index=False)

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Data migration to SQLite completed successfully.")

if __name__ == "__main__":
    migrate_csv_to_sqlite()
