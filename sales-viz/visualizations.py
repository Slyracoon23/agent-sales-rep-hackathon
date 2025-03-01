import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

def create_pass_rate_gauge(pass_rate: str) -> go.Figure:
    """Create a gauge chart showing the pass rate."""
    # Extract numeric value from pass rate string
    try:
        value = float(pass_rate.replace('%', ''))
    except (ValueError, AttributeError):
        value = 0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Pass Rate"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, 90], 'color': "yellow"},
                {'range': [90, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig

def create_simulation_results_table(df: pd.DataFrame) -> go.Figure:
    """Create a table showing simulation results."""
    if df.empty:
        return go.Figure()
    
    # Format duration as seconds with 2 decimal places
    if 'duration' in df.columns:
        df['duration'] = df['duration'].apply(lambda x: f"{x/1000:.2f}s")
    
    # Create a more readable table
    table_df = df[['simulationNumber', 'startIndex', 'overallPassed', 
                   'salesAgentPassed', 'customerAgentPassed', 'duration']].copy()
    
    table_df.columns = ['Simulation #', 'Start Index', 'Overall Result', 
                        'Sales Agent', 'Customer Agent', 'Duration']
    
    # Convert boolean values to Pass/Fail
    for col in ['Overall Result', 'Sales Agent', 'Customer Agent']:
        table_df[col] = table_df[col].map({True: '✅ Pass', False: '❌ Fail'})
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(table_df.columns),
            fill_color='paleturquoise',
            align='left',
            font=dict(size=14)
        ),
        cells=dict(
            values=[table_df[col] for col in table_df.columns],
            fill_color=[['white', 'lightgrey'] * len(table_df)],
            align='left',
            font=dict(size=12),
            height=30
        )
    )])
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(150, min(50 * len(table_df) + 50, 400))
    )
    
    return fig

def create_conversation_flow(conversation_df: pd.DataFrame) -> go.Figure:
    """Create a visualization of conversation flow with message lengths."""
    if conversation_df.empty:
        return go.Figure()
    
    # Create a figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add message length bars
    fig.add_trace(
        go.Bar(
            x=conversation_df['turn_number'],
            y=conversation_df['message_length'],
            name="Message Length",
            marker_color=conversation_df['agent'].map({
                'Sales Agent': 'royalblue',
                'Customer': 'firebrick'
            }),
            opacity=0.7,
            hovertemplate="Turn %{x}<br>Length: %{y} chars<br>%{text}",
            text=conversation_df['agent']
        ),
        secondary_y=False,
    )
    
    # Add agent indicators
    sales_turns = conversation_df[conversation_df['agent'] == 'Sales Agent']['turn_number']
    customer_turns = conversation_df[conversation_df['agent'] == 'Customer']['turn_number']
    
    # Add agent indicators as scatter points
    fig.add_trace(
        go.Scatter(
            x=sales_turns,
            y=[1] * len(sales_turns),
            mode='markers',
            name='Sales Agent',
            marker=dict(
                symbol='circle',
                size=12,
                color='royalblue'
            ),
            showlegend=True
        ),
        secondary_y=True
    )
    
    fig.add_trace(
        go.Scatter(
            x=customer_turns,
            y=[0] * len(customer_turns),
            mode='markers',
            name='Customer',
            marker=dict(
                symbol='circle',
                size=12,
                color='firebrick'
            ),
            showlegend=True
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title="Conversation Flow",
        xaxis_title="Turn Number",
        yaxis_title="Message Length (chars)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )
    
    # Update secondary y-axis
    fig.update_yaxes(
        title_text="Agent",
        secondary_y=True,
        showticklabels=False,
        range=[-0.5, 1.5]
    )
    
    return fig

def create_message_length_comparison(conversation_stats_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart comparing message lengths between agents across simulations."""
    if conversation_stats_df.empty:
        return go.Figure()
    
    # Prepare data for grouped bar chart
    fig = go.Figure()
    
    # Add bars for sales agent average message length
    fig.add_trace(go.Bar(
        x=conversation_stats_df['simulation_id'],
        y=conversation_stats_df['avg_sales_length'],
        name='Sales Agent Avg',
        marker_color='royalblue',
        opacity=0.7
    ))
    
    # Add bars for customer average message length
    fig.add_trace(go.Bar(
        x=conversation_stats_df['simulation_id'],
        y=conversation_stats_df['avg_customer_length'],
        name='Customer Avg',
        marker_color='firebrick',
        opacity=0.7
    ))
    
    # Update layout
    fig.update_layout(
        title="Average Message Length by Agent",
        xaxis_title="Simulation ID",
        yaxis_title="Average Length (chars)",
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_conversation_heatmap(conversation_df: pd.DataFrame) -> go.Figure:
    """Create a heatmap visualization of the conversation."""
    if conversation_df.empty:
        return go.Figure()
    
    # Create a matrix for the heatmap
    # Rows are turns, columns are: [Agent, Message Length]
    agent_map = {'Sales Agent': 1, 'Customer': 0}
    
    # Create the heatmap data
    heatmap_data = np.zeros((len(conversation_df), 2))
    for i, row in conversation_df.iterrows():
        heatmap_data[i, 0] = agent_map[row['agent']]
        heatmap_data[i, 1] = min(1, row['message_length'] / 500)  # Normalize message length
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.T,
        x=conversation_df['turn_number'],
        y=['Agent', 'Length'],
        colorscale=[
            [0, 'firebrick'],  # Customer
            [0.5, 'white'],    # Neutral
            [1, 'royalblue']   # Sales Agent
        ],
        showscale=False,
        hovertemplate="Turn %{x}<br>%{customdata}",
        customdata=[[
            f"{'Sales Agent' if row['agent'] == 'Sales Agent' else 'Customer'}<br>{row['message_length']} chars"
        ] for _, row in conversation_df.iterrows()]
    ))
    
    # Update layout
    fig.update_layout(
        title="Conversation Heatmap",
        xaxis_title="Turn Number",
        yaxis=dict(
            tickvals=[0, 1],
            ticktext=['Agent', 'Length']
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=200
    )
    
    return fig

def create_historical_pass_rates(historical_df: pd.DataFrame) -> go.Figure:
    """Create a line chart showing historical pass rates."""
    if historical_df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # Add pass rate line
    fig.add_trace(go.Scatter(
        x=historical_df['timestamp'],
        y=historical_df['pass_rate'],
        mode='lines+markers',
        name='Pass Rate',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    # Add total simulations line
    fig.add_trace(go.Scatter(
        x=historical_df['timestamp'],
        y=historical_df['total_simulations'],
        mode='lines+markers',
        name='Total Simulations',
        line=dict(color='blue', width=2, dash='dash'),
        marker=dict(size=6),
        yaxis='y2'
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title="Historical Pass Rates",
        xaxis_title="Test Run",
        yaxis=dict(
            title="Pass Rate (%)",
            range=[0, 100]
        ),
        yaxis2=dict(
            title="Total Simulations",
            overlaying='y',
            side='right',
            range=[0, max(historical_df['total_simulations']) * 1.2]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_feedback_wordcloud(feedback_list: List[str]) -> go.Figure:
    """Create a simple word frequency visualization for feedback."""
    if not feedback_list or all(not feedback for feedback in feedback_list):
        return go.Figure()
    
    # Combine all feedback
    all_feedback = ' '.join(feedback_list)
    
    # Simple word frequency analysis
    words = all_feedback.lower().split()
    # Remove common words
    stop_words = {'the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'was', 'for', 'with', 'their', 'they', 'their'}
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    top_words = sorted_words[:20]  # Take top 20 words
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=[word[0] for word in top_words],
            y=[word[1] for word in top_words],
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title="Common Words in Feedback",
        xaxis_title="Word",
        yaxis_title="Frequency",
        margin=dict(l=20, r=20, t=50, b=20),
        height=300
    )
    
    return fig

def create_simulation_duration_chart(metadata_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing simulation durations."""
    if metadata_df.empty:
        return go.Figure()
    
    # Sort by simulation ID
    metadata_df = metadata_df.sort_values('simulation_id')
    
    # Create the bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=metadata_df['simulation_id'],
            y=metadata_df['duration'],
            marker_color=metadata_df['passed'].map({True: 'green', False: 'red'}),
            text=metadata_df['passed'].map({True: '✅', False: '❌'}),
            hovertemplate="Simulation #%{x}<br>Duration: %{y:.2f}s<br>Result: %{text}"
        )
    ])
    
    # Update layout
    fig.update_layout(
        title="Simulation Durations",
        xaxis_title="Simulation ID",
        yaxis_title="Duration (seconds)",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig 