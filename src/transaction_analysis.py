# src/transaction_analysis.py
import streamlit as st
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from st_aggrid import AgGrid, GridOptionsBuilder
from utils.data_loader import load_transaction_events
from utils.model_handler import apply_customer_segmentation
from utils.visualizations import (
    plot_weekly_transaction_trend,
    plot_basket_analysis,
    plot_clv_distribution,
    plot_transaction_forecast
)
from utils.data_processor import (
    preprocess_transaction_events,
    analyze_customer_lifetime_value,
    create_basket_data
)
from utils.pdf_generator import generate_pdf_report
from utils.styles import load_css

@st.cache_data
def preprocess_and_filter_transactions(start_date, end_date, transaction_amount_range):
    transaction_events = load_transaction_events()
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
    st.markdown('<h1 class="title">Transaction Analysis</h1>', unsafe_allow_html=True)
    # Load CSS
    st.markdown(load_css(), unsafe_allow_html=True)

    # Sidebar for filters
    st.sidebar.header("⚙️ Filters")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    time_range = st.sidebar.slider("Select Time Range", min_value=1, max_value=30, value=(1, 30))
    transaction_events = load_transaction_events()
    if transaction_events['time'].dtype == 'int':
        # Assuming time is in hours since the start
        transaction_events['time'] = pd.to_datetime(transaction_events['time'], unit='h', origin='unix')
        # Convert 'time' column to datetime if not already
    transaction_events['time'] = pd.to_datetime(transaction_events['time'])

    min_date = transaction_events['time'].min().date()
    start_date = min_date + pd.to_timedelta(time_range[0] - 1, unit='D')
    end_date = min_date + pd.to_timedelta(time_range[1] - 1, unit='D')

    transaction_amount_range = st.sidebar.slider("Transaction Amount ($)", 0, int(transaction_events['amount'].max()),
                                                 (0, int(transaction_events['amount'].max())))
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Preprocess and filter transaction events
    filtered_transactions = preprocess_and_filter_transactions(start_date, end_date, transaction_amount_range)

    # Transaction Overview
    #st.markdown('<h2 class="header">📊 Transaction Overview</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f"{len(filtered_transactions):,}" +
                    '</div><div class="metric-label">Total Transactions</div></div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f"${filtered_transactions['amount'].sum():,.2f}" +
                    '</div><div class="metric-label">Total Revenue</div></div>',
                    unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f"${filtered_transactions['amount'].mean():.2f}" +
                    '</div><div class="metric-label">Average Transaction Value</div></div>',
                    unsafe_allow_html=True)

    # Time series analysis of transactions
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    #st.markdown('<h2 class="header">📈 Transaction Trends</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<h3 class="sub-header">Weekly Trend</h3>', unsafe_allow_html=True)
        fig_weekly = plot_weekly_transaction_trend(filtered_transactions)
        st.altair_chart(fig_weekly, use_container_width=True)

    with col2:
        st.markdown('<h3 class="sub-header">Segment Characteristics</h3>', unsafe_allow_html=True)
        basket_data = create_basket_data(filtered_transactions)
        cluster_stats = basket_data.groupby('cluster')[['transaction_count', 'avg_basket_size']].mean().round(2)
        cluster_stats.columns = ['Avg. Transactions', 'Avg. Basket Size ($)']
        cluster_stats.index.name = 'Segment'

        gb = GridOptionsBuilder.from_dataframe(cluster_stats)
        gb.configure_default_column(min_column_width=20)
        gb.configure_grid_options(
            rowStyle={"color": "#6f4f28", "background-color": "#f0e6db"},
            # Adjust this to match the desired app background
            headerStyle={"color": "#000", "background-color": "#dcd6c7"},
            # Header background color to match the app's theme
        )
        gridOptions = gb.build()

        AgGrid(cluster_stats,
               gridOptions=gridOptions,
               height=170)

    # st.markdown('<h3 class="sub-header">Daily Transactions</h3>', unsafe_allow_html=True)
    # fig_time_series = plot_transaction_time_series(filtered_transactions)
    # st.plotly_chart(fig_time_series, use_container_width=True)

    # Basket Analysis
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    # st.markdown('<h2 class="header">🛒 Customer Segmentation</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<h3 class="sub-header">Basket Analysis</h3>', unsafe_allow_html=True)
        fig_basket = plot_basket_analysis(basket_data)
        st.altair_chart(fig_basket, use_container_width=True)

    with col2:
        st.markdown('<h3 class="sub-header">Transaction Forecast</h3>', unsafe_allow_html=True)
        daily_transactions = filtered_transactions.set_index('time')['amount'].resample('D').sum()
        forecast_df, historical_df = generate_forecast(daily_transactions)

        forecast_chart = plot_transaction_forecast(forecast_df, historical_df)
        st.altair_chart(forecast_chart, use_container_width=True)


    # Customer Lifetime Value (CLV) Analysis
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    #st.markdown('<h2 class="header">💰 Customer Lifetime Value Analysis</h2>', unsafe_allow_html=True)
    clv_data = analyze_customer_lifetime_value(filtered_transactions)

    # if not clv_data.empty:
    #     col1, col2 = st.columns(2)
    #
    #     with col1:
    #         st.markdown('<h3 class="sub-header">Distribution of CLV</h3>', unsafe_allow_html=True)
    #         fig_clv = plot_clv_distribution(clv_data)
    #         st.altair_chart(fig_clv, use_container_width=True)

    st.markdown('<h3 class="sub-header">Top Customers by CLV</h3>', unsafe_allow_html=True)
    top_customers = clv_data.sort_values(by='total_spend', ascending=False).head(10)
    if 'customer_id' in top_customers.columns:
        gb = GridOptionsBuilder.from_dataframe(top_customers[['customer_id', 'total_spend', 'annual_value']])
        gb.configure_default_column(min_column_width=120)
        gridOptions = gb.build()

        AgGrid(top_customers[['customer_id', 'total_spend', 'annual_value']],
               gridOptions=gridOptions,
               height=350)
    else:
        st.write(top_customers)

    # else:
    #     st.write("No data available for CLV analysis in the selected filters.")

    # Export options
    st.sidebar.header("📤 Export Option")
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    if st.sidebar.button("Generate PDF Report"):
        pdf_buffer = generate_pdf_report(filtered_transactions, basket_data, clv_data, cluster_stats)
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="transaction_analysis_report.pdf",
            mime="application/pdf"
        )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    transaction_analysis_page()
