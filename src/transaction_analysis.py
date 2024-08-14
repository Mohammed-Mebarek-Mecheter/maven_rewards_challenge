# src/transaction_analysis.py
import streamlit as st
import altair as alt
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from st_aggrid import AgGrid, GridOptionsBuilder
from sklearn.cluster import KMeans
from utils.visualizations import (
    plot_transaction_time_series,
    plot_weekly_transaction_trend,
    plot_basket_analysis,
    plot_clv_distribution,
    plot_segment_characteristics
)
from utils.data_processor import (
    preprocess_transaction_events,
    analyze_customer_lifetime_value,
    create_basket_data
)
from utils.pdf_generator import generate_pdf_report


@st.cache_data
def preprocess_and_filter_transactions(transaction_events, start_date, end_date, transaction_amount_range):
    transaction_events = preprocess_transaction_events(transaction_events)
    filtered_transactions = transaction_events[
        (transaction_events['time'].dt.date.between(start_date, end_date)) &
        (transaction_events['amount'].between(transaction_amount_range[0], transaction_amount_range[1]))
    ]
    return filtered_transactions


@st.cache_data
def generate_forecast(daily_transactions, steps=30):
    model = ARIMA(daily_transactions, order=(1, 1, 1))
    results = model.fit()
    forecast = results.forecast(steps=steps)
    forecast_df = pd.DataFrame({'date': forecast.index, 'forecast': forecast.values})
    historical_df = pd.DataFrame({'date': daily_transactions.index, 'actual': daily_transactions.values})
    return forecast_df, historical_df


def transaction_analysis_page(offer_events, transaction_events):
    st.title("Transaction Analysis")

    # Sidebar for filters
    st.sidebar.header("⚙️ Filters")
    time_range = st.sidebar.slider("Select Time Range", min_value=1, max_value=30, value=(1, 30))
    min_date = transaction_events['time'].min().date()
    start_date = min_date + pd.to_timedelta(time_range[0] - 1, unit='D')
    end_date = min_date + pd.to_timedelta(time_range[1] - 1, unit='D')

    transaction_amount_range = st.sidebar.slider("Transaction Amount ($)", 0, int(transaction_events['amount'].max()),
                                                 (0, int(transaction_events['amount'].max())))

    # Preprocess and filter transaction events
    filtered_transactions = preprocess_and_filter_transactions(transaction_events, start_date, end_date,
                                                                transaction_amount_range)

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
        fig_time_series = plot_transaction_time_series(filtered_transactions)
        st.plotly_chart(fig_time_series, use_container_width=True)

    with col2:
        st.subheader("Weekly Trend")
        fig_weekly = plot_weekly_transaction_trend(filtered_transactions)
        st.altair_chart(fig_weekly, use_container_width=True)

    with col3:
        st.subheader("Transaction Forecast")
        daily_transactions = filtered_transactions.set_index('time')['amount'].resample('D').sum()
        forecast_df, historical_df = generate_forecast(daily_transactions)

        forecast_chart = alt.Chart(forecast_df).mark_line(color='#000').encode(
            x='date:T',
            y='forecast:Q'
        )
        historical_chart = alt.Chart(historical_df).mark_line(color='#6f4f28').encode(
            x='date:T',
            y='actual:Q'
        )
        st.altair_chart(historical_chart + forecast_chart, use_container_width=True)

    # Basket Analysis
    st.header("🛒 Customer Segmentation")
    basket_data = create_basket_data(filtered_transactions)

    col1, col2 = st.columns([1, 1])

    with col1:
        fig_basket = plot_basket_analysis(basket_data)
        st.altair_chart(fig_basket, use_container_width=True)

    with col2:
        cluster_stats = basket_data.groupby('cluster')[['transaction_count', 'avg_basket_size']].mean().round(2)
        cluster_stats.columns = ['Avg. Transactions', 'Avg. Basket Size ($)']
        cluster_stats.index.name = 'Segment'
        fig_segment_radar = plot_segment_characteristics(cluster_stats)
        st.altair_chart(fig_segment_radar, use_container_width=True)

    # Customer Lifetime Value (CLV) Analysis
    st.header("💰 Customer Lifetime Value Analysis")
    clv_data = analyze_customer_lifetime_value(filtered_transactions)

    if not clv_data.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribution of CLV")
            fig_clv = plot_clv_distribution(clv_data)
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


if __name__ == "__main__":
    transaction_analysis_page()
