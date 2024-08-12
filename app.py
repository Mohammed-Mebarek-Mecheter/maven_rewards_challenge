# app.py
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from pages.customer_segments import customer_segments_page
from pages.offer_performance import offer_performance_page
from pages.transaction_analysis import transaction_analysis_page
from utils.data_loader import load_all_data
from utils.data_processor import preprocess_offer_events, preprocess_transaction_events

# Set page config
st.set_page_config(page_title="Maven Rewards Challenge", page_icon=":coffee:", layout="wide")

# Custom CSS to inject for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #3d2c1f;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #5c3d2e;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0e6db;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #3d2c1f;
    }
    .metric-label {
        font-size: 1rem;
        color: #5c3d2e;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Header with Maven Cafe logo and challenge title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://via.placeholder.com/150x150.png?text=Maven+Cafe", width=100)  # Replace with actual logo
    with col2:
        st.markdown('<p class="main-header">Maven Rewards Challenge</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Data-Driven Marketing Strategy</p>', unsafe_allow_html=True)

    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Home", "Customer Segments", "Offer Performance", "Transaction Analysis"],
        icons=["house", "people-fill", "graph-up", "cash-coin"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    # Load and preprocess data
    offer_events, transaction_events = load_all_data()
    offer_events = preprocess_offer_events(offer_events)
    transaction_events = preprocess_transaction_events(transaction_events)

    if selected == "Home":
        show_home_page(offer_events, transaction_events)
    elif selected == "Customer Segments":
        customer_segments_page()
    elif selected == "Offer Performance":
        offer_performance_page()
    elif selected == "Transaction Analysis":
        transaction_analysis_page()

def show_home_page(offer_events, transaction_events):
    st.markdown('<p class="sub-header">Executive Summary</p>', unsafe_allow_html=True)
    st.write("""
    Our analysis of the Maven Rewards program has revealed several key insights that will drive our future marketing strategy:
    
    1. Customer segmentation has identified 5 distinct groups with varying preferences and behaviors.
    2. BOGO offers have shown the highest conversion rate across all customer segments.
    3. Email has proven to be the most effective channel for offer distribution.
    4. There's a strong positive correlation between offer views and transaction amounts.
    5. We've identified opportunities to increase Customer Lifetime Value through targeted promotions.
    """)

    st.markdown('<p class="sub-header">High-Level Metrics and KPIs</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-value">5</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Customer Segments</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        conversion_rate = offer_events[offer_events['event'] == 'offer completed'].shape[0] / offer_events[offer_events['event'] == 'offer received'].shape[0]
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{conversion_rate:.2%}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Overall Offer Conversion Rate</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        total_revenue = transaction_events['amount'].sum()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">${total_revenue:,.0f}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Total Revenue</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        avg_transaction = transaction_events['amount'].mean()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">${avg_transaction:.2f}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Average Transaction Amount</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p class="sub-header">Key Recommendations</p>', unsafe_allow_html=True)
    st.write("""
    Based on our analysis, we recommend the following strategies:
    
    1. Tailor offer types to customer segments, focusing on BOGO offers for high-value customers.
    2. Increase use of email for offer distribution while optimizing mobile and social channels.
    3. Implement a tiered rewards system based on customer lifetime value predictions.
    4. Develop a re-engagement campaign for the identified "at-risk" customer segment.
    5. Optimize offer duration and difficulty based on segment-specific performance data.
    """)

if __name__ == "__main__":
    main()