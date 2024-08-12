# utils/visualizations.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def plot_customer_segments(rfm_df):
    """
    Create a 3D scatter plot of customer segments.
    """
    fig = px.scatter_3d(rfm_df, x='recency', y='frequency', z='monetary',
                        color='cluster', hover_name=rfm_df.index,
                        labels={'cluster': 'Segment'})

    fig.update_layout(scene=dict(xaxis_title='Recency',
                                 yaxis_title='Frequency',
                                 zaxis_title='Monetary'),
                      title='Customer Segments')

    return fig

def plot_offer_performance(performance_df):
    """
    Create a heatmap of offer performance by type and customer segment.
    """
    performance_pivot = performance_df['conversion_rate'].unstack()
    fig = px.imshow(performance_pivot,
                    labels=dict(x='Customer Segment', y='Offer Type', color='Conversion Rate'),
                    x=performance_pivot.columns,
                    y=performance_pivot.index,
                    color_continuous_scale='YlOrRd')

    fig.update_layout(title='Offer Performance by Type and Customer Segment')

    return fig

def plot_transaction_time_series(transaction_df):
    """
    Create a time series plot of transaction amounts.
    """
    daily_transactions = transaction_df.set_index('time').resample('D')['amount'].sum().reset_index()

    fig = px.line(daily_transactions, x='time', y='amount',
                  labels={'time': 'Date', 'amount': 'Total Transaction Amount'},
                  title='Daily Transaction Amounts Over Time')

    fig.update_layout(xaxis_rangeslider_visible=True)

    return fig

def plot_channel_effectiveness(offer_df):
    """
    Create a stacked bar chart of offer success rates by channel.
    """
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

# Add more visualization functions as needed