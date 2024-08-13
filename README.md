# Maven Rewards Analysis App

## Overview

This Streamlit app is developed as part of the Maven Rewards Challenge, where we analyze customer behavior and the effectiveness of different promotional offers sent to rewards members over a 30-day period. The objective of the analysis is to identify key customer segments and develop a data-driven strategy for future promotional messaging and targeting.

The app provides an interactive interface for exploring customer segments, offer performance, and transaction patterns. It is designed to assist in strategic decision-making for marketing and promotions.

## Data Sources

The analysis is based on three primary datasets:

1. **Offers Data**: Contains details about the promotional offers sent to customers, including offer type, difficulty, reward, duration, and the marketing channels used.
2. **Customers Data**: Includes demographic information about each customer, such as gender, age, income, and the date they became a member.
3. **Events Data**: Records customer activities, including transactions, offers received, viewed, and completed, with associated details like the offer ID and transaction amounts.

## Data Cleaning and Preparation

The raw data underwent several cleaning and preparation steps:

1. **Data Loading**: Loaded three CSV files—`customers.csv`, `events.csv`, and `offers.csv`.
2. **Customers Data Cleaning**:
   - Converted the `became_member_on` field to datetime format.
   - Filled missing `gender` values with 'Unknown'.
   - Capped `age` values above 100 to the median age.
   - Addressed outliers in `income` using the Interquartile Range (IQR) method and filled missing values with the median income.
3. **Events Data Cleaning**:
   - Converted the `value` column from a string to a dictionary.
   - Extracted `offer_id` and `amount` from the `value` column.
   - Removed the original `value` column.
4. **Offers Data Cleaning**:
   - Converted the `channels` field from a string to a list format.
5. **Data Merging**:
   - Merged the cleaned events data with the customers data and then merged the result with the offers data.
6. **Outlier Handling**:
   - Applied percentile capping to the `amount` column (1st to 99th percentile).
7. **Event Type Separation**:
   - Separated the merged dataset into offer events and transaction events for more focused analysis.

You will find the raw data in here: [Maven Rewards Challenge](https://mavenanalytics.io/challenges/maven-rewards-challenge/404c6060-60eb-400f-9bce-c3b9f97e9d5a)
## App Features

### 1. **Customer Segments**
   - **Interactive Segment Explorer**: Allows users to explore different customer segments based on RFM (Recency, Frequency, Monetary) analysis.
   - **Demographic Insights**: Provides visualizations of age distribution and income distribution by gender for each segment.

### 2. **Offer Performance**
   - **Key Insights**: Displays the top-performing offer types, best-responding customer segments, and most effective marketing channels.
   - **Detailed Data View**: Presents a comprehensive view of offer interactions, including the success rate by offer type and channel effectiveness.

### 3. **Transaction Analysis**
   - **Transaction Trends**: Analyzes daily and weekly transaction patterns.
   - **Customer Segmentation**: Segments customers based on transaction behavior and visualizes the results.
   - **Customer Lifetime Value (CLV) Analysis**: Calculates and displays CLV for different customer segments.

### 4. **Report Generation**
   - The app allows users to generate PDF reports summarizing the analysis, which can be downloaded for further review.

## How to Run the App

### Prerequisites

- Python 3.11 or higher
- Streamlit and required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mohammed-Mebarek-Mecheter/maven_rewards_challenge.git
   cd maven_rewards_challenge
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

### Deployment

The app can be deployed on Streamlit Cloud or any other platform that supports Python and Streamlit. For deployment on Streamlit Cloud:

1. Link your GitHub repository to Streamlit Cloud.
2. Set the app's entry point to `app.py`.
3. Configure the environment variables, if any, in the Streamlit Cloud settings.
4. Deploy the app.

The app is currently live and accessible at [Maven Rewards Analysis App](https://mavencafe.streamlit.app/).

## License

This project is licensed under the MIT License.

## Acknowledgments

Special thanks to the Maven Cafe team for providing the datasets and the opportunity to work on this analysis. The insights derived from this analysis aim to enhance customer engagement and optimize promotional strategies.
