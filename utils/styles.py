def load_css():
    return """
    <style>
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #3e2a1e;
        margin-bottom: 2rem;
        text-align: center;
        animation: fadeInDown 1s ease;
    }
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
    .header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #3e2a1e;
        margin-bottom: 1rem;
        text-align: center;
        border-bottom: 2px solid #e0d9cf;
        padding-bottom: 0.5rem;
        animation: fadeInUp 1s ease;
    }
    .b-header {
        font-size: 1.8rem;
        font-weight: 500;
        color: #3e2a1e;  /* Deep Coffee */
        margin-bottom: 2rem;
        text-align: center;
        border-bottom: 1px solid #e0d9cf;
        padding-bottom: 0.5rem;
        animation: fadeInUp 1s ease;
    }
    .sub-header {
        font-size: 1.2rem;
        font-weight: 300;
        color: #3e2a1e;
        margin-bottom: 1rem;
        text-align: center;
        border-bottom: 2px solid #e0d9cf;
        padding-bottom: 0.5rem;
        animation: fadeInUp 1s ease;
    }
    .metric-card {
        background-color: #f9f5f0;
        border-radius: 15px;
        padding: 1.5rem;
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
        font-size: 2.2rem;
        font-weight: 700;
        color: #3e2a1e;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 1.1rem;
        color: #3e2a1e;
        margin-top: 0.5rem;
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
    """