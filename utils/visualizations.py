# utils/visualizations.py
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def plot_age_distribution_violin(filtered_data):
    """Create a violin plot for age distribution."""
    primary_color = st.get_option("theme.primaryColor")
    return alt.Chart(filtered_data).transform_density(
        'age',
        as_=['age', 'density'],
        extent=[filtered_data['age'].min(), filtered_data['age'].max()]
    ).mark_area(color=primary_color).encode(
        x=alt.X('age:Q', title='Age'),
        y=alt.Y('density:Q', title='Density'),
        tooltip=[alt.Tooltip('age:Q', title='Age'), alt.Tooltip('density:Q', title='Density')]
    ).properties(title='')

@st.cache_data
def plot_income_distribution(filtered_data):
    """Create a boxplot for income distribution by gender."""
    return alt.Chart(filtered_data).mark_boxplot().encode(
        y=alt.Y('income:Q', title='Income'),
        x=alt.X('gender:N', title='Gender'),
        color=alt.Color('gender:N', scale=alt.Scale(scheme='browns'), legend=None),
        tooltip=[alt.Tooltip('income:Q', title='Income'), alt.Tooltip('gender:N', title='Gender')]
    ).properties(title='')

@st.cache_data
def plot_rfm_clusters(rfm_data):
    """Plot RFM clusters in a 2D scatter plot."""
    primary_color = st.get_option("theme.primaryColor")
    return alt.Chart(rfm_data).mark_circle(size=60).encode(
        x=alt.X('recency:Q', title='Recency (days)'),
        y=alt.Y('frequency:Q', title='Frequency (transactions)'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='browns'), title='Customer Segment'),
        size=alt.Size('monetary:Q', title='Monetary Value'),
        tooltip=['recency', 'frequency', 'monetary', 'cluster']
    ).properties(title='RFM Clusters').configure_mark(color=primary_color)

@st.cache_data
def plot_segment_distribution(rfm_data):
    primary_color = st.get_option("theme.primaryColor")
    return alt.Chart(rfm_data).mark_bar(color=primary_color).encode(
        x=alt.X('cluster:N', title='Customer Segment'),
        y=alt.Y('count()', title='Number of Customers'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='browns'), legend=None),
        tooltip=['cluster', alt.Tooltip('count()', title='Number of Customers')]
    ).properties(title='Customer Segment Distribution')

@st.cache_data
def plot_customer_segments_interactive(rfm_df):
    color_scale = [
        [0.0, '#f0e6db'], [0.1, '#e0d4c3'], [0.2, '#d1c2ab'], [0.3, '#c2b093'],
        [0.4, '#b39e7b'], [0.5, '#a48c63'], [0.6, '#957a4b'], [0.7, '#866833'],
        [0.8, '#77561b'], [0.9, '#684403'], [1.0, '#3d2c1f']
    ]

    fig = px.scatter_3d(
        rfm_df, x='recency', y='frequency', z='monetary',
        color='cluster', hover_name=rfm_df.index,
        hover_data={'recency': True, 'frequency': True, 'monetary': True, 'cluster': True},
        labels={'cluster': 'Customer Segment'},
        title='',
        color_continuous_scale=color_scale
    )

    fig.update_traces(marker=dict(size=5, opacity=0.8),
                      selector=dict(mode='markers'))

    return fig


@st.cache_data
def plot_offer_performance(performance_df):
    performance_pivot = performance_df['conversion_rate'].unstack()
    fig = px.imshow(performance_pivot,
                    labels=dict(x='Customer Segment', y='Offer Type', color='Conversion Rate'),
                    x=performance_pivot.columns,
                    y=performance_pivot.index,
                    color_continuous_scale='YlOrRd')

    fig.update_layout(title='Offer Performance by Type and Customer Segment')

    return fig

@st.cache_data
def plot_transaction_time_series(transaction_df, primary_color):
    transaction_df['time'] = pd.to_datetime(transaction_df['time'], unit='h')
    daily_transactions = transaction_df.set_index('time').resample('D')['amount'].sum().reset_index()

    fig = px.line(daily_transactions, x='time', y='amount',
                  labels={'time': 'Date', 'amount': 'Total Transaction Amount'},
                  title='Daily Transaction Amounts Over Time',
                  line_shape="spline")

    fig.update_traces(line_color=primary_color)
    fig.update_layout(xaxis_rangeslider_visible=True)

    return fig

# Updated to use the processed channels column
@st.cache_data
def plot_offer_completion_by_channel(offer_events_with_cluster):
    primary_color = st.get_option("theme.primaryColor")
    # Explode the channels column and group by channels and offer success
    offer_completion = offer_events_with_cluster.explode('channels').groupby(['channels', 'offer_success'])[
        'offer_id'].count().reset_index()

    return alt.Chart(offer_completion).mark_bar(color=primary_color).encode(
        x=alt.X('channels:N', title='Channel'),
        y=alt.Y('offer_id:Q', title='Count of Offers'),
        color=alt.Color('offer_success:N', title='Offer Completion', scale=alt.Scale(scheme='browns')),
        tooltip=[alt.Tooltip('channels:N', title='Channel'),
                 alt.Tooltip('offer_success:N', title='Offer Completion'),
                 alt.Tooltip('offer_id:Q', title='Count')]
    ).properties(title='')


@st.cache_data
def plot_weekly_transaction_trend(filtered_transactions):
    """Plot weekly transaction trend."""
    weekly_transactions = filtered_transactions.set_index('time').resample('W')['amount'].sum().reset_index()
    primary_color = st.get_option("theme.primaryColor")
    secondary_color = st.get_option("theme.backgroundColor")

    chart = alt.Chart(weekly_transactions).mark_area(
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
    return chart


@st.cache_data
def plot_basket_analysis(basket_data):
    """Plot basket analysis showing average basket size vs. transaction count."""
    scatter = alt.Chart(basket_data).mark_circle(size=60).encode(
        x=alt.X('transaction_count:Q', title='Number of Transactions'),
        y=alt.Y('avg_basket_size:Q', title='Average Basket Size ($)'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='browns'), title='Segment'),
        tooltip=['transaction_count', 'avg_basket_size', 'cluster']
    ).properties(title='Customer Segments based on Transaction Behavior')
    return scatter

@st.cache_data
def plot_clv_distribution(clv_data):
    """Plot the distribution of Customer Lifetime Value."""
    primary_color = st.get_option("theme.primaryColor")
    chart = alt.Chart(clv_data).mark_bar().encode(
        x=alt.X('total_spend:Q', bin=alt.Bin(maxbins=20), title='Total Spend ($)'),
        y=alt.Y('count()', title='Number of Customers'),
        color=alt.value(primary_color)
    ).properties(title='')
    return chart
@st.cache_data
def plot_transaction_forecast(forecast_df, historical_df):
    """Plot historical and forecasted transaction amounts."""
    primary_color = st.get_option("theme.primaryColor")
    forecast_chart = alt.Chart(forecast_df).mark_line(color=primary_color).encode(
        x='date:T',
        y='forecast:Q',
        tooltip=['date:T', 'forecast:Q']
    )
    historical_chart = alt.Chart(historical_df).mark_line(color='#6f4f28').encode(
        x='date:T',
        y='actual:Q',
        tooltip=['date:T', 'actual:Q']
    ).properties(title='Transaction Forecast')
    return historical_chart + forecast_chart

@st.cache_data
def plot_transaction_time_series(transaction_df):
    primary_color = st.get_option("theme.primaryColor")
    # Resample the data by hours instead of days
    hourly_transactions = transaction_df.set_index('time').resample('H')['amount'].sum().reset_index()
    # Create the figure with hourly data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hourly_transactions['time'], y=hourly_transactions['amount'],
                             mode='lines', name='Hourly Transactions',
                             line=dict(color=primary_color)))
    # Update layout to reflect hours on the x-axis
    fig.update_layout(
        title='Hourly Transaction Amounts Over Time',
        xaxis_title='Hours Passed',
        yaxis_title='Total Transaction Amount ($)',
        xaxis_rangeslider_visible=True
    )
    # Format the x-axis labels to display as hours passed since the start
    fig.update_xaxes(
        tickformat="%H",  # Formats as hours
        dtick=3600000  # Tick interval set to every hour (3600 seconds * 1000 ms)
    )
    return fig

@st.cache_data
def plot_segment_distribution(offer_events_with_cluster):
    primary_color = st.get_option("theme.primaryColor")
    rfm_data = offer_events_with_cluster['cluster'].value_counts().reset_index()
    rfm_data.columns = ['cluster', 'count']

    return alt.Chart(rfm_data).mark_bar(color=primary_color).encode(
        x=alt.X('cluster:N', title='Customer Segment'),
        y=alt.Y('count:Q', title='Number of Customers'),
        tooltip=['cluster', 'count']
    ).properties(title='')


@st.cache_data
def plot_channel_success_over_time(offer_events_with_cluster):
    primary_color = st.get_option("theme.primaryColor")
    offer_events_with_cluster['time'] = offer_events_with_cluster['time'].dt.hour
    exploded_df = offer_events_with_cluster.explode('channels')
    channel_success_over_time = exploded_df.groupby(['time', 'channels'])['offer_success'].mean().reset_index()

    return alt.Chart(channel_success_over_time).mark_line().encode(
        x=alt.X('time:Q', title='Time (hours)'),
        y=alt.Y('offer_success:Q', title='Success Rate', axis=alt.Axis(format='.0%')),
        color=alt.Color('channels:N', title='Channel', scale=alt.Scale(scheme='browns')),
        tooltip=['time', 'channels', 'offer_success']
    ).properties(title='')

@st.cache_data
def plot_segment_characteristics(cluster_stats):
    primary_color = st.get_option("theme.primaryColor")
    melted_stats = cluster_stats.reset_index().melt(id_vars='Segment', var_name='Metric', value_name='Value')

    chart = alt.Chart(melted_stats).mark_bar(color=primary_color).encode(
        x=alt.X('Segment:N', title='Customer Segment'),
        y=alt.Y('Value:Q', title='Value'),
        column=alt.Column('Metric:N', title=None),
        tooltip=['Segment', 'Metric', 'Value']
    ).properties(
        title='',
        width=200
    ).configure_view(
        strokeWidth=0  # Remove border around the chart
    )
    return chart

@st.cache_data
def create_correlation_heatmap(offer_data, rfm_data):
    # Merge offer data with RFM data
    merged_data = pd.merge(offer_data, rfm_data, left_on='customer_id', right_index=True)
    # Select relevant columns for correlation
    columns_for_correlation = ['age', 'income', 'recency', 'frequency', 'monetary']
    correlation_matrix = merged_data[columns_for_correlation].corr().reset_index().melt(id_vars='index')
    # Create heatmap
    heatmap = alt.Chart(correlation_matrix).mark_rect().encode(
        x=alt.X('index:O', title=None),
        y=alt.Y('variable:O', title=None),
        color=alt.Color('value:Q', title='Correlation', scale=alt.Scale(scheme='browns')),
        tooltip=['index', 'variable', 'value']
    ).properties(
        title='',
        width=400,
        height=400
    )
    return heatmap

@st.cache_data
def create_offer_distribution_by_age(offer_data):
    # Create age groups
    offer_data['age_group'] = pd.cut(offer_data['age'], bins=[0, 30, 45, 60, 100],
                                     labels=['18-30', '31-45', '46-60', '60+'])
    # Calculate distribution
    distribution = offer_data.groupby(['age_group', 'offer_type']).size().reset_index(name='count')
    distribution_percentage = distribution.groupby('age_group').apply(
        lambda x: x.assign(percentage=x['count'] / x['count'].sum())
    ).reset_index(drop=True)
    # Create stacked bar chart
    bar_chart = alt.Chart(distribution_percentage).mark_bar().encode(
        x=alt.X('age_group:N', title='Age Group'),
        y=alt.Y('percentage:Q', title='Percentage', axis=alt.Axis(format='.0%')),
        color=alt.Color('offer_type:N', title='Offer Type', scale=alt.Scale(scheme='browns')),
        tooltip=['age_group', 'offer_type', 'percentage']
    ).properties(
        title='',
        width=400,
        height=400
    ).configure_axis(
        labelAngle=0
    )
    return bar_chart

@st.cache_data
def plot_success_rate_by_offer_type(offer_events_with_cluster):
    primary_color = st.get_option("theme.primaryColor")
    success_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean().reset_index()
    return alt.Chart(success_rate).mark_bar(color=primary_color).encode(
        x=alt.X('offer_type:N', title='Offer Type', sort='-y'),
        y=alt.Y('offer_success:Q', title='Success Rate', axis=alt.Axis(format='.0%')),
        tooltip=[alt.Tooltip('offer_type:N', title='Offer Type'),
                 alt.Tooltip('offer_success:Q', title='Success Rate', format='.2%')]
    ).properties(title='')

@st.cache_data
def plot_offer_age_heatmap(offer_data):
    # Create age groups
    offer_data['age_group'] = pd.cut(offer_data['age'], bins=[0, 30, 45, 60, 100],
                                     labels=['18-30', '31-45', '46-60', '60+'])
    # Calculate distribution
    distribution = offer_data.groupby(['age_group', 'offer_type']).size().reset_index(name='count')
    distribution_percentage = distribution.groupby('age_group').apply(
        lambda x: x.assign(percentage=x['count'] / x['count'].sum())
    ).reset_index(drop=True)
    # Create heatmap
    chart = alt.Chart(distribution_percentage).mark_rect().encode(
        x=alt.X('age_group:N', title='Age Group'),
        y=alt.Y('offer_type:N', title='Offer Type'),
        color=alt.Color('percentage:Q', title='Percentage', scale=alt.Scale(scheme='browns')),
        tooltip=['age_group', 'offer_type', alt.Tooltip('percentage:Q', format='.2%')]
    ).properties(
        title='',
        width=600,
        height=400
    )
    return chart

@st.cache_data
def plot_grouped_bar_chart_age(offer_data):
    # Create age groups
    offer_data['age_group'] = pd.cut(offer_data['age'], bins=[0, 30, 45, 60, 100],
                                     labels=['18-30', '31-45', '46-60', '60+'])
    # Calculate distribution
    distribution = offer_data.groupby(['age_group', 'offer_type']).size().reset_index(name='count')
    # Create grouped bar chart
    chart = alt.Chart(distribution).mark_bar().encode(
        x=alt.X('age_group:N', title='Age Group'),
        y=alt.Y('count:Q', title='Number of Offers'),
        color=alt.Color('offer_type:N', title='Offer Type', scale=alt.Scale(scheme='browns')),
        column='offer_type:N',
        tooltip=['age_group', 'offer_type', 'count']
    ).properties(
        title='Offer Distribution by Age',
        width=50,
        height=150
    )
    return chart

@st.cache_data
def plot_stacked_area_chart(offer_data):
    # Create age groups
    offer_data['age_group'] = pd.cut(offer_data['age'], bins=[0, 30, 45, 60, 100],
                                     labels=['18-30', '31-45', '46-60', '60+'])
    # Calculate distribution
    distribution = offer_data.groupby(['age_group', 'offer_type']).size().reset_index(name='count')
    distribution_percentage = distribution.groupby('age_group').apply(
        lambda x: x.assign(percentage=x['count'] / x['count'].sum())
    ).reset_index(drop=True)
    # Create stacked area chart
    chart = alt.Chart(distribution_percentage).mark_area().encode(
        x=alt.X('age_group:N', title='Age Group'),
        y=alt.Y('percentage:Q', title='Percentage', stack='normalize', axis=alt.Axis(format='.0%')),
        color=alt.Color('offer_type:N', title='Offer Type', scale=alt.Scale(scheme='browns')),
        tooltip=['age_group', 'offer_type', alt.Tooltip('percentage:Q', format='.2%')]
    ).properties(
        title='',
        width=600,
        height=400
    )
    return chart

@st.cache_data
def plot_segment_heatmap(cluster_stats):
    # Melt the DataFrame
    melted_stats = cluster_stats.melt(id_vars='cluster', var_name='Metric', value_name='Value')
    # Create the heatmap
    chart = alt.Chart(melted_stats).mark_rect().encode(
        x='Metric:N',
        y='cluster:N',
        color=alt.Color('Value:Q', scale=alt.Scale(scheme='browns')),
        tooltip=['cluster', 'Metric', 'Value']
    ).properties(
        width=600,
        height=400,
        title=''
    )
    return chart

@st.cache_data
def plot_segment_characteristics(segment_data):
    """Plot characteristics of a specific segment."""
    melted_data = segment_data.melt(id_vars=['cluster'],
                                    value_vars=['recency', 'frequency', 'monetary'])
    chart = alt.Chart(melted_data).mark_boxplot().encode(
        x='variable:N',
        y='value:Q',
        color=alt.Color('variable:N', scale=alt.Scale(scheme='browns'))
    ).properties(title='Segment Characteristics')
    return chart

@st.cache_data
def plot_clv_distribution(clv_data):
    """Plot the distribution of Customer Lifetime Value."""
    chart = alt.Chart(clv_data).mark_bar().encode(
        x=alt.X('clv:Q', bin=alt.Bin(maxbins=20), title='Customer Lifetime Value'),
        y='count()',
        color=alt.value('#8B4513')  # Brown color
    ).properties(title='')
    return chart

@st.cache_data
def plot_success_rate_by_offer_type(offer_events_with_cluster):
    success_rate = offer_events_with_cluster.groupby('offer_type')['offer_success'].mean().reset_index()
    fig = px.bar(success_rate, x='offer_type', y='offer_success',
                 title='Success Rate by Offer Type',
                 labels={'offer_success': 'Success Rate', 'offer_type': 'Offer Type'},
                 color='offer_type')
    return fig

@st.cache_data
def plot_offer_performance_over_time(offer_events_with_cluster):
    performance_over_time = offer_events_with_cluster.groupby(['time', 'offer_type'])['offer_success'].mean().reset_index()
    fig = px.line(performance_over_time, x='time', y='offer_success', color='offer_type',
                  title='Offer Performance Over Time',
                  labels={'offer_success': 'Success Rate', 'time': 'Time', 'offer_type': 'Offer Type'})
    return fig

@st.cache_data
def plot_redemption_rate(redemption_rate):
    """Plot the redemption rate by offer type."""
    return alt.Chart(redemption_rate.reset_index()).mark_bar().encode(
        x=alt.X('offer_type:N', title='Offer Type'),
        y=alt.Y('offer_success:Q', title='Redemption Rate', axis=alt.Axis(format='.0%')),
        color=alt.Color('offer_type:N', legend=None)
    ).properties(title='Redemption Rate by Offer Type')

@st.cache_data
def plot_customer_retention_rate(retention_rate):
    """Plot customer retention rate over time."""
    return alt.Chart(retention_rate.reset_index()).mark_line().encode(
        x=alt.X('time:T', title='Date'),
        y=alt.Y('retention_rate:Q', title='Retention Rate', axis=alt.Axis(format='.0%'))
    ).properties(title='Customer Retention Rate Over Time')

@st.cache_data
def plot_time_to_redemption(time_to_redemption):
    """Plot distribution of time to redemption."""
    return alt.Chart(time_to_redemption.reset_index()).mark_bar().encode(
        x=alt.X('offer_type:N', title='Offer Type'),
        y=alt.Y('time_to_redemption:Q', title='Average Time to Redemption (Days)')
    ).properties(title='Time to Redemption by Offer Type')

@st.cache_data
def plot_churn_rate(churn_rate):
    """Plot churn rate by offer type and segment."""
    return alt.Chart(churn_rate.reset_index()).mark_bar().encode(
        x=alt.X('offer_type:N', title='Offer Type'),
        y=alt.Y('churn_rate:Q', title='Churn Rate', axis=alt.Axis(format='.0%')),
        color=alt.Color('offer_type:N', legend=None)
    ).properties(title='Churn Rate by Offer Type and Segment')

@st.cache_data
def plot_offer_response_time_distribution(response_time_distribution):
    """Plot offer response time distribution by segment."""
    return alt.Chart(response_time_distribution.reset_index()).mark_boxplot().encode(
        x=alt.X('cluster:N', title='Customer Segment'),
        y=alt.Y('time_to_redemption:Q', title='Response Time (Days)'),
        color=alt.Color('offer_type:N', legend=None)
    ).properties(title='Offer Response Time Distribution by Segment')
