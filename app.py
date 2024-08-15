import streamlit as st
from streamlit_option_menu import option_menu
from src.customer_segments import customer_segments_page
from src.offer_performance import offer_performance_page
from src.transaction_analysis import transaction_analysis_page
from utils.data_loader import load_all_data
from utils.data_processor import preprocess_offer_events, preprocess_transaction_events

# Set page config
st.set_page_config(page_title="Maven Rewards Challenge", page_icon=":coffee:", layout="wide")

st.markdown("""
    <style>
    /* General Layout */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e0d9cf; /* Light Coffee for elegant separation */
    }
    .header-container img {
        align-self: flex-start;
        width: 100px;
        margin-right: 1rem;
    }
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #3e2a1e;  /* Deep Coffee */
        margin-bottom: 0.5rem;
        text-align: center;
        width: 100%;
        animation: fadeInDown 1s ease;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 500;
        color: #3e2a1e;  /* Deep Coffee */
        margin-bottom: 2rem;
        text-align: center;
        border-bottom: 1px solid #e0d9cf;
        padding-bottom: 0.5rem;
        animation: fadeInUp 1s ease;
    }
    /* Metric Cards */
    .metric-card {
        background-color: #f9f5f0;  /* Ivory */
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
        cursor: pointer;
        transform-origin: center;
    }
    .metric-card:hover {
        transform: scale(1.1);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #3e2a1e;  /* Deep Coffee */
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 1.2rem;
        color: #3e2a1e;  /* Deep Coffee */
        margin-top: 0.5rem;
    }
    /* Section Divider */
    .section-divider {
        margin: 3rem 0;
        border-bottom: 2px solid #e0d9cf;
        animation: fadeIn 1s ease;
    }
    /* Fade-in Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    /* Option Menu Styling */
    .option-menu-container {
        margin-top: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e0d9cf;
    }
    .st-emotion-cache-gvyv8g {
        color: #000;  /* Deep Coffee */
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
    with st.container():
        div1, div2 = st.columns([1, 5])

        with div1:
            st.image("https://images.ctfassets.net/p80c52b4itd3/3tay5qlhYeC8yxOQJXmv4v/11eaa9683c8b34d513aae63f9fd26297/barista.jpg", width=100)
        with div2:
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
        styles={
            "container": {"padding": "0!important", "background-color": "#f0e6db", "border-radius": "10px"},
            "icon": {"color": "#3d2c1f", "font-size": "16px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eae0d5"},
            "nav-link-selected": {"background-color": "#3d2c1f", "color": "white"},
        },
    )

    # Load and preprocess data
    offer_events, transaction_events = load_and_preprocess_data()

    # Render selected page
    if selected == "Home":
        show_home_page(offer_events, transaction_events)
    elif selected == "Customer Segments":
        customer_segments_page()
    elif selected == "Offer Performance":
        offer_performance_page()
    elif selected == "Transaction Analysis":
        transaction_analysis_page(offer_events, transaction_events)


def show_home_page(offer_events, transaction_events):

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f'{len(offer_events["customer_id"].unique()):,}' +
                    '</div><div class="metric-label">Total Customers</div></div>',
                    unsafe_allow_html=True)

    with col2:
        conversion_rate = offer_events[offer_events['event'] == 'offer completed'].shape[0] / \
                          offer_events[offer_events['event'] == 'offer received'].shape[0]
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f'{conversion_rate:.2%}' +
                    '</div><div class="metric-label">Overall Offer Conversion Rate</div></div>',
                    unsafe_allow_html=True)

    with col3:
        total_revenue = transaction_events['amount'].sum()
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f'${total_revenue:,.0f}' +
                    '</div><div class="metric-label">Total Revenue</div></div>',
                    unsafe_allow_html=True)

    with col4:
        avg_transaction = transaction_events['amount'].mean()
        st.markdown('<div class="metric-card"><div class="metric-value">' +
                    f'${avg_transaction:.2f}' +
                    '</div><div class="metric-label">Average Transaction Amount</div></div>',
                    unsafe_allow_html=True)

    # Elegant separation between metrics and summary
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<p class="sub-header">Executive Summary</p>', unsafe_allow_html=True)
        st.write("""
                Our analysis of the Maven Rewards program has revealed several key insights that will drive our future marketing strategy:

                1. Customer segmentation has identified distinct groups with varying preferences and behaviors.
                2. BOGO offers have shown the highest conversion rate across all customer segments.
                3. Informational offers have high view rates but need better reward strategies.
                4. Web has proven to be the most effective channel for offer distribution.
                5. There's a positive correlation between offer duration and completion rates.
                6. Customer Lifetime Value (CLV) varies significantly across segments.
                """)

    with col6:
        st.markdown('<p class="sub-header">Key Recommendations</p>', unsafe_allow_html=True)
        st.write("""
            Based on our analysis, we recommend the following strategies:

            1. Tailor offer types to customer segments, focusing on BOGO offers for high-value customers.
            2. Optimize email distribution and explore enhancing mobile and social channels.
            3. Implement a tiered rewards system based on Customer Lifetime Value (CLV) predictions.
            4. Create targeted campaigns for "at-risk" segments to improve retention.
            5. Adjust offer durations to increase completion rates while maintaining engagement.
                    """)

    # Final elegant separation
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
