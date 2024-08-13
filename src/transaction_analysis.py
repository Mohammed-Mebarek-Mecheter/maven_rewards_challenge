# src/transaction_analysis.py
import streamlit as st
import pandas as pd
import altair as alt
from statsmodels.tsa.arima.model import ARIMA
from st_aggrid import AgGrid, GridOptionsBuilder
from sklearn.cluster import KMeans
from utils.visualizations import plot_transaction_time_series
from utils.data_processor import preprocess_transaction_events, analyze_customer_lifetime_value
from utils.pdf_generator import generate_pdf_report

# Caching data processing functions
def preprocess_and_filter_transactions(transaction_events, min_amount, max_amount, min_frequency, max_frequency):
    transaction_events = preprocess_transaction_events(transaction_events)
    filtered_transactions = transaction_events[(transaction_events['amount'] >= min_amount) &
                                               (transaction_events['amount'] <= max_amount)]
    transaction_counts = filtered_transactions['customer_id'].value_counts()
    filtered_customers = transaction_counts[(transaction_counts >= min_frequency) &
                                            (transaction_counts <= max_frequency)].index
    filtered_transactions = filtered_transactions[filtered_transactions['customer_id'].isin(filtered_customers)]
    return filtered_transactions

# Weekly Transaction Trend with Theme Colors
def plot_weekly_transaction_trend(filtered_transactions, primary_color, secondary_color):
    weekly_transactions = filtered_transactions.set_index('time').resample('W')['amount'].sum().reset_index()
    weekly_chart = alt.Chart(weekly_transactions).mark_area(
        line={'color': primary_color},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color=secondary_color, offset=0),
                   alt.GradientStop(color=primary_color, offset=1)],
            x1=1,
            x2=1,
            y1=1,
            y2=0
        )
    ).encode(
        x=alt.X('time:T', title='Date'),
        y=alt.Y('amount:Q', title='Total Transaction Amount ($)'),
        tooltip=[alt.Tooltip('time:T', title='Date'), alt.Tooltip('amount:Q', title='Amount', format='$,.2f')]
    ).properties(title='Weekly Transaction Trend')
    return weekly_chart

# Basket Analysis with Theme Colors
def plot_basket_analysis(basket_data, primary_color):
    scatter = alt.Chart(basket_data).mark_circle(size=60).encode(
        x=alt.X('transaction_count:Q', title='Number of Transactions'),
        y=alt.Y('avg_basket_size:Q', title='Average Basket Size ($)'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='dark2'), title='Segment'),
        tooltip=['transaction_count', 'avg_basket_size', 'cluster']
    ).properties(title='Customer Segments based on Transaction Behavior')
    scatter = scatter.configure_mark(color=primary_color)
    return scatter

def transaction_analysis_page(offer_events, transaction_events):
    # Determine theme colors
    primary_color = st.get_option("theme.primaryColor")
    secondary_color = st.get_option("theme.backgroundColor")

    st.title("Transaction Analysis")

    # Sidebar for filters
    st.sidebar.header("⚙️ Filters")
    min_transaction_amount = st.sidebar.slider("Min Transaction Amount ($)", 0, int(transaction_events['amount'].max()), 0)
    max_transaction_amount = st.sidebar.slider("Max Transaction Amount ($)", 0, int(transaction_events['amount'].max()), int(transaction_events['amount'].max()))
    min_transaction_frequency = st.sidebar.slider("Min Transaction Frequency", 0, int(transaction_events['customer_id'].value_counts().max()), 0)
    max_transaction_frequency = st.sidebar.slider("Max Transaction Frequency", 0, int(transaction_events['customer_id'].value_counts().max()), int(transaction_events['customer_id'].value_counts().max()))

    # Preprocess and filter transaction events
    filtered_transactions = preprocess_and_filter_transactions(transaction_events, min_transaction_amount, max_transaction_amount, min_transaction_frequency, max_transaction_frequency)

    # Transaction Overview
    st.header("📊 Transaction Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", f"{len(filtered_transactions):,}")
    col2.metric("Total Revenue", f"${filtered_transactions['amount'].sum():,.2f}")
    col3.metric("Average Transaction Value", f"${filtered_transactions['amount'].mean():.2f}")

    # Time series analysis of transactions
    st.header("📈 Transaction Trends")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Daily Transactions")
        fig_time_series = plot_transaction_time_series(filtered_transactions, primary_color)
        st.plotly_chart(fig_time_series, use_container_width=True)

    with col2:
        st.subheader("Weekly Trend")
        fig_weekly = plot_weekly_transaction_trend(filtered_transactions, primary_color, secondary_color)
        st.altair_chart(fig_weekly, use_container_width=True)

    with col3:
        st.subheader("Transaction Forecast")
        daily_transactions = filtered_transactions.set_index('time')['amount'].resample('D').sum()
        model = ARIMA(daily_transactions, order=(1, 1, 1))
        results = model.fit()
        forecast = results.forecast(steps=30)

        forecast_df = pd.DataFrame({'date': forecast.index, 'forecast': forecast.values})
        historical_df = pd.DataFrame({'date': daily_transactions.index, 'actual': daily_transactions.values})

        forecast_chart = alt.Chart(forecast_df).mark_line(color='secondary_color').encode(
            x='date:T',
            y='forecast:Q'
        )
        historical_chart = alt.Chart(historical_df).mark_line(color='primary_color').encode(
            x='date:T',
            y='actual:Q'
        )
        st.altair_chart(historical_chart + forecast_chart, use_container_width=True)

    # Basket Analysis
    st.header("🛒 Customer Segmentation")
    transaction_counts = filtered_transactions.groupby('customer_id').size().reset_index(name='transaction_count')
    transaction_amounts = filtered_transactions.groupby('customer_id')['amount'].sum().reset_index()
    basket_data = pd.merge(transaction_counts, transaction_amounts, on='customer_id')
    basket_data['avg_basket_size'] = basket_data['amount'] / basket_data['transaction_count']

    # Cluster customers based on transaction count and average basket size
    kmeans = KMeans(n_clusters=4, random_state=42)
    basket_data['cluster'] = kmeans.fit_predict(basket_data[['transaction_count', 'avg_basket_size']])

    col1, col2 = st.columns(2)

    with col1:
        fig_basket = plot_basket_analysis(basket_data, primary_color)
        st.altair_chart(fig_basket, use_container_width=True)

    with col2:
        st.subheader("Segment Characteristics")
        cluster_stats = basket_data.groupby('cluster')[['transaction_count', 'avg_basket_size']].mean().round(2)
        cluster_stats.columns = ['Avg. Transactions', 'Avg. Basket Size ($)']
        cluster_stats.index.name = 'Segment'

        gb = GridOptionsBuilder.from_dataframe(cluster_stats)
        gb.configure_default_column(min_column_width=120)
        gridOptions = gb.build()

        AgGrid(cluster_stats, gridOptions=gridOptions, height=300)

    # Customer Lifetime Value (CLV) Analysis
    st.header("💰 Customer Lifetime Value Analysis")
    clv_data = analyze_customer_lifetime_value(filtered_transactions)

    if not clv_data.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribution of CLV")
            fig_clv = alt.Chart(clv_data).mark_bar().encode(
                x=alt.X('total_spend:Q', bin=alt.Bin(maxbins=20), title='Total Spend ($)'),
                y=alt.Y('count()', title='Number of Customers'),
                color=alt.value(primary_color)
            ).properties(title='')
            st.altair_chart(fig_clv, use_container_width=True)

        with col2:
            st.subheader("Top Customers by CLV")
            top_customers = clv_data.sort_values(by='total_spend', ascending=False).head(10)
            if 'customer_id' in top_customers.columns:
                gb = GridOptionsBuilder.from_dataframe(top_customers[['customer_id', 'total_spend', 'annual_value']])
                gb.configure_default_column(min_column_width=120)
                gridOptions = gb.build()

                AgGrid(top_customers[['customer_id', 'total_spend', 'annual_value']],
                       gridOptions=gridOptions,
                       height=300)
            else:
                st.write(top_customers)
    else:
        st.write("No data available for CLV analysis in the selected filters.")

    # Export options
    st.sidebar.header("📤 Export Options")
    if st.sidebar.button("Generate PDF Report"):
        pdf_buffer = generate_pdf_report(filtered_transactions, basket_data, clv_data, cluster_stats)
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="transaction_analysis_report.pdf",
            mime="application/pdf"
        )

