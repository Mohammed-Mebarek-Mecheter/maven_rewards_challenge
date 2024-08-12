# pages/offer_performance.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_data
from utils.data_processor import preprocess_offer_events, create_customer_segments, analyze_offer_performance
from utils.visualizations import plot_offer_performance, plot_channel_effectiveness

def offer_performance_page():
    st.title("Offer Performance Analysis")

    # Load and preprocess data
    offer_events, transaction_events = load_all_data()
    offer_events = preprocess_offer_events(offer_events)

    # Convert 'time' in offer_events and transaction_events to datetime
    offer_events['time'] = pd.to_datetime(offer_events['time'], unit='h')
    transaction_events['time'] = pd.to_datetime(transaction_events['time'], unit='h')  # Ensure the same unit is used

    # Merge offer_events with transaction_events
    merged_data = pd.merge_asof(offer_events.sort_values('time'),
                                transaction_events[['customer_id', 'time', 'amount']].sort_values('time'),
                                on='time',
                                by='customer_id',
                                direction='forward')

    # Create customer segments
    rfm_data = create_customer_segments(merged_data, transaction_events)
    merged_data['cluster'] = merged_data['customer_id'].map(rfm_data['cluster'])

    # Sidebar for interactive filters
    st.sidebar.header("Filters")
    offer_types = st.sidebar.multiselect("Offer Types", merged_data['offer_type'].unique(), default=merged_data['offer_type'].unique())
    segments = st.sidebar.multiselect("Customer Segments", rfm_data['cluster'].unique(), default=rfm_data['cluster'].unique())

    # Apply filters
    filtered_offers = merged_data[
        (merged_data['offer_type'].isin(offer_types)) &
        (merged_data['cluster'].isin(segments))
        ]

    # Offer Type Analysis
    st.header("Offer Type Analysis")
    offer_type_counts = filtered_offers['offer_type'].value_counts()
    fig_offer_types = px.pie(values=offer_type_counts.values, names=offer_type_counts.index, title="Distribution of Offer Types")
    st.plotly_chart(fig_offer_types)

    # Offer Success Rate by Type
    success_rate = filtered_offers.groupby('offer_type')['offer_success'].mean().sort_values(ascending=False)
    fig_success_rate = px.bar(x=success_rate.index, y=success_rate.values, title="Offer Success Rate by Type")
    fig_success_rate.update_layout(xaxis_title="Offer Type", yaxis_title="Success Rate")
    st.plotly_chart(fig_success_rate)

    # Conversion Rates by Offer Type and Customer Segment
    st.header("Conversion Rates by Offer Type and Customer Segment")
    performance_df = analyze_offer_performance(filtered_offers)
    fig_performance = plot_offer_performance(performance_df)
    st.plotly_chart(fig_performance)

    # Channel Effectiveness Analysis
    st.header("Channel Effectiveness Analysis")
    fig_channel = plot_channel_effectiveness(filtered_offers)
    st.plotly_chart(fig_channel)

    # Average Spend by Offer Type
    st.header("Average Spend by Offer Type")
    avg_spend = filtered_offers.groupby('offer_type')['amount'].mean().sort_values(ascending=False)
    fig_avg_spend = px.bar(x=avg_spend.index, y=avg_spend.values, title="Average Transaction Amount by Offer Type")
    fig_avg_spend.update_layout(xaxis_title="Offer Type", yaxis_title="Average Transaction Amount")
    st.plotly_chart(fig_avg_spend)

    # A/B Testing Results Visualization
    st.header("A/B Testing Results")

    # Simulate A/B test results (replace with actual A/B test data if available)
    ab_test_data = pd.DataFrame({
        'Variant': ['A', 'B'],
        'Conversion_Rate': [0.15, 0.18],
        'Average_Revenue': [25.5, 28.2]
    })

    col1, col2 = st.columns(2)

    with col1:
        fig_ab_conversion = px.bar(ab_test_data, x='Variant', y='Conversion_Rate', title="A/B Test: Conversion Rate")
        st.plotly_chart(fig_ab_conversion)

    with col2:
        fig_ab_revenue = px.bar(ab_test_data, x='Variant', y='Average_Revenue', title="A/B Test: Average Revenue")
        st.plotly_chart(fig_ab_revenue)

    # Statistical significance (this is a placeholder - replace with actual statistical test)
    st.write("Statistical Significance:")
    st.write("p-value for conversion rate: 0.03 (significant at 5% level)")
    st.write("p-value for average revenue: 0.07 (not significant at 5% level)")

    # Offer Duration Analysis
    st.header("Offer Duration Analysis")
    fig_duration = px.scatter(filtered_offers, x='duration', y='offer_success', color='offer_type',
                              title="Offer Success Rate vs Duration")
    fig_duration.update_layout(xaxis_title="Offer Duration (days)", yaxis_title="Success Rate")
    st.plotly_chart(fig_duration)

    # Key Insights
    st.header("Key Insights")
    st.write("1. The most successful offer type is [insert insight].")
    st.write("2. Customer segment [X] responds best to [Y] type of offers.")
    st.write("3. The most effective channel for offer distribution is [insert channel].")
    st.write("4. A/B testing results suggest that Variant [A/B] performs better in terms of conversion rate.")
    st.write("5. Offer duration seems to have [positive/negative] correlation with offer success rate.")

if __name__ == "__main__":
    offer_performance_page()
