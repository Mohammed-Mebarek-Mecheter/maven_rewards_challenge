# app.py
import streamlit as st
from streamlit_option_menu import option_menu
from pages.customer_segments import customer_segments_page
from pages.offer_performance import offer_performance_page
from pages.transaction_analysis import transaction_analysis_page
from utils.data_loader import load_all_data
from utils.data_processor import preprocess_offer_events, preprocess_transaction_events

# Set page config
st.set_page_config(page_title="Maven Rewards Challenge", page_icon=":coffee:", layout="wide")

# Custom CSS for Maven Cafe Rewards theme
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #3d2c1f; /* Dark Coffee */
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #5c3d2e; /* Olive Green */
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0e6db; /* Light Beige */
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #3d2c1f; /* Dark Coffee */
    }
    .metric-label {
        font-size: 1rem;
        color: #5c3d2e; /* Olive Green */
    }
    .button-primary {
        background-color: #3d2c1f; /* Dark Coffee */
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .button-primary:hover {
        background-color: #5c3d2e; /* Olive Green */
    }
    .sidebar .sidebar-content {
        background-color: #f0e6db; /* Light Beige */
    }
    .sidebar .sidebar-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #3d2c1f; /* Dark Coffee */
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_preprocess_data():
    offer_events, transaction_events = load_all_data()
    offer_events = preprocess_offer_events(offer_events)
    transaction_events = preprocess_transaction_events(transaction_events)
    return offer_events, transaction_events

def main():
    # Header with Maven Cafe logo and challenge title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://cdn.dribbble.com/userupload/4292674/file/original-73b8de0fd0cdd3e288a127e95e2cabc7.jpg?resize=752x", width=100)  # Replace with actual logo
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
    if 'offer_events' not in st.session_state or 'transaction_events' not in st.session_state:
        offer_events, transaction_events = load_and_preprocess_data()
        st.session_state['offer_events'] = offer_events
        st.session_state['transaction_events'] = transaction_events

    offer_events = st.session_state['offer_events']
    transaction_events = st.session_state['transaction_events']

    # Render selected page
    if selected == "Home":
        show_home_page(offer_events, transaction_events)
    elif selected == "Customer Segments":
        customer_segments_page(offer_events, transaction_events)
    elif selected == "Offer Performance":
        offer_performance_page(offer_events, transaction_events)
    elif selected == "Transaction Analysis":
        transaction_analysis_page(offer_events, transaction_events)


def show_home_page(offer_events, transaction_events):
    st.markdown('<p class="sub-header">Executive Summary</p>', unsafe_allow_html=True)
    st.write("""
    Our analysis of the Maven Rewards program has revealed several key insights that will drive our future marketing strategy:

    1. Customer segmentation has identified 4 distinct groups with varying preferences and behaviors.
    2. BOGO offers have shown the highest conversion rate across all customer segments.
    3. Informational offers have high view rates but need better reward strategies.
    4. Email has proven to be the most effective channel for offer distribution.
    5. There's a positive correlation between offer duration and completion rates, suggesting longer offers may be more effective.
    6. Average Customer Lifetime Value (CLV) is highest in Cluster 1, indicating the most valuable segment.
    """)

    st.markdown('<p class="sub-header">High-Level Metrics and KPIs</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-value">4</p>', unsafe_allow_html=True)  # Update to the actual number of customer segments
        st.markdown('<p class="metric-label">Customer Segments</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        conversion_rate = offer_events[offer_events['event'] == 'offer completed'].shape[0] / \
                          offer_events[offer_events['event'] == 'offer received'].shape[0]
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

    1. **Tailor offer types**: Focus on BOGO offers for high-value customers and use Informational offers with improved rewards to boost engagement.
    2. **Optimize channels**: Increase email distribution and explore enhancing mobile and social channels for better engagement.
    3. **Implement tiered rewards**: Develop a rewards system based on Customer Lifetime Value (CLV) predictions, focusing on Cluster 1.
    4. **Re-engage at-risk customers**: Create campaigns targeted at "at-risk" segments.
    5. **Adjust offer durations**: Use longer durations for offers to increase completion rates, while balancing difficulty levels to avoid discouraging customers.
    """)

if __name__ == "__main__":
    main()
