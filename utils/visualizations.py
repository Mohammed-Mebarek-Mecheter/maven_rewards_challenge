# utils/visualizations.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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

def plot_offer_performance(performance_df):
    performance_pivot = performance_df['conversion_rate'].unstack()
    fig = px.imshow(performance_pivot,
                    labels=dict(x='Customer Segment', y='Offer Type', color='Conversion Rate'),
                    x=performance_pivot.columns,
                    y=performance_pivot.index,
                    color_continuous_scale='YlOrRd')

    fig.update_layout(title='Offer Performance by Type and Customer Segment')

    return fig

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
