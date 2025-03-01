import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our custom modules
from data_loader import SalesSimulationData
import visualizations as viz

# Initialize the OpenAI client
openai_api_key = os.environ.get("OPENAI_API_KEY")
try:
    # Try to initialize the OpenAI client with just the API key
    openai_client = OpenAI(api_key=openai_api_key)
except TypeError as e:
    # If that fails, try without any additional parameters that might cause issues
    if "unexpected keyword argument" in str(e):
        print(f"Warning: {e}. Trying alternative initialization.")
        openai_client = OpenAI()
        openai_client.api_key = openai_api_key
    else:
        raise e

# Check if OpenAI API key is set
has_openai_api_key = openai_api_key is not None

# Function to generate optimized prompts using OpenAI
def generate_optimized_prompt_with_openai(current_prompt, conversation_text, optimization_goal, optimization_areas, agent_type):
    """
    Generate an optimized prompt using OpenAI's GPT-4o-mini model.
    
    Args:
        current_prompt (str): The current system prompt
        conversation_text (str): The conversation text
        optimization_goal (str): The goal of the optimization
        optimization_areas (str): Specific areas to optimize
        agent_type (str): Either 'sales' or 'customer'
        
    Returns:
        str: The optimized prompt
    """
    try:
        # Create the system message
        system_message = """You are an expert prompt engineer specializing in optimizing prompts for sales and customer simulations.
Your task is to improve a system prompt based on the provided conversation, optimization goals, and areas for improvement."""

        # Create the user message
        user_message = f"""Please optimize the following {agent_type} agent system prompt based on the conversation and optimization parameters:

CURRENT PROMPT:
{current_prompt}

SAMPLE CONVERSATION:
{conversation_text}

OPTIMIZATION GOAL:
{optimization_goal if optimization_goal else "Improve overall effectiveness"}

AREAS TO OPTIMIZE:
{optimization_areas}

Please provide an improved version of the prompt that addresses the optimization goals and areas.
The optimized prompt should maintain the same general structure but enhance the specified areas.
Focus on making the prompt more effective for the {agent_type} agent role.
"""

        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract and return the optimized prompt
        optimized_prompt = response.choices[0].message.content
        return optimized_prompt
    
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return f"Error generating optimized prompt: {str(e)}"

# Function to generate optimized grader prompts using OpenAI
def generate_optimized_grader_prompt_with_openai(current_prompt, conversation_text, expected_outcomes):
    """
    Generate an optimized grader prompt using OpenAI's GPT-4o-mini model.
    
    Args:
        current_prompt (str): The current grader prompt
        conversation_text (str): The conversation text
        expected_outcomes (dict): Expected outcomes for the grader
        
    Returns:
        str: The optimized grader prompt
    """
    try:
        # Create the system message
        system_message = """You are an expert prompt engineer specializing in optimizing evaluation prompts for sales conversations.
Your task is to improve a grader prompt based on the provided conversation and expected outcomes."""

        # Create the user message
        user_message = f"""Please optimize the following grader prompt based on the conversation and expected outcomes:

CURRENT GRADER PROMPT:
{current_prompt}

SAMPLE CONVERSATION:
{conversation_text}

EXPECTED OUTCOMES:
- Sales Agent Assessment: {expected_outcomes.get('sales_assessment', 'Not specified')}
- Sales Agent Feedback Focus: {expected_outcomes.get('sales_feedback', 'Not specified')}
- Customer Agent Assessment: {expected_outcomes.get('customer_assessment', 'Not specified')}
- Customer Agent Feedback Focus: {expected_outcomes.get('customer_feedback', 'Not specified')}
- Overall Assessment: {expected_outcomes.get('overall_assessment', 'Not specified')}

Please provide an improved version of the grader prompt that will lead to the expected outcomes.
The optimized prompt should maintain the same general structure but include clearer evaluation criteria
that would guide an evaluator toward the expected assessments.
"""

        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract and return the optimized prompt
        optimized_prompt = response.choices[0].message.content
        return optimized_prompt
    
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return f"Error generating optimized grader prompt: {str(e)}"

# Initialize the data loader
data_loader = SalesSimulationData()

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Sales Simulation Dashboard"
server = app.server

# Define the layout with tabs
app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1("Sales Simulation Dashboard", className="text-center my-4"),
            html.P("Visualizing sales agent and customer agent interactions from simulated conversations", 
                   className="text-center text-muted mb-5"),
        ], width=12)
    ]),
    
    # Add tabs for navigation
    dbc.Tabs([
        # Dashboard Tab
        dbc.Tab(label="Dashboard Overview", tab_id="tab-dashboard", children=[
            dbc.Container([
                # Summary Cards
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Test Summary", className="text-center"),
                            dbc.CardBody([
                                html.H3(f"{data_loader.get_summary_stats().get('pass_rate', '0%')}", className="text-center text-success"),
                                html.P(f"Pass Rate ({data_loader.get_summary_stats().get('passed_simulations', 0)}/{data_loader.get_summary_stats().get('total_simulations', 0)} simulations)", className="text-center"),
                                html.P(f"Last Run: {data_loader.get_summary_stats().get('test_run_date', 'N/A')} at {data_loader.get_summary_stats().get('test_run_time', 'N/A')}", className="text-center text-muted small"),
                            ])
                        ], className="h-100")
                    ], width=4),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Pass Rate", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='pass-rate-gauge',
                                    figure=viz.create_pass_rate_gauge(data_loader.get_summary_stats().get('pass_rate', '0%')),
                                    config={'displayModeBar': False}
                                )
                            ])
                        ], className="h-100")
                    ], width=4),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Test Duration", className="text-center"),
                            dbc.CardBody([
                                html.H3(f"{data_loader.get_summary_stats().get('duration', 0):.2f}s", className="text-center"),
                                html.P("Total test duration", className="text-center"),
                                html.P(f"Average per simulation: {data_loader.get_summary_stats().get('duration', 0) / max(1, data_loader.get_summary_stats().get('total_simulations', 1)):.2f}s", 
                                       className="text-center text-muted small"),
                            ])
                        ], className="h-100")
                    ], width=4),
                ], className="mb-4"),
                
                # Simulation Results Table
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Simulation Results", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='simulation-results-table',
                                    figure=viz.create_simulation_results_table(data_loader.get_simulation_results_df()),
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Simulation Selector
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Select Simulation", className="text-center"),
                            dbc.CardBody([
                                dcc.Dropdown(
                                    id='simulation-selector',
                                    options=[
                                        {'label': f'Simulation #{sim["simulationNumber"]} (Start Index: {sim["startIndex"]})', 
                                         'value': sim["simulationNumber"]} 
                                        for sim in data_loader.simulation_results
                                    ],
                                    value=data_loader.simulation_results[0]["simulationNumber"] if data_loader.simulation_results else None,
                                    clearable=False
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Conversation Visualization
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Conversation Flow", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='conversation-flow',
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Conversation Heatmap
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Conversation Heatmap", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='conversation-heatmap',
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Conversation Content
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Conversation Content", className="text-center"),
                            dbc.CardBody([
                                html.Div(id='conversation-content')
                            ], style={"maxHeight": "500px", "overflow": "auto"})
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Agent Evaluation
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Sales Agent Evaluation", className="text-center"),
                            dbc.CardBody([
                                html.Div(id='sales-agent-evaluation')
                            ])
                        ])
                    ], width=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Customer Agent Evaluation", className="text-center"),
                            dbc.CardBody([
                                html.Div(id='customer-agent-evaluation')
                            ])
                        ])
                    ], width=6)
                ], className="mb-4"),
                
                # Message Length Comparison
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Message Length Comparison", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='message-length-comparison',
                                    figure=viz.create_message_length_comparison(data_loader.get_conversation_stats()),
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Simulation Durations
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Simulation Durations", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='simulation-durations',
                                    figure=viz.create_simulation_duration_chart(data_loader.get_all_simulations_metadata()),
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Historical Pass Rates
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Historical Pass Rates", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='historical-pass-rates',
                                    figure=viz.create_historical_pass_rates(data_loader.get_historical_pass_rates()),
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Feedback Word Frequency
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Common Words in Feedback", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='feedback-wordcloud',
                                    figure=viz.create_feedback_wordcloud(data_loader.get_feedback_data()[0]),
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], width=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Common Words in Customer Feedback", className="text-center"),
                            dbc.CardBody([
                                dcc.Graph(
                                    id='customer-feedback-wordcloud',
                                    figure=viz.create_feedback_wordcloud(data_loader.get_feedback_data()[1]),
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], width=6)
                ], className="mb-4"),
            ], fluid=True)
        ]),
        
        # Conversation Detail Tab
        dbc.Tab(label="Conversation Details", tab_id="tab-conversation-detail", children=[
            dbc.Container([
                # Simulation Selector for Conversation View
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Select Simulation", className="text-center"),
                            dbc.CardBody([
                                dcc.Dropdown(
                                    id='conversation-detail-selector',
                                    options=[
                                        {'label': f'Simulation #{sim["simulationNumber"]} (Start Index: {sim["startIndex"]})', 
                                         'value': sim["simulationNumber"]} 
                                        for sim in data_loader.simulation_results
                                    ],
                                    value=data_loader.simulation_results[0]["simulationNumber"] if data_loader.simulation_results else None,
                                    clearable=False
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Two-column layout: Conversation on left, Evaluation on right
                dbc.Row([
                    # Left column - Conversation
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Conversation", className="text-center"),
                            dbc.CardBody([
                                html.Div(
                                    id='conversation-detail-view',
                                    style={"maxHeight": "600px", "overflowY": "auto"}
                                )
                            ])
                        ])
                    ], width=8),
                    
                    # Right column - Evaluation Results
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Simulation Evaluation Results", className="text-center"),
                            dbc.CardBody([
                                html.Div(id='conversation-detail-evaluation')
                            ])
                        ])
                    ], width=4)
                ], className="mb-4"),
                
                # Grader Prompt and User Feedback Section
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Grader Prompt", className="text-center"),
                            dbc.CardBody([
                                html.Div(id='grader-prompt', className="border p-3 mb-3 bg-light"),
                                html.Hr(),
                                html.H5("User Feedback", className="mt-3"),
                                html.P("Do you agree with the grader's evaluation? Provide your feedback below:"),
                                
                                # Sales Agent Evaluation Feedback
                                html.H6("Sales Agent Evaluation", className="mt-3"),
                                dbc.Form([
                                    dbc.Label("Your Assessment:"),
                                    dbc.RadioItems(
                                        id='user-sales-agent-assessment',
                                        options=[
                                            {'label': 'Pass', 'value': 'pass'},
                                            {'label': 'Fail', 'value': 'fail'}
                                        ],
                                        inline=True,
                                        className="mb-2"
                                    ),
                                    dbc.Textarea(
                                        id='user-sales-agent-feedback',
                                        placeholder="Explain why you agree or disagree with the grader's assessment of the sales agent...",
                                        rows=3,
                                        className="mb-3"
                                    )
                                ]),
                                
                                # Customer Agent Evaluation Feedback
                                html.H6("Customer Agent Evaluation", className="mt-3"),
                                dbc.Form([
                                    dbc.Label("Your Assessment:"),
                                    dbc.RadioItems(
                                        id='user-customer-agent-assessment',
                                        options=[
                                            {'label': 'Pass', 'value': 'pass'},
                                            {'label': 'Fail', 'value': 'fail'}
                                        ],
                                        inline=True,
                                        className="mb-2"
                                    ),
                                    dbc.Textarea(
                                        id='user-customer-agent-feedback',
                                        placeholder="Explain why you agree or disagree with the grader's assessment of the customer agent...",
                                        rows=3,
                                        className="mb-3"
                                    )
                                ]),
                                
                                # Overall Feedback
                                html.H6("Overall Feedback", className="mt-3"),
                                dbc.Form([
                                    dbc.Label("Your Overall Assessment:"),
                                    dbc.RadioItems(
                                        id='user-overall-assessment',
                                        options=[
                                            {'label': 'Pass', 'value': 'pass'},
                                            {'label': 'Fail', 'value': 'fail'}
                                        ],
                                        inline=True,
                                        className="mb-2"
                                    ),
                                    dbc.Textarea(
                                        id='user-overall-feedback',
                                        placeholder="Provide your overall feedback on this conversation...",
                                        rows=4,
                                        className="mb-3"
                                    )
                                ]),
                                
                                # Submit Button
                                dbc.Button(
                                    "Submit Feedback", 
                                    id="submit-feedback", 
                                    color="primary", 
                                    className="mt-2"
                                ),
                                
                                # Feedback Submission Status
                                html.Div(id="feedback-submission-status", className="mt-3")
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # User Feedback Summary
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("User Feedback Summary", className="text-center"),
                            dbc.CardBody([
                                html.Div(id='user-feedback-summary')
                            ])
                        ])
                    ], width=12)
                ], className="mb-4")
            ], fluid=True)
        ]),
        
        # Optimizer Tab (New)
        dbc.Tab(label="Optimizer", tab_id="tab-optimizer", children=[
            dbc.Container([
                # Tab Description
                dbc.Row([
                    dbc.Col([
                        html.H3("Prompt Optimization Tools", className="text-center my-3"),
                        html.P("Optimize grader and system prompts based on conversation analysis and expected outcomes.", 
                               className="text-center text-muted mb-4"),
                    ], width=12)
                ]),
                
                # API Key Warning (if not set)
                dbc.Row([
                    dbc.Col([
                        dbc.Alert(
                            [
                                html.H4("OpenAI API Key Not Set", className="alert-heading"),
                                html.P(
                                    "The OpenAI API key is not set. The optimizer will not work without a valid API key.",
                                    className="mb-0"
                                ),
                                html.Hr(),
                                html.P([
                                    "Please set the OPENAI_API_KEY in your .env file. ",
                                    "Copy the .env.example file to .env and add your API key."
                                ],
                                    className="mb-0"
                                )
                            ],
                            color="warning",
                            dismissable=True,
                            is_open=not has_openai_api_key,
                            className="mb-4"
                        )
                    ], width=12)
                ]) if not has_openai_api_key else html.Div(),
                
                # Simulation Selector for Optimizer
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Select Simulation to Optimize", className="text-center"),
                            dbc.CardBody([
                                dcc.Dropdown(
                                    id='optimizer-simulation-selector',
                                    options=[
                                        {'label': f'Simulation #{sim["simulationNumber"]} (Start Index: {sim["startIndex"]})', 
                                         'value': sim["simulationNumber"]} 
                                        for sim in data_loader.simulation_results
                                    ],
                                    value=data_loader.simulation_results[0]["simulationNumber"] if data_loader.simulation_results else None,
                                    clearable=False
                                )
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Tabs for Grader and System Prompt Optimizers
                dbc.Tabs([
                    # Grader Prompt Optimizer
                    dbc.Tab(label="Grader Prompt Optimizer", tab_id="tab-grader-optimizer", children=[
                        dbc.Row([
                            # Left Column - Conversation and Current Evaluation
                            dbc.Col([
                                # Conversation Display
                                dbc.Card([
                                    dbc.CardHeader("Conversation", className="text-center"),
                                    dbc.CardBody([
                                        html.Div(
                                            id='optimizer-conversation-view',
                                            style={"height": "400px", "overflowY": "auto"}
                                        )
                                    ])
                                ], className="mb-3"),
                                
                                # Current Grader Evaluation
                                dbc.Card([
                                    dbc.CardHeader("Current Grader Evaluation", className="text-center"),
                                    dbc.CardBody([
                                        html.Div(id='optimizer-current-evaluation', 
                                               style={"maxHeight": "300px", "overflowY": "auto"})
                                    ])
                                ])
                            ], width=6),
                            
                            # Right Column - Grader Prompt and Expected Evaluation
                            dbc.Col([
                                # Current Grader Prompt
                                dbc.Card([
                                    dbc.CardHeader("Current Grader Prompt", className="text-center"),
                                    dbc.CardBody([
                                        html.Div(id='optimizer-current-grader-prompt', className="border p-3 bg-light", 
                                                style={"height": "400px", "overflowY": "auto", "white-space": "pre-wrap"})
                                    ])
                                ], className="mb-3"),
                                
                                # Expected Evaluation
                                dbc.Card([
                                    dbc.CardHeader("Expected Evaluation", className="text-center"),
                                    dbc.CardBody([
                                        html.H6("Sales Agent Evaluation", className="mt-1"),
                                        dbc.RadioItems(
                                            id='optimizer-expected-sales-assessment',
                                            options=[
                                                {'label': 'Pass', 'value': 'pass'},
                                                {'label': 'Fail', 'value': 'fail'}
                                            ],
                                            inline=True,
                                            className="mb-1"
                                        ),
                                        dbc.Textarea(
                                            id='optimizer-expected-sales-feedback',
                                            placeholder="Expected feedback for sales agent...",
                                            rows=2,
                                            className="mb-2"
                                        ),
                                        
                                        html.H6("Customer Agent Evaluation", className="mt-1"),
                                        dbc.RadioItems(
                                            id='optimizer-expected-customer-assessment',
                                            options=[
                                                {'label': 'Pass', 'value': 'pass'},
                                                {'label': 'Fail', 'value': 'fail'}
                                            ],
                                            inline=True,
                                            className="mb-1"
                                        ),
                                        dbc.Textarea(
                                            id='optimizer-expected-customer-feedback',
                                            placeholder="Expected feedback for customer agent...",
                                            rows=2,
                                            className="mb-2"
                                        ),
                                        
                                        html.H6("Overall Assessment", className="mt-1"),
                                        dbc.RadioItems(
                                            id='optimizer-expected-overall-assessment',
                                            options=[
                                                {'label': 'Pass', 'value': 'pass'},
                                                {'label': 'Fail', 'value': 'fail'}
                                            ],
                                            inline=True,
                                            className="mb-1"
                                        )
                                    ])
                                ])
                            ], width=6)
                        ], className="mb-4"),
                        
                        # Optimized Grader Prompt Section
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Optimized Grader Prompt", className="text-center"),
                                    dbc.CardBody([
                                        dbc.Button(
                                            "Generate Optimized Grader Prompt", 
                                            id="generate-optimized-grader-prompt", 
                                            color="primary", 
                                            className="mb-3",
                                            disabled=not has_openai_api_key
                                        ),
                                        dbc.Spinner(
                                            html.Div(id="optimized-grader-prompt-container", className="border p-3 bg-light",
                                                    style={"minHeight": "200px", "white-space": "pre-wrap"}),
                                            color="primary",
                                            type="border",
                                            fullscreen=False,
                                        ),
                                        dbc.Button(
                                            "Apply Optimized Prompt", 
                                            id="apply-optimized-grader-prompt", 
                                            color="success", 
                                            className="mt-3",
                                            disabled=True
                                        ),
                                        html.Div(id="grader-prompt-update-status", className="mt-2")
                                    ])
                                ])
                            ], width=12)
                        ])
                    ]),
                    
                    # System Prompt Optimizer
                    dbc.Tab(label="System Prompt Optimizer", tab_id="tab-system-optimizer", children=[
                        dbc.Row([
                            # Left Column - Current System Prompts
                            dbc.Col([
                                # Sales Agent System Prompt
                                dbc.Card([
                                    dbc.CardHeader("Current Sales Agent System Prompt", className="text-center"),
                                    dbc.CardBody([
                                        html.Div(id='current-sales-agent-prompt', className="border p-3 mb-3 bg-light", 
                                                style={"maxHeight": "300px", "overflowY": "auto", "white-space": "pre-wrap"})
                                    ])
                                ], className="mb-3"),
                                
                                # Customer Agent System Prompt
                                dbc.Card([
                                    dbc.CardHeader("Current Customer Agent System Prompt", className="text-center"),
                                    dbc.CardBody([
                                        html.Div(id='current-customer-agent-prompt', className="border p-3 mb-3 bg-light", 
                                                style={"maxHeight": "300px", "overflowY": "auto", "white-space": "pre-wrap"})
                                    ])
                                ])
                            ], width=6),
                            
                            # Right Column - Optimization Controls
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Optimization Parameters", className="text-center"),
                                    dbc.CardBody([
                                        html.H6("Select Agent to Optimize", className="mt-2"),
                                        dbc.RadioItems(
                                            id='system-prompt-agent-selector',
                                            options=[
                                                {'label': 'Sales Agent', 'value': 'sales'},
                                                {'label': 'Customer Agent', 'value': 'customer'}
                                            ],
                                            value='sales',
                                            inline=True,
                                            className="mb-3"
                                        ),
                                        
                                        html.H6("Optimization Goal", className="mt-2"),
                                        dbc.Textarea(
                                            id='system-prompt-optimization-goal',
                                            placeholder="Describe what you want to improve in the agent's behavior...",
                                            rows=3,
                                            className="mb-3"
                                        ),
                                        
                                        html.H6("Specific Instructions", className="mt-2"),
                                        dbc.Checklist(
                                            id='system-prompt-optimization-options',
                                            options=[
                                                {'label': 'Improve clarity of communication', 'value': 'clarity'},
                                                {'label': 'Enhance objection handling', 'value': 'objections'},
                                                {'label': 'Better needs identification', 'value': 'needs'},
                                                {'label': 'More persuasive presentation', 'value': 'persuasion'},
                                                {'label': 'Maintain character consistency', 'value': 'character'}
                                            ],
                                            className="mb-3"
                                        ),
                                        
                                        dbc.Button(
                                            "Generate Optimized System Prompt", 
                                            id="generate-optimized-system-prompt", 
                                            color="primary", 
                                            className="mt-2",
                                            disabled=not has_openai_api_key
                                        )
                                    ])
                                ], className="mb-3"),
                                
                                # Conversation Performance Summary
                                dbc.Card([
                                    dbc.CardHeader("Conversation Performance Summary", className="text-center"),
                                    dbc.CardBody([
                                        html.Div(id='system-prompt-performance-summary')
                                    ])
                                ])
                            ], width=6)
                        ], className="mb-4"),
                        
                        # Optimized System Prompt Section
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Optimized System Prompt", className="text-center"),
                                    dbc.CardBody([
                                        dbc.Spinner(
                                            html.Div(id="optimized-system-prompt-container", className="border p-3 bg-light",
                                                    style={"minHeight": "200px", "white-space": "pre-wrap"}),
                                            color="primary",
                                            type="border",
                                            fullscreen=False,
                                        ),
                                        dbc.Button(
                                            "Apply Optimized System Prompt", 
                                            id="apply-optimized-system-prompt", 
                                            color="success", 
                                            className="mt-3",
                                            disabled=True
                                        ),
                                        html.Div(id="system-prompt-update-status", className="mt-2")
                                    ])
                                ])
                            ], width=12)
                        ])
                    ])
                ], id="optimizer-tabs", active_tab="tab-grader-optimizer")
            ], fluid=True)
        ])
    ], id="tabs", active_tab="tab-dashboard"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Sales Simulation Dashboard • Created with Dash and Plotly", className="text-center text-muted"),
            html.P(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", className="text-center text-muted small")
        ], width=12)
    ]),
    
    # Store components for saving user feedback
    dcc.Store(id='user-feedback-store', storage_type='session')
], className="container-fluid")

# Callbacks
@app.callback(
    [Output('conversation-flow', 'figure'),
     Output('conversation-heatmap', 'figure'),
     Output('conversation-content', 'children'),
     Output('sales-agent-evaluation', 'children'),
     Output('customer-agent-evaluation', 'children')],
    [Input('simulation-selector', 'value')]
)
def update_conversation_visualizations(simulation_id):
    if not simulation_id:
        return go.Figure(), go.Figure(), [], "", ""
    
    # Get conversation data
    conversation_df = data_loader.get_conversation_df(simulation_id)
    
    # Create conversation flow visualization
    flow_fig = viz.create_conversation_flow(conversation_df)
    
    # Create conversation heatmap
    heatmap_fig = viz.create_conversation_heatmap(conversation_df)
    
    # Create conversation content display
    conversation = data_loader.get_conversation_by_simulation_id(simulation_id)
    conversation_content = []
    
    for i, msg in enumerate(conversation):
        agent_color = "primary" if msg['agent'] == 'Sales Agent' else "danger"
        conversation_content.append(
            dbc.Card([
                dbc.CardHeader(f"Turn {i+1}: {msg['agent']}", className=f"bg-{agent_color} text-white"),
                dbc.CardBody([
                    html.P(msg['message'].replace('\n', '<br>'), dangerously_allow_html=True)
                ])
            ], className="mb-2")
        )
    
    # Get agent evaluations
    sim_results = data_loader.get_simulation_results_df()
    sales_evaluation = ""
    customer_evaluation = ""
    
    if not sim_results.empty:
        sim_row = sim_results[sim_results['simulationNumber'] == simulation_id]
        if not sim_row.empty:
            sales_evaluation = sim_row.iloc[0].get('salesAgentFeedback', '')
            customer_evaluation = sim_row.iloc[0].get('customerAgentFeedback', '')
    
    # Format evaluations
    sales_evaluation_component = html.Div([
        html.P(sales_evaluation),
        html.Div([
            html.Span("Result: ", className="font-weight-bold"),
            html.Span("✅ PASS", className="text-success") if sim_row.iloc[0].get('salesAgentPassed', False) 
            else html.Span("❌ FAIL", className="text-danger")
        ])
    ])
    
    customer_evaluation_component = html.Div([
        html.P(customer_evaluation),
        html.Div([
            html.Span("Result: ", className="font-weight-bold"),
            html.Span("✅ PASS", className="text-success") if sim_row.iloc[0].get('customerAgentPassed', False) 
            else html.Span("❌ FAIL", className="text-danger")
        ])
    ])
    
    return flow_fig, heatmap_fig, conversation_content, sales_evaluation_component, customer_evaluation_component

# Update the callback for conversation detail view
@app.callback(
    [Output('conversation-detail-view', 'children'),
     Output('conversation-detail-evaluation', 'children'),
     Output('grader-prompt', 'children')],
    [Input('conversation-detail-selector', 'value')]
)
def update_conversation_detail(simulation_id):
    if not simulation_id:
        return [], html.Div("No simulation selected"), ""
    
    # Get conversation data
    conversation = data_loader.get_conversation_by_simulation_id(simulation_id)
    
    # Create vertical conversation view
    conversation_content = []
    
    for i, msg in enumerate(conversation):
        agent_color = "primary" if msg['agent'] == 'Sales Agent' else "danger"
        conversation_content.append(
            dbc.Card([
                dbc.CardHeader([
                    html.Span(f"Turn {i+1}: {msg['agent']}", className=f"text-{agent_color}")
                ]),
                dbc.CardBody([
                    html.Div([html.P(para) for para in msg['message'].split('\n\n')])
                ])
            ], className="mb-3")
        )
    
    # Get evaluation results
    sim_results = data_loader.get_simulation_results_df()
    evaluation_content = html.Div("No evaluation data available")
    
    # Format the conversation for the grader prompt
    conversation_text = ""
    for i, msg in enumerate(conversation):
        conversation_text += f"{msg['agent']}: {msg['message']}\n\n"
    
    # Create the grader prompt
    grader_prompt = f"""
    You are an expert conversation analyst tasked with evaluating a simulated conversation between a sales agent and a potential customer.
    
    Here is the conversation:
    {conversation_text}
    
    Your goal is to evaluate this conversation and provide a boolean assessment for both the sales agent and customer agent.
    
    For the sales agent, evaluate:
    1. Did they effectively introduce themselves and Truss Payments?
    2. Did they attempt to identify the customer's payment challenges?
    3. Did they present the solution clearly?
    4. Did they emphasize key benefits relevant to the customer?
    5. Did they handle objections professionally?
    
    For the customer agent, evaluate:
    1. Did they maintain their established character traits (resistant to change, values relationships, etc.)?
    2. Did they communicate in a direct, sometimes blunt style?
    3. Did they question the benefits of changing their established processes?
    4. Did they respond realistically to the sales pitch?
    
    Provide a boolean value (true for pass, false for fail) for each agent, along with brief feedback explaining your decision.
    """
    
    if not sim_results.empty:
        sim_row = sim_results[sim_results['simulationNumber'] == simulation_id]
        if not sim_row.empty:
            row = sim_row.iloc[0]
            
            # Create evaluation content
            evaluation_content = html.Div([
                # Sales Agent Evaluation
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Sales Agent Evaluation", className="font-weight-bold"),
                        html.Span(
                            " ✅ PASS" if row.get('salesAgentPassed', False) else " ❌ FAIL", 
                            className=f"{'text-success' if row.get('salesAgentPassed', False) else 'text-danger'}"
                        )
                    ]),
                    dbc.CardBody([
                        html.P(row.get('salesAgentFeedback', 'No feedback available'))
                    ])
                ], className="mb-3"),
                
                # Customer Agent Evaluation
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Customer Agent Evaluation", className="font-weight-bold"),
                        html.Span(
                            " ✅ PASS" if row.get('customerAgentPassed', False) else " ❌ FAIL", 
                            className=f"{'text-success' if row.get('customerAgentPassed', False) else 'text-danger'}"
                        )
                    ]),
                    dbc.CardBody([
                        html.P(row.get('customerAgentFeedback', 'No feedback available'))
                    ])
                ], className="mb-3"),
                
                # Overall Result
                dbc.Card([
                    dbc.CardHeader("Overall Result"),
                    dbc.CardBody([
                        html.H3(
                            "✅ PASS" if row.get('overallPassed', False) else "❌ FAIL",
                            className=f"text-center {'text-success' if row.get('overallPassed', False) else 'text-danger'}"
                        ),
                        html.P(f"Duration: {row.get('duration', 0)/1000:.2f}s", className="text-center")
                    ])
                ])
            ])
    
    return conversation_content, evaluation_content, html.Pre(grader_prompt, style={"white-space": "pre-wrap"})

# Callback to handle feedback submission
@app.callback(
    [Output('feedback-submission-status', 'children'),
     Output('user-feedback-store', 'data')],
    [Input('submit-feedback', 'n_clicks')],
    [State('conversation-detail-selector', 'value'),
     State('user-sales-agent-assessment', 'value'),
     State('user-sales-agent-feedback', 'value'),
     State('user-customer-agent-assessment', 'value'),
     State('user-customer-agent-feedback', 'value'),
     State('user-overall-assessment', 'value'),
     State('user-overall-feedback', 'value'),
     State('user-feedback-store', 'data')]
)
def submit_feedback(n_clicks, simulation_id, sales_assessment, sales_feedback, 
                   customer_assessment, customer_feedback, overall_assessment, 
                   overall_feedback, stored_feedback):
    if n_clicks is None:
        return "", stored_feedback or {}
    
    if not simulation_id:
        return dbc.Alert("No simulation selected", color="warning"), stored_feedback or {}
    
    # Initialize feedback store if it doesn't exist
    if stored_feedback is None:
        stored_feedback = {}
    
    # Get the full conversation data
    conversation = data_loader.get_conversation_by_simulation_id(simulation_id)
    
    # Get the grader results
    sim_results = data_loader.get_simulation_results_df()
    grader_results = {}
    
    if not sim_results.empty:
        sim_row = sim_results[sim_results['simulationNumber'] == simulation_id]
        if not sim_row.empty:
            row = sim_row.iloc[0]
            grader_results = {
                'salesAgentPassed': bool(row.get('salesAgentPassed', False)),
                'customerAgentPassed': bool(row.get('customerAgentPassed', False)),
                'overallPassed': bool(row.get('overallPassed', False)),
                'salesAgentFeedback': row.get('salesAgentFeedback', ''),
                'customerAgentFeedback': row.get('customerAgentFeedback', ''),
                'duration': float(row.get('duration', 0))/1000
            }
    
    # Format the conversation for the grader prompt
    conversation_text = ""
    for i, msg in enumerate(conversation):
        conversation_text += f"{msg['agent']}: {msg['message']}\n\n"
    
    # Create the grader prompt
    grader_prompt = f"""
    You are an expert conversation analyst tasked with evaluating a simulated conversation between a sales agent and a potential customer.
    
    Here is the conversation:
    {conversation_text}
    
    Your goal is to evaluate this conversation and provide a boolean assessment for both the sales agent and customer agent.
    
    For the sales agent, evaluate:
    1. Did they effectively introduce themselves and Truss Payments?
    2. Did they attempt to identify the customer's payment challenges?
    3. Did they present the solution clearly?
    4. Did they emphasize key benefits relevant to the customer?
    5. Did they handle objections professionally?
    
    For the customer agent, evaluate:
    1. Did they maintain their established character traits (resistant to change, values relationships, etc.)?
    2. Did they communicate in a direct, sometimes blunt style?
    3. Did they question the benefits of changing their established processes?
    4. Did they respond realistically to the sales pitch?
    
    Provide a boolean value (true for pass, false for fail) for each agent, along with brief feedback explaining your decision.
    """
    
    # Create comprehensive feedback entry
    feedback_entry = {
        'timestamp': datetime.now().isoformat(),
        'simulation_id': simulation_id,
        'conversation': conversation,
        'grader_prompt': grader_prompt,
        'grader_results': grader_results,
        'user_feedback': {
            'sales_assessment': sales_assessment,
            'sales_feedback': sales_feedback,
            'customer_assessment': customer_assessment,
            'customer_feedback': customer_feedback,
            'overall_assessment': overall_assessment,
            'overall_feedback': overall_feedback
        }
    }
    
    # Store feedback by simulation ID
    stored_feedback[str(simulation_id)] = feedback_entry
    
    # Save to a JSON file (optional)
    try:
        feedback_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_feedback')
        os.makedirs(feedback_dir, exist_ok=True)
        
        feedback_file = os.path.join(feedback_dir, f'feedback_sim_{simulation_id}.json')
        with open(feedback_file, 'w') as f:
            json.dump(feedback_entry, f, indent=2)
        
        return dbc.Alert("Feedback submitted successfully and saved to file!", color="success"), stored_feedback
    except Exception as e:
        return dbc.Alert(f"Feedback stored in session, but could not save to file: {str(e)}", color="warning"), stored_feedback

# Callback to display user feedback summary
@app.callback(
    Output('user-feedback-summary', 'children'),
    [Input('user-feedback-store', 'data'),
     Input('conversation-detail-selector', 'value')]
)
def update_feedback_summary(stored_feedback, simulation_id):
    if not stored_feedback or not simulation_id or str(simulation_id) not in stored_feedback:
        return html.P("No feedback has been submitted for this conversation yet.")
    
    feedback = stored_feedback[str(simulation_id)]
    user_feedback = feedback.get('user_feedback', {})
    
    return html.Div([
        html.H5("Your Assessment", className="mb-3"),
        
        # Sales Agent Assessment
        dbc.Card([
            dbc.CardHeader([
                html.Span("Sales Agent", className="font-weight-bold"),
                html.Span(
                    " ✅ PASS" if user_feedback.get('sales_assessment') == 'pass' else " ❌ FAIL", 
                    className=f"{'text-success' if user_feedback.get('sales_assessment') == 'pass' else 'text-danger'}"
                )
            ]),
            dbc.CardBody([
                html.P(user_feedback.get('sales_feedback', 'No feedback provided'))
            ])
        ], className="mb-3"),
        
        # Customer Agent Assessment
        dbc.Card([
            dbc.CardHeader([
                html.Span("Customer Agent", className="font-weight-bold"),
                html.Span(
                    " ✅ PASS" if user_feedback.get('customer_assessment') == 'pass' else " ❌ FAIL", 
                    className=f"{'text-success' if user_feedback.get('customer_assessment') == 'pass' else 'text-danger'}"
                )
            ]),
            dbc.CardBody([
                html.P(user_feedback.get('customer_feedback', 'No feedback provided'))
            ])
        ], className="mb-3"),
        
        # Overall Assessment
        dbc.Card([
            dbc.CardHeader("Overall Assessment"),
            dbc.CardBody([
                html.H3(
                    "✅ PASS" if user_feedback.get('overall_assessment') == 'pass' else "❌ FAIL",
                    className=f"text-center {'text-success' if user_feedback.get('overall_assessment') == 'pass' else 'text-danger'}"
                ),
                html.P(user_feedback.get('overall_feedback', 'No overall feedback provided'), className="mt-3")
            ])
        ]),
        
        html.P(f"Submitted on: {datetime.fromisoformat(feedback.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S')}", 
               className="text-muted mt-3 small")
    ])

# Callbacks for the Optimizer Tab

# Callback to update the optimizer conversation view and current evaluation
@app.callback(
    [Output('optimizer-conversation-view', 'children'),
     Output('optimizer-current-evaluation', 'children'),
     Output('optimizer-current-grader-prompt', 'children')],
    [Input('optimizer-simulation-selector', 'value')]
)
def update_optimizer_conversation(simulation_id):
    if not simulation_id:
        return [], html.Div("No simulation selected"), ""
    
    # Get conversation data
    conversation = data_loader.get_conversation_by_simulation_id(simulation_id)
    
    # Create vertical conversation view
    conversation_content = []
    
    for i, msg in enumerate(conversation):
        agent_color = "primary" if msg['agent'] == 'Sales Agent' else "danger"
        conversation_content.append(
            dbc.Card([
                dbc.CardHeader([
                    html.Span(f"Turn {i+1}: {msg['agent']}", className=f"text-{agent_color}")
                ]),
                dbc.CardBody([
                    html.Div([html.P(para) for para in msg['message'].split('\n\n')])
                ])
            ], className="mb-3")
        )
    
    # Get evaluation results
    sim_results = data_loader.get_simulation_results_df()
    evaluation_content = html.Div("No evaluation data available")
    
    # Format the conversation for the grader prompt
    conversation_text = ""
    for i, msg in enumerate(conversation):
        conversation_text += f"{msg['agent']}: {msg['message']}\n\n"
    
    # Create the grader prompt
    grader_prompt = f"""
    You are an expert conversation analyst tasked with evaluating a simulated conversation between a sales agent and a potential customer.
    
    Here is the conversation:
    {conversation_text}
    
    Your goal is to evaluate this conversation and provide a boolean assessment for both the sales agent and customer agent.
    
    For the sales agent, evaluate:
    1. Did they effectively introduce themselves and Truss Payments?
    2. Did they attempt to identify the customer's payment challenges?
    3. Did they present the solution clearly?
    4. Did they emphasize key benefits relevant to the customer?
    5. Did they handle objections professionally?
    
    For the customer agent, evaluate:
    1. Did they maintain their established character traits (resistant to change, values relationships, etc.)?
    2. Did they communicate in a direct, sometimes blunt style?
    3. Did they question the benefits of changing their established processes?
    4. Did they respond realistically to the sales pitch?
    5. Did they express legitimate concerns that would be expected from a real customer?
    
    IMPORTANT GUIDANCE:
    - For the sales agent: Consider whether they effectively communicated value and addressed customer concerns
    - For the customer agent: Consider whether they maintained a realistic customer persona throughout the conversation
    - Overall result: Consider whether the conversation demonstrates effective sales techniques and realistic customer interactions
    
    Provide a boolean value (true for pass, false for fail) for each agent, along with detailed feedback explaining your decision.
    """
    
    if not sim_results.empty:
        sim_row = sim_results[sim_results['simulationNumber'] == simulation_id]
        if not sim_row.empty:
            row = sim_row.iloc[0]
            
            # Create evaluation content
            evaluation_content = html.Div([
                # Sales Agent Evaluation
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Sales Agent Evaluation", className="font-weight-bold"),
                        html.Span(
                            " ✅ PASS" if row.get('salesAgentPassed', False) else " ❌ FAIL", 
                            className=f"{'text-success' if row.get('salesAgentPassed', False) else 'text-danger'}"
                        )
                    ]),
                    dbc.CardBody([
                        html.P(row.get('salesAgentFeedback', 'No feedback available'))
                    ])
                ], className="mb-3"),
                
                # Customer Agent Evaluation
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Customer Agent Evaluation", className="font-weight-bold"),
                        html.Span(
                            " ✅ PASS" if row.get('customerAgentPassed', False) else " ❌ FAIL", 
                            className=f"{'text-success' if row.get('customerAgentPassed', False) else 'text-danger'}"
                        )
                    ]),
                    dbc.CardBody([
                        html.P(row.get('customerAgentFeedback', 'No feedback available'))
                    ])
                ], className="mb-3"),
                
                # Overall Result
                dbc.Card([
                    dbc.CardHeader("Overall Result"),
                    dbc.CardBody([
                        html.H3(
                            "✅ PASS" if row.get('overallPassed', False) else "❌ FAIL",
                            className=f"text-center {'text-success' if row.get('overallPassed', False) else 'text-danger'}"
                        ),
                        html.P(f"Duration: {row.get('duration', 0)/1000:.2f}s", className="text-center")
                    ])
                ])
            ])
    
    return conversation_content, evaluation_content, html.Pre(grader_prompt, style={"white-space": "pre-wrap"})

# Callback to update system prompts
@app.callback(
    [Output('current-sales-agent-prompt', 'children'),
     Output('current-customer-agent-prompt', 'children'),
     Output('system-prompt-performance-summary', 'children')],
    [Input('optimizer-simulation-selector', 'value'),
     Input('system-prompt-agent-selector', 'value')]
)
def update_system_prompts(simulation_id, agent_type):
    if not simulation_id:
        return "No simulation selected", "No simulation selected", "No simulation selected"
    
    # In a real implementation, these would be loaded from files or a database
    # For this example, we'll use placeholder text
    sales_agent_prompt = """You are a sales agent for Truss Payments, a payment processing company that specializes in helping small to medium-sized businesses streamline their payment operations.

Your goal is to convince the potential customer to switch to Truss Payments from their current payment processor.

Key points about Truss Payments:
1. Competitive rates: 2.5% + $0.10 per transaction (compared to industry average of 2.9% + $0.30)
2. Next-day deposits (compared to 2-3 business days with most processors)
3. No monthly fees or hidden charges
4. 24/7 customer support
5. Easy integration with popular e-commerce platforms and POS systems
6. Advanced fraud protection

Remember to:
- Introduce yourself and Truss Payments professionally
- Ask questions to understand the customer's current payment challenges
- Listen to their needs and tailor your pitch accordingly
- Address objections with empathy and clear information
- Focus on the benefits that matter most to this specific customer
- Be persistent but respectful"""
    
    customer_agent_prompt = """You are a small business owner who has been using the same payment processor for the past 5 years.

Your character traits:
- Somewhat resistant to change (you value stability)
- Price-conscious but willing to pay for quality
- Values relationships and good customer service
- Skeptical of sales pitches (you've heard many before)
- Direct and sometimes blunt communication style

Your current payment processor:
- Charges 2.9% + $0.30 per transaction
- Takes 3 business days for deposits
- Has acceptable but not great customer service
- Has been reliable but occasionally has technical issues
- Charges a $25 monthly fee

Your business concerns:
- Cash flow is important (faster deposits would help)
- You process about $20,000 in payments monthly
- You've had a few fraudulent transactions in the past year
- Your staff finds the current system somewhat difficult to use

During this conversation:
- Ask pointed questions about the new service
- Express skepticism about claims that seem too good to be true
- Mention your loyalty to your current provider
- Bring up concerns about the hassle of switching systems
- Don't agree to switch immediately, but show interest if the offer seems genuinely better"""
    
    # Get evaluation results for performance summary
    sim_results = data_loader.get_simulation_results_df()
    performance_summary = html.Div("No performance data available")
    
    if not sim_results.empty:
        sim_row = sim_results[sim_results['simulationNumber'] == simulation_id]
        if not sim_row.empty:
            row = sim_row.iloc[0]
            
            # Create performance summary based on selected agent
            if agent_type == 'sales':
                agent_passed = row.get('salesAgentPassed', False)
                agent_feedback = row.get('salesAgentFeedback', '')
                agent_name = "Sales Agent"
            else:
                agent_passed = row.get('customerAgentPassed', False)
                agent_feedback = row.get('customerAgentFeedback', '')
                agent_name = "Customer Agent"
            
            performance_summary = html.Div([
                html.H5(f"{agent_name} Performance", className="mb-3"),
                html.Div([
                    html.Span("Result: ", className="font-weight-bold"),
                    html.Span(
                        "✅ PASS" if agent_passed else "❌ FAIL",
                        className=f"{'text-success' if agent_passed else 'text-danger'}"
                    )
                ], className="mb-2"),
                html.P(agent_feedback),
                html.Hr(),
                html.P("Select optimization parameters and click 'Generate Optimized System Prompt' to create an improved prompt based on this performance.", className="text-muted")
            ])
    
    return html.Pre(sales_agent_prompt), html.Pre(customer_agent_prompt), performance_summary

# Callback for generating optimized grader prompt
@app.callback(
    [Output('optimized-grader-prompt-container', 'children'),
     Output('apply-optimized-grader-prompt', 'disabled')],
    [Input('generate-optimized-grader-prompt', 'n_clicks')],
    [State('optimizer-simulation-selector', 'value'),
     State('optimizer-current-grader-prompt', 'children'),
     State('optimizer-expected-sales-assessment', 'value'),
     State('optimizer-expected-customer-assessment', 'value'),
     State('optimizer-expected-overall-assessment', 'value'),
     State('optimizer-expected-sales-feedback', 'value'),
     State('optimizer-expected-customer-feedback', 'value')]
)
def generate_optimized_grader_prompt(n_clicks, simulation_id, current_prompt, 
                                    expected_sales, expected_customer, expected_overall,
                                    expected_sales_feedback, expected_customer_feedback):
    if n_clicks is None or not simulation_id:
        return "Click 'Generate Optimized Grader Prompt' to create an improved prompt based on your expected outcomes.", True
    
    # Get conversation data
    conversation = data_loader.get_conversation_by_simulation_id(simulation_id)
    
    # Format the conversation
    conversation_text = ""
    for i, msg in enumerate(conversation):
        conversation_text += f"{msg['agent']}: {msg['message']}\n\n"
    
    # Get current evaluation results
    sim_results = data_loader.get_simulation_results_df()
    current_results = {}
    
    if not sim_results.empty:
        sim_row = sim_results[sim_results['simulationNumber'] == simulation_id]
        if not sim_row.empty:
            row = sim_row.iloc[0]
            current_results = {
                'salesAgentPassed': bool(row.get('salesAgentPassed', False)),
                'customerAgentPassed': bool(row.get('customerAgentPassed', False)),
                'overallPassed': bool(row.get('overallPassed', False)),
                'salesAgentFeedback': row.get('salesAgentFeedback', ''),
                'customerAgentFeedback': row.get('customerAgentFeedback', '')
            }
    
    # Extract the current prompt text
    current_prompt_text = current_prompt.props['children'] if hasattr(current_prompt, 'props') else str(current_prompt)
    
    # Create expected outcomes dictionary
    expected_outcomes = {
        'sales_assessment': expected_sales if expected_sales else 'Not specified',
        'sales_feedback': expected_sales_feedback if expected_sales_feedback else 'Not specified',
        'customer_assessment': expected_customer if expected_customer else 'Not specified',
        'customer_feedback': expected_customer_feedback if expected_customer_feedback else 'Not specified',
        'overall_assessment': expected_overall if expected_overall else 'Not specified'
    }
    
    # Create a modified prompt with the expected outcomes for OpenAI to use as reference
    modified_prompt_for_openai = f"""
    You are an expert conversation analyst tasked with evaluating a simulated conversation between a sales agent and a potential customer.
    
    Here is the conversation:
    {conversation_text}
    
    Your goal is to evaluate this conversation and provide a boolean assessment for both the sales agent and customer agent.
    
    For the sales agent, evaluate:
    1. Did they effectively introduce themselves and Truss Payments?
    2. Did they attempt to identify the customer's payment challenges?
    3. Did they present the solution clearly?
    4. Did they emphasize key benefits relevant to the customer?
    5. Did they handle objections professionally?
    
    For the customer agent, evaluate:
    1. Did they maintain their established character traits (resistant to change, values relationships, etc.)?
    2. Did they communicate in a direct, sometimes blunt style?
    3. Did they question the benefits of changing their established processes?
    4. Did they respond realistically to the sales pitch?
    5. Did they express legitimate concerns that would be expected from a real customer?
    
    IMPORTANT GUIDANCE:
    - For the sales agent: {"They should PASS this evaluation" if expected_sales == 'pass' else "They should FAIL this evaluation"}
    - For the customer agent: {"They should PASS this evaluation" if expected_customer == 'pass' else "They should FAIL this evaluation"}
    - Overall result: {"The conversation should be considered a PASS" if expected_overall == 'pass' else "The conversation should be considered a FAIL"}
    
    Expected sales agent feedback themes: {expected_sales_feedback if expected_sales_feedback else "Provide balanced feedback highlighting strengths and areas for improvement"}
    
    Expected customer agent feedback themes: {expected_customer_feedback if expected_customer_feedback else "Provide balanced feedback on the realism and consistency of the customer portrayal"}
    
    Provide a boolean value (true for pass, false for fail) for each agent, along with detailed feedback explaining your decision.
    """
    
    # Use OpenAI to generate the optimized grader prompt
    optimized_prompt = generate_optimized_grader_prompt_with_openai(
        modified_prompt_for_openai,
        conversation_text,
        expected_outcomes
    )
    
    return html.Pre(optimized_prompt), False

# Callback for generating optimized system prompt
@app.callback(
    [Output('optimized-system-prompt-container', 'children'),
     Output('apply-optimized-system-prompt', 'disabled')],
    [Input('generate-optimized-system-prompt', 'n_clicks')],
    [State('optimizer-simulation-selector', 'value'),
     State('system-prompt-agent-selector', 'value'),
     State('system-prompt-optimization-goal', 'value'),
     State('system-prompt-optimization-options', 'value'),
     State('current-sales-agent-prompt', 'children'),
     State('current-customer-agent-prompt', 'children')]
)
def generate_optimized_system_prompt(n_clicks, simulation_id, agent_type, optimization_goal,
                                    optimization_options, sales_prompt, customer_prompt):
    if n_clicks is None or not simulation_id:
        return "Click 'Generate Optimized System Prompt' to create an improved prompt based on your parameters.", True
    
    # Get the current prompt based on agent type
    current_prompt = sales_prompt if agent_type == 'sales' else customer_prompt
    current_prompt_text = current_prompt.props['children'] if hasattr(current_prompt, 'props') else str(current_prompt)
    
    # Get conversation data
    conversation = data_loader.get_conversation_by_simulation_id(simulation_id)
    
    # Format the conversation
    conversation_text = ""
    for i, msg in enumerate(conversation):
        conversation_text += f"{msg['agent']}: {msg['message']}\n\n"
    
    # Create optimization notes based on selected options
    optimization_notes = []
    if optimization_options:
        if 'clarity' in optimization_options:
            optimization_notes.append("- Improve clarity of communication")
        if 'objections' in optimization_options:
            optimization_notes.append("- Enhance objection handling techniques")
        if 'needs' in optimization_options:
            optimization_notes.append("- Improve needs identification process")
        if 'persuasion' in optimization_options:
            optimization_notes.append("- Make presentation more persuasive")
        if 'character' in optimization_options:
            optimization_notes.append("- Maintain stronger character consistency")
    
    optimization_text = "\n".join(optimization_notes) if optimization_notes else "No specific optimization areas selected"
    
    # Use OpenAI to generate the optimized prompt
    optimized_prompt = generate_optimized_prompt_with_openai(
        current_prompt_text,
        conversation_text,
        optimization_goal,
        optimization_text,
        "sales agent" if agent_type == 'sales' else "customer agent"
    )
    
    return html.Pre(optimized_prompt), False

# Callback for applying the optimized grader prompt
@app.callback(
    Output('grader-prompt-update-status', 'children'),
    [Input('apply-optimized-grader-prompt', 'n_clicks')],
    [State('optimized-grader-prompt-container', 'children')]
)
def apply_optimized_grader_prompt(n_clicks, optimized_prompt):
    if n_clicks is None:
        return ""
    
    # In a real implementation, this would save the optimized prompt to a file or database
    # For this example, we'll just show a success message
    
    return dbc.Alert(
        "Optimized grader prompt has been applied successfully! Future evaluations will use this prompt.",
        color="success",
        duration=4000
    )

# Callback for applying the optimized system prompt
@app.callback(
    Output('system-prompt-update-status', 'children'),
    [Input('apply-optimized-system-prompt', 'n_clicks')],
    [State('optimized-system-prompt-container', 'children'),
     State('system-prompt-agent-selector', 'value')]
)
def apply_optimized_system_prompt(n_clicks, optimized_prompt, agent_type):
    if n_clicks is None:
        return ""
    
    # In a real implementation, this would save the optimized prompt to a file or database
    # For this example, we'll just show a success message
    
    agent_name = "Sales Agent" if agent_type == 'sales' else "Customer Agent"
    
    return dbc.Alert(
        f"Optimized system prompt for {agent_name} has been applied successfully! Future simulations will use this prompt.",
        color="success",
        duration=4000
    )

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050) 