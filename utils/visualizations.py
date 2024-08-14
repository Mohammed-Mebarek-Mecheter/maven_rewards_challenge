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
        color=alt.Color('gender:N', scale=alt.Scale(scheme='viridis'), legend=None),
        tooltip=[alt.Tooltip('income:Q', title='Income'), alt.Tooltip('gender:N', title='Gender')]
    ).properties(title='Income Distribution by Gender')

@st.cache_data
def plot_rfm_clusters(rfm_data):
    primary_color = st.get_option("theme.primaryColor")
    return alt.Chart(rfm_data).mark_circle(size=60).encode(
        x=alt.X('recency:Q', title='Recency (days)'),
        y=alt.Y('frequency:Q', title='Frequency (transactions)'),
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='category10'), title='Customer Segment'),
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
    ).properties(title='Offer Success Rate by Type')


@st.cache_data
def plot_channel_effectiveness(offer_events_with_cluster):
    channel_data = offer_events_with_cluster.explode('channels').groupby('channels').agg({
        'offer_success': 'mean',
        'customer_id': 'count'
    }).reset_index()

    fig = go.Figure(data=[go.Scatter(
        x=channel_data['channels'],
        y=channel_data['offer_success'],
        mode='markers',
        marker=dict(
            size=channel_data['customer_id'] / channel_data['customer_id'].max() * 50,
            color=channel_data['offer_success'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Success Rate')
        ),
        text=[f"Channel: {ch}<br>Success Rate: {sr:.1%}<br>Customers: {ct}"
              for ch, sr, ct in
              zip(channel_data['channels'], channel_data['offer_success'], channel_data['customer_id'])],
        hoverinfo='text'
    )])

    fig.update_layout(
        title='Channel Effectiveness and Reach',
        xaxis_title='Channel',
        yaxis_title='Success Rate',
        yaxis=dict(tickformat='.0%'),
        height=500
    )

    return fig

@st.cache_data
def plot_segment_distribution(rfm_data):
    return alt.Chart(rfm_data).mark_bar().encode(
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

@st.cache_data
def plot_channel_effectiveness(offer_df):
    channel_success = offer_df.groupby('channels')['offer_success'].agg(['mean', 'count'])
    channel_success.columns = ['success_rate', 'total_offers']

    fig = go.Figure()
    fig.add_trace(go.Bar(x=channel_success.index, y=channel_success['success_rate'],
                         name='Success Rate', marker_color='green'))
    fig.add_trace(go.Bar(x=channel_success.index, y=1 - channel_success['success_rate'],
                         name='Failure Rate', marker_color='red'))

    fig.update_layout(barmode='stack', title='Offer Success Rates by Channel',
                      xaxis_title='Channel', yaxis_title='Rate')

    return fig


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
        color=alt.Color('cluster:N', scale=alt.Scale(scheme='dark2'), title='Segment'),
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

@st.cache_data
def plot_transaction_time_series(transaction_df):
    primary_color = st.get_option("theme.primaryColor")
    daily_transactions = transaction_df.set_index('time').resample('D')['amount'].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_transactions['time'], y=daily_transactions['amount'],
                             mode='lines', name='Daily Transactions',
                             line=dict(color=primary_color)))

    fig.update_layout(
        title='Daily Transaction Amounts Over Time',
        xaxis_title='Date',
        yaxis_title='Total Transaction Amount ($)',
        xaxis_rangeslider_visible=True
    )

    return fig