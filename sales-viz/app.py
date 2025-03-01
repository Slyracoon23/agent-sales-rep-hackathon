import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import json
from datetime import datetime

# Import our custom modules
from data_loader import SalesSimulationData
import visualizations as viz

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
    
    # Create feedback entry
    feedback_entry = {
        'timestamp': datetime.now().isoformat(),
        'sales_assessment': sales_assessment,
        'sales_feedback': sales_feedback,
        'customer_assessment': customer_assessment,
        'customer_feedback': customer_feedback,
        'overall_assessment': overall_assessment,
        'overall_feedback': overall_feedback
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
    
    return html.Div([
        html.H5("Your Assessment", className="mb-3"),
        
        # Sales Agent Assessment
        dbc.Card([
            dbc.CardHeader([
                html.Span("Sales Agent", className="font-weight-bold"),
                html.Span(
                    " ✅ PASS" if feedback.get('sales_assessment') == 'pass' else " ❌ FAIL", 
                    className=f"{'text-success' if feedback.get('sales_assessment') == 'pass' else 'text-danger'}"
                )
            ]),
            dbc.CardBody([
                html.P(feedback.get('sales_feedback', 'No feedback provided'))
            ])
        ], className="mb-3"),
        
        # Customer Agent Assessment
        dbc.Card([
            dbc.CardHeader([
                html.Span("Customer Agent", className="font-weight-bold"),
                html.Span(
                    " ✅ PASS" if feedback.get('customer_assessment') == 'pass' else " ❌ FAIL", 
                    className=f"{'text-success' if feedback.get('customer_assessment') == 'pass' else 'text-danger'}"
                )
            ]),
            dbc.CardBody([
                html.P(feedback.get('customer_feedback', 'No feedback provided'))
            ])
        ], className="mb-3"),
        
        # Overall Assessment
        dbc.Card([
            dbc.CardHeader("Overall Assessment"),
            dbc.CardBody([
                html.H3(
                    "✅ PASS" if feedback.get('overall_assessment') == 'pass' else "❌ FAIL",
                    className=f"text-center {'text-success' if feedback.get('overall_assessment') == 'pass' else 'text-danger'}"
                ),
                html.P(feedback.get('overall_feedback', 'No overall feedback provided'), className="mt-3")
            ])
        ]),
        
        html.P(f"Submitted on: {datetime.fromisoformat(feedback.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S')}", 
               className="text-muted mt-3 small")
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050) 