# utils/visualizations.py
import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@st.cache_data
def plot_age_distribution(filtered_data):
    primary_color = st.get_option("theme.primaryColor")
    return alt.Chart(filtered_data).mark_bar(color=primary_color).encode(
        x=alt.X('age:Q', bin=alt.Bin(maxbins=20), title='Age'),
        y=alt.Y('count()', title='Number of Customers'),
        tooltip=[alt.Tooltip('age:Q', title='Age'), alt.Tooltip('count()', title='Number of Customers')]
    ).properties(title='Age Distribution')

@st.cache_data
def plot_income_distribution(filtered_data):
    return alt.Chart(filtered_data).mark_boxplot(size=50).encode(
        y=alt.Y('income:Q', title='Income'),
        x=alt.X('gender:N', title='Gender'),
        color=alt.Color('gender:N', scale=alt.Scale(scheme='browns'), legend=None),
        tooltip=[alt.Tooltip('income:Q', title='Income'), alt.Tooltip('gender:N', title='Gender')]
    ).properties(title='Income Distribution by Gender')

@st.cache_data
def plot_rfm_clusters(rfm_data):
    primary_color = st.get_option("theme.primaryColor")
    return alt.Chart(rfm_data).mark_circle(size=60).encode(
        x=alt.X('recency:Q', title='Recency (days)'),
        y=alt.Y('frequency:Q', title='Frequency (transactions)'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='browns'), title='Customer Segment'),
        size=alt.Size('monetary:Q', title='Monetary Value'),
        tooltip=['recency', 'frequency', 'monetary', 'cluster']
    ).properties(title='RFM Clusters').configure_mark(color=primary_color)

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

# Updated to use the processed channels column
@st.cache_data
def plot_channel_success_over_time(offer_events_with_cluster):
    primary_color = st.get_option("theme.primaryColor")
    offer_events_with_cluster['time'] = offer_events_with_cluster['time'].dt.hour
    exploded_df = offer_events_with_cluster.explode('channels')  # Explode the channels column
    channel_success_over_time = exploded_df.groupby(['time', 'channels'])['offer_success'].mean().reset_index()

    return alt.Chart(channel_success_over_time).mark_line(color=primary_color).encode(
        x=alt.X('time:T', title='Date'),
        y=alt.Y('offer_success:Q', title='Success Rate', axis=alt.Axis(format='.0%')),
        color=alt.Color('channels:N', title='Channel'),
        tooltip=[alt.Tooltip('time:T', title='Date'),
                 alt.Tooltip('channels:N', title='Channel'),
                 alt.Tooltip('offer_success:Q', title='Success Rate', format='.2%')]
    ).properties(title='Channel Success Rate Over Time')

@st.cache_data
def plot_segment_distribution(rfm_data):
    primary_color = st.get_option("theme.primaryColor")
    return alt.Chart(rfm_data).mark_bar(color=primary_color).encode(
        x=alt.X('cluster:N', title='Customer Segment'),
        y=alt.Y('count()', title='Number of Customers'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='category10'), legend=None),
        tooltip=['cluster', alt.Tooltip('count()', title='Number of Customers')]
    ).properties(title='Customer Segment Distribution')

@st.cache_data
def plot_customer_segments_interactive(rfm_df):
    fig = px.scatter_3d(
        rfm_df, x='recency', y='frequency', z='monetary',
        color='cluster', hover_name=rfm_df.index,
        hover_data={'recency': True, 'frequency': True, 'monetary': True, 'cluster': True},
        labels={'cluster': 'Customer Segment'},
        title='Interactive 3D Customer Segments'
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
    primary_color = st.get_option("theme.primaryColor")
    secondary_color = st.get_option("theme.backgroundColor")
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

@st.cache_data
def plot_basket_analysis(basket_data):
    primary_color = st.get_option("theme.primaryColor")
    scatter = alt.Chart(basket_data).mark_circle(size=60).encode(
        x=alt.X('transaction_count:Q', title='Number of Transactions'),
        y=alt.Y('avg_basket_size:Q', title='Average Basket Size ($)'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='browns'), title='Segment'),
        tooltip=['transaction_count', 'avg_basket_size', 'cluster']
    ).properties(title='Customer Segments based on Transaction Behavior')
    scatter = scatter.configure_mark(color=primary_color)
    return scatter

@st.cache_data
def plot_clv_distribution(clv_data):
    primary_color = st.get_option("theme.primaryColor")
    return alt.Chart(clv_data).mark_bar().encode(
        x=alt.X('total_spend:Q', bin=alt.Bin(maxbins=20), title='Total Spend ($)'),
        y=alt.Y('count()', title='Number of Customers'),
        color=alt.value(primary_color)
    ).properties(title='')


import plotly.graph_objects as go
import streamlit as st


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
    ).properties(title='Number of Customers for each Segment')


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
        title='Segment Characteristics',
        width=200
    ).configure_view(
        strokeWidth=0  # Remove border around the chart
    )

    return chart


def plot_segment_radar(cluster_stats):
    melted_stats = cluster_stats.reset_index().melt(id_vars='Segment', var_name='Metric', value_name='Value')

    base = alt.Chart(melted_stats).encode(
        theta=alt.Theta('Metric:N', type='nominal'),
        radius=alt.Radius('Value:Q', scale=alt.Scale(type='sqrt', zero=True, nice=False)),
        tooltip=['Segment', 'Metric', 'Value']
    )

    chart = base.mark_line(point=True).encode(
        opacity=alt.value(0.7)
    ).properties(
        width=400,
        height=400,
        title='Segment Characteristics Radar'
    )

    return chart