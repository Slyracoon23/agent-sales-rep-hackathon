import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import json
import glob
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Step 7: Evaluate Agent Performance"

# Function to load agent prompts
def load_agent_prompts():
    prompts = {
        'sales_agent': '',
        'customer_agent': ''
    }
    
    # First check if the prompts exist in the step6 app (optimized prompts)
    step6_dir = "../step6_agent_optimization/data"
    if os.path.exists(f"{step6_dir}/sales_agent_prompt.txt"):
        with open(f"{step6_dir}/sales_agent_prompt.txt", 'r') as f:
            prompts['sales_agent'] = f.read()
    
    if os.path.exists(f"{step6_dir}/customer_agent_prompt.txt"):
        with open(f"{step6_dir}/customer_agent_prompt.txt", 'r') as f:
            prompts['customer_agent'] = f.read()
    
    # If not found in step6, check step1 app (original prompts)
    if not prompts['sales_agent']:
        step1_dir = "../step1_agent_prompts/data"
        if os.path.exists(f"{step1_dir}/sales_agent_prompt.txt"):
            with open(f"{step1_dir}/sales_agent_prompt.txt", 'r') as f:
                prompts['sales_agent'] = f.read()
    
    if not prompts['customer_agent']:
        step1_dir = "../step1_agent_prompts/data"
        if os.path.exists(f"{step1_dir}/customer_agent_prompt.txt"):
            with open(f"{step1_dir}/customer_agent_prompt.txt", 'r') as f:
                prompts['customer_agent'] = f.read()
    
    # Also check local data directory
    local_dir = "data"
    if os.path.exists(f"{local_dir}/sales_agent_prompt.txt"):
        with open(f"{local_dir}/sales_agent_prompt.txt", 'r') as f:
            prompts['sales_agent'] = f.read()
    
    if os.path.exists(f"{local_dir}/customer_agent_prompt.txt"):
        with open(f"{local_dir}/customer_agent_prompt.txt", 'r') as f:
            prompts['customer_agent'] = f.read()
    
    return prompts

# Function to load grader prompt
def load_grader_prompt():
    # First check if the grader prompt exists in the step4 app (optimized prompt)
    step4_prompt_path = "../step4_grader_optimization/data/grader_prompt.txt"
    if os.path.exists(step4_prompt_path):
        with open(step4_prompt_path, 'r') as f:
            return f.read()
    
    # Then check if the grader prompt exists in the step3 app (original prompt)
    step3_prompt_path = "../step3_grader_prompt/data/grader_prompt.txt"
    if os.path.exists(step3_prompt_path):
        with open(step3_prompt_path, 'r') as f:
            return f.read()
    
    # Also check local data directory
    local_prompt_path = "data/grader_prompt.txt"
    if os.path.exists(local_prompt_path):
        with open(local_prompt_path, 'r') as f:
            return f.read()
    
    # Return a default prompt if none found
    return """You are an expert evaluator of sales conversations. Your task is to analyze a conversation between a sales agent and a customer and provide ratings and feedback."""

# Function to load evaluation results
def load_evaluation_results():
    results = []
    
    # Check if the evaluation results directory exists
    results_dir = "data/evaluation_results"
    if os.path.exists(results_dir):
        # Load evaluation results
        for file_path in glob.glob(f"{results_dir}/*.json"):
            try:
                with open(file_path, 'r') as f:
                    result = json.load(f)
                    results.append(result)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
    
    return results

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Step 7: Evaluate Agent Performance", className="text-center my-4"),
            html.P("Test agent performance against the grader prompt.", className="text-center mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Agent Prompts"),
                dbc.CardBody([
                    dbc.Tabs([
                        dbc.Tab([
                            html.Div(id="sales-agent-prompt-container", className="mt-3")
                        ], label="Sales Agent Prompt"),
                        dbc.Tab([
                            html.Div(id="customer-agent-prompt-container", className="mt-3")
                        ], label="Customer Agent Prompt"),
                    ]),
                    dbc.Button("Load Agent Prompts", id="load-agent-prompts", color="secondary", className="mt-3"),
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Evaluation Settings"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Number of Conversations to Generate"),
                            dcc.Slider(
                                id='num-conversations',
                                min=1,
                                max=10,
                                step=1,
                                value=5,
                                marks={i: str(i) for i in range(1, 11)},
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Conversation Length"),
                            dcc.Slider(
                                id='conversation-length',
                                min=5,
                                max=20,
                                step=1,
                                value=10,
                                marks={i: str(i) for i in [5, 10, 15, 20]},
                            ),
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Conversation Scenarios"),
                            dcc.Dropdown(
                                id='conversation-scenarios',
                                options=[
                                    {'label': 'Small Business (5-20 employees)', 'value': 'small_business'},
                                    {'label': 'Medium Business (20-100 employees)', 'value': 'medium_business'},
                                    {'label': 'Enterprise (100+ employees)', 'value': 'enterprise'},
                                    {'label': 'Startup', 'value': 'startup'},
                                    {'label': 'Non-profit', 'value': 'nonprofit'}
                                ],
                                value=['small_business', 'medium_business', 'enterprise'],
                                multi=True
                            ),
                        ], width=12, className="mt-3"),
                    ]),
                    dbc.Button("Run Evaluation", id="run-evaluation", color="primary", className="mt-3"),
                    html.Div(id="evaluation-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Evaluation Results"),
                dbc.CardBody([
                    html.Div(id="evaluation-results-container")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Detailed Analysis"),
                dbc.CardBody([
                    html.Div(id="detailed-analysis-container")
                ])
            ]),
        ], width=12)
    ]),
    
    dbc.Modal([
        dbc.ModalHeader("Conversation Details"),
        dbc.ModalBody(id="conversation-detail-modal-body"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-conversation-modal", className="ml-auto")
        ),
    ], id="conversation-detail-modal", size="xl"),
    
    # Store components for managing state
    dcc.Store(id='agent-prompts-store'),
    dcc.Store(id='grader-prompt-store'),
    dcc.Store(id='evaluation-results-store'),
    dcc.Store(id='selected-conversation-store'),
    
], fluid=True)

# Define callbacks
@app.callback(
    [Output('agent-prompts-store', 'data'),
     Output('grader-prompt-store', 'data'),
     Output('sales-agent-prompt-container', 'children'),
     Output('customer-agent-prompt-container', 'children')],
    [Input('load-agent-prompts', 'n_clicks')],
    prevent_initial_call=False
)
def load_data(n_clicks):
    agent_prompts = load_agent_prompts()
    grader_prompt = load_grader_prompt()
    
    # Create displays for the agent prompts
    sales_prompt_display = html.Pre(
        agent_prompts.get('sales_agent', "No sales agent prompt found."), 
        style={"white-space": "pre-wrap", "max-height": "300px", "overflow-y": "auto"}
    )
    
    customer_prompt_display = html.Pre(
        agent_prompts.get('customer_agent', "No customer agent prompt found."), 
        style={"white-space": "pre-wrap", "max-height": "300px", "overflow-y": "auto"}
    )
    
    return agent_prompts, grader_prompt, sales_prompt_display, customer_prompt_display

@app.callback(
    [Output('evaluation-status', 'children'),
     Output('evaluation-results-store', 'data'),
     Output('evaluation-results-container', 'children'),
     Output('detailed-analysis-container', 'children')],
    [Input('run-evaluation', 'n_clicks')],
    [State('agent-prompts-store', 'data'),
     State('grader-prompt-store', 'data'),
     State('num-conversations', 'value'),
     State('conversation-length', 'value'),
     State('conversation-scenarios', 'value')],
    prevent_initial_call=True
)
def run_evaluation(n_clicks, agent_prompts, grader_prompt, num_conversations, conversation_length, scenarios):
    if n_clicks is None or not agent_prompts or not grader_prompt:
        return "", None, "", ""
    
    if not openai_api_key:
        return dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger"), None, "", ""
    
    # Get the agent prompts
    sales_agent_prompt = agent_prompts.get('sales_agent', "")
    customer_agent_prompt = agent_prompts.get('customer_agent', "")
    
    if not sales_agent_prompt or not customer_agent_prompt:
        return dbc.Alert("Missing agent prompts. Please load agent prompts first.", color="danger"), None, "", ""
    
    # Create directory if it doesn't exist
    os.makedirs("data/evaluation_results", exist_ok=True)
    
    # Generate and evaluate conversations
    evaluation_results = []
    
    for i in range(num_conversations):
        # Select a random scenario
        scenario = np.random.choice(scenarios)
        
        try:
            # Create a system message for the conversation generation
            system_message = f"""Generate a realistic sales conversation between a sales agent and a customer.
The conversation should be about {conversation_length} messages long (alternating between sales agent and customer).

Sales Agent Prompt:
{sales_agent_prompt}

Customer Agent Prompt:
{customer_agent_prompt}

Scenario: {scenario.replace('_', ' ').title()}

Format the conversation as a JSON array of message objects, each with 'role' (either 'sales_agent' or 'customer') and 'content' fields.
"""

            # Call the OpenAI API to generate the conversation
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": "Generate a realistic sales conversation based on the provided prompts and scenario."}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract the conversation
            conversation_text = response.choices[0].message.content
            
            # Try to parse the JSON
            try:
                # Find JSON array in the response
                import re
                json_match = re.search(r'\[\s*\{.*\}\s*\]', conversation_text, re.DOTALL)
                if json_match:
                    conversation_json = json.loads(json_match.group(0))
                else:
                    # If no JSON array found, try to parse the entire response
                    conversation_json = json.loads(conversation_text)
                
                # Format the conversation for the grader
                conversation_text_formatted = ""
                
                for msg in conversation_json:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    conversation_text_formatted += f"{role.replace('_', ' ').title()}: {content}\n\n"
                
                # Now evaluate the conversation with the grader
                user_message = f"""Please analyze the following conversation:

CONVERSATION:
{conversation_text_formatted}"""

                # Call the OpenAI API to evaluate the conversation
                grader_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": grader_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # Extract the response
                grader_text = grader_response.choices[0].message.content
                
                # Parse the grader response
                import re
                
                # Extract ratings
                sales_rating_match = re.search(r'SALES_AGENT_RATING:\s*(PASS|FAIL)', grader_text, re.IGNORECASE)
                sales_rating = sales_rating_match.group(1).lower() if sales_rating_match else "unknown"
                
                customer_rating_match = re.search(r'CUSTOMER_AGENT_RATING:\s*(PASS|FAIL)', grader_text, re.IGNORECASE)
                customer_rating = customer_rating_match.group(1).lower() if customer_rating_match else "unknown"
                
                overall_rating_match = re.search(r'OVERALL_RATING:\s*(PASS|FAIL)', grader_text, re.IGNORECASE)
                overall_rating = overall_rating_match.group(1).lower() if overall_rating_match else "unknown"
                
                # Extract feedback
                sales_feedback_match = re.search(r'SALES_AGENT_FEEDBACK:\s*(.*?)(?=CUSTOMER_AGENT_RATING:|$)', grader_text, re.IGNORECASE | re.DOTALL)
                sales_feedback = sales_feedback_match.group(1).strip() if sales_feedback_match else ""
                
                customer_feedback_match = re.search(r'CUSTOMER_AGENT_FEEDBACK:\s*(.*?)(?=OVERALL_RATING:|$)', grader_text, re.IGNORECASE | re.DOTALL)
                customer_feedback = customer_feedback_match.group(1).strip() if customer_feedback_match else ""
                
                overall_feedback_match = re.search(r'OVERALL_FEEDBACK:\s*(.*?)(?=$)', grader_text, re.IGNORECASE | re.DOTALL)
                overall_feedback = overall_feedback_match.group(1).strip() if overall_feedback_match else ""
                
                # Store the results
                result = {
                    'id': f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                    'timestamp': datetime.now().isoformat(),
                    'scenario': scenario,
                    'conversation': conversation_json,
                    'conversation_text': conversation_text_formatted,
                    'grader_response': grader_text,
                    'sales_rating': sales_rating,
                    'customer_rating': customer_rating,
                    'overall_rating': overall_rating,
                    'sales_feedback': sales_feedback,
                    'customer_feedback': customer_feedback,
                    'overall_feedback': overall_feedback
                }
                
                # Save to file
                filename = f"data/evaluation_results/evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.json"
                with open(filename, "w") as f:
                    json.dump(result, f, indent=2)
                
                evaluation_results.append(result)
                
            except json.JSONDecodeError:
                print(f"Error parsing conversation {i}: JSON decode error")
        
        except Exception as e:
            print(f"Error evaluating conversation {i}: {str(e)}")
    
    # Load any existing evaluation results
    existing_results = load_evaluation_results()
    
    # Combine with new results
    all_results = existing_results + evaluation_results
    
    # Calculate statistics
    sales_pass = sum(1 for result in all_results if result.get('sales_rating') == 'pass')
    sales_fail = sum(1 for result in all_results if result.get('sales_rating') == 'fail')
    sales_pass_rate = (sales_pass / (sales_pass + sales_fail)) * 100 if sales_pass + sales_fail > 0 else 0
    
    customer_pass = sum(1 for result in all_results if result.get('customer_rating') == 'pass')
    customer_fail = sum(1 for result in all_results if result.get('customer_rating') == 'fail')
    customer_pass_rate = (customer_pass / (customer_pass + customer_fail)) * 100 if customer_pass + customer_fail > 0 else 0
    
    overall_pass = sum(1 for result in all_results if result.get('overall_rating') == 'pass')
    overall_fail = sum(1 for result in all_results if result.get('overall_rating') == 'fail')
    overall_pass_rate = (overall_pass / (overall_pass + overall_fail)) * 100 if overall_pass + overall_fail > 0 else 0
    
    # Create a summary figure
    categories = ['Sales Agent', 'Customer Agent', 'Overall']
    pass_rates = [sales_pass_rate, customer_pass_rate, overall_pass_rate]
    
    fig = go.Figure(go.Bar(
        x=categories,
        y=pass_rates,
        text=[f"{rate:.1f}%" for rate in pass_rates],
        textposition='auto',
        marker_color=['blue', 'green', 'purple']
    ))
    
    fig.update_layout(
        title='Pass Rates by Category',
        xaxis_title='Category',
        yaxis_title='Pass Rate (%)',
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    # Create a summary table
    summary_table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Category"),
                html.Th("Pass"),
                html.Th("Fail"),
                html.Th("Pass Rate")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td("Sales Agent"),
                html.Td(sales_pass),
                html.Td(sales_fail),
                html.Td(f"{sales_pass_rate:.1f}%")
            ]),
            html.Tr([
                html.Td("Customer Agent"),
                html.Td(customer_pass),
                html.Td(customer_fail),
                html.Td(f"{customer_pass_rate:.1f}%")
            ]),
            html.Tr([
                html.Td("Overall"),
                html.Td(overall_pass),
                html.Td(overall_fail),
                html.Td(f"{overall_pass_rate:.1f}%")
            ])
        ])
    ], bordered=True, hover=True)
    
    # Create a scenario breakdown
    scenario_counts = {}
    scenario_pass_rates = {}
    
    for result in all_results:
        scenario = result.get('scenario', 'unknown')
        overall_rating = result.get('overall_rating', 'unknown')
        
        if scenario not in scenario_counts:
            scenario_counts[scenario] = {'pass': 0, 'fail': 0}
        
        if overall_rating == 'pass':
            scenario_counts[scenario]['pass'] += 1
        elif overall_rating == 'fail':
            scenario_counts[scenario]['fail'] += 1
    
    for scenario, counts in scenario_counts.items():
        total = counts['pass'] + counts['fail']
        pass_rate = (counts['pass'] / total) * 100 if total > 0 else 0
        scenario_pass_rates[scenario] = pass_rate
    
    # Create a scenario breakdown figure
    scenario_fig = go.Figure(go.Bar(
        x=list(scenario_pass_rates.keys()),
        y=list(scenario_pass_rates.values()),
        text=[f"{rate:.1f}%" for rate in scenario_pass_rates.values()],
        textposition='auto',
        marker_color='lightblue'
    ))
    
    scenario_fig.update_layout(
        title='Pass Rates by Scenario',
        xaxis_title='Scenario',
        yaxis_title='Pass Rate (%)',
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    # Create the results container
    results_container = [
        html.H5(f"Evaluation Results ({len(all_results)} conversations)"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=fig)
            ], width=6),
            dbc.Col([
                summary_table
            ], width=6)
        ]),
        html.H5("Scenario Breakdown", className="mt-4"),
        dcc.Graph(figure=scenario_fig)
    ]
    
    # Create the detailed analysis container
    conversation_cards = []
    
    for i, result in enumerate(all_results):
        # Create a card for each conversation
        card = dbc.Card([
            dbc.CardHeader([
                html.H5(f"Conversation {i+1} - {result.get('scenario', 'Unknown').replace('_', ' ').title()}"),
                html.Small(f"ID: {result.get('id', 'Unknown')}")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Strong("Sales Agent: "),
                        html.Span(result.get('sales_rating', 'unknown').upper(), 
                                 style={"color": "green" if result.get('sales_rating') == 'pass' else "red"})
                    ], width=4),
                    dbc.Col([
                        html.Strong("Customer Agent: "),
                        html.Span(result.get('customer_rating', 'unknown').upper(),
                                 style={"color": "green" if result.get('customer_rating') == 'pass' else "red"})
                    ], width=4),
                    dbc.Col([
                        html.Strong("Overall: "),
                        html.Span(result.get('overall_rating', 'unknown').upper(),
                                 style={"color": "green" if result.get('overall_rating') == 'pass' else "red"})
                    ], width=4)
                ]),
                dbc.Button("View Details", id=f"view-conversation-{i}", color="info", className="mt-3")
            ])
        ], className="mb-3")
        
        conversation_cards.append(card)
    
    detailed_analysis = [
        html.H5("Individual Conversation Results"),
        html.Div(conversation_cards)
    ]
    
    # Create a status message
    status_message = dbc.Alert(
        f"Successfully evaluated {len(evaluation_results)} new conversations. Total: {len(all_results)} conversations.",
        color="success"
    )
    
    return status_message, all_results, results_container, detailed_analysis

# Callback for opening the conversation detail modal
@app.callback(
    [Output('conversation-detail-modal', 'is_open'),
     Output('selected-conversation-store', 'data'),
     Output('conversation-detail-modal-body', 'children')],
    [Input('view-conversation-0', 'n_clicks'),
     Input('view-conversation-1', 'n_clicks'),
     Input('view-conversation-2', 'n_clicks'),
     Input('view-conversation-3', 'n_clicks'),
     Input('view-conversation-4', 'n_clicks'),
     Input('view-conversation-5', 'n_clicks'),
     Input('view-conversation-6', 'n_clicks'),
     Input('view-conversation-7', 'n_clicks'),
     Input('view-conversation-8', 'n_clicks'),
     Input('view-conversation-9', 'n_clicks'),
     Input('close-conversation-modal', 'n_clicks')],
    [State('evaluation-results-store', 'data'),
     State('conversation-detail-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_conversation_modal(n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, close_clicks, results, is_open):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return is_open, None, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'close-conversation-modal':
        return False, None, ""
    
    if 'view-conversation' in button_id:
        # Extract the index from the button ID
        idx = int(button_id.split('-')[-1])
        
        if results and idx < len(results):
            result = results[idx]
            
            # Create the conversation display
            conversation_display = []
            
            if "conversation" in result:
                for msg in result["conversation"]:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    
                    conversation_display.append(
                        dbc.ListGroupItem([
                            html.Strong(f"{role.replace('_', ' ').title()}: "),
                            html.Span(content)
                        ])
                    )
            
            # Create the modal body
            modal_body = [
                html.H5(f"Scenario: {result.get('scenario', 'Unknown').replace('_', ' ').title()}"),
                html.H6("Conversation:", className="mt-3"),
                dbc.ListGroup(conversation_display, className="mb-4"),
                html.H6("Grader Evaluation:", className="mt-3"),
                dbc.Card([
                    dbc.CardHeader(f"Sales Agent Rating: {result.get('sales_rating', 'unknown').upper()}"),
                    dbc.CardBody(result.get('sales_feedback', ''))
                ], className="mb-2"),
                dbc.Card([
                    dbc.CardHeader(f"Customer Agent Rating: {result.get('customer_rating', 'unknown').upper()}"),
                    dbc.CardBody(result.get('customer_feedback', ''))
                ], className="mb-2"),
                dbc.Card([
                    dbc.CardHeader(f"Overall Rating: {result.get('overall_rating', 'unknown').upper()}"),
                    dbc.CardBody(result.get('overall_feedback', ''))
                ])
            ]
            
            return True, result, modal_body
    
    return is_open, None, ""

# Run the app
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/evaluation_results", exist_ok=True)
    
    port = int(os.environ.get("PORT", 8056))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run_server(debug=debug, port=port) 