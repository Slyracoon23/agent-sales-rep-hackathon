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
app.title = "Step 2: Clean and Label Data"

# Function to load conversations
def load_conversations():
    conversations = []
    
    # Check if the conversations directory exists in the step1 app
    step1_conv_dir = "../step1_agent_prompts/data/conversations"
    if os.path.exists(step1_conv_dir):
        # Load conversations from step1
        for file_path in glob.glob(f"{step1_conv_dir}/*.json"):
            try:
                with open(file_path, 'r') as f:
                    conversation = json.load(f)
                    conversations.append(conversation)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
    
    # Also check local data directory
    local_conv_dir = "data/conversations"
    if os.path.exists(local_conv_dir):
        # Load conversations from local directory
        for file_path in glob.glob(f"{local_conv_dir}/*.json"):
            try:
                with open(file_path, 'r') as f:
                    conversation = json.load(f)
                    conversations.append(conversation)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
    
    return conversations

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Step 2: Clean and Label Data", className="text-center my-4"),
            html.P("Process conversation data with natural language feedback and structured pass/fail labels.", className="text-center mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Conversation Selection"),
                dbc.CardBody([
                    html.Div(id="conversation-count"),
                    dcc.Dropdown(
                        id='conversation-selector',
                        options=[],
                        placeholder="Select a conversation to label",
                    ),
                    dbc.Button("Refresh Conversations", id="refresh-conversations", color="secondary", className="mt-2"),
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Conversation View"),
                dbc.CardBody([
                    html.Div(id="conversation-view")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Conversation Labeling"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Sales Agent Performance"),
                            dcc.RadioItems(
                                id='sales-agent-rating',
                                options=[
                                    {'label': 'Pass', 'value': 'pass'},
                                    {'label': 'Fail', 'value': 'fail'}
                                ],
                                className="mb-2"
                            ),
                            html.Label("Sales Agent Feedback"),
                            dcc.Textarea(
                                id='sales-agent-feedback',
                                placeholder="Provide detailed feedback on the sales agent's performance...",
                                style={'width': '100%', 'height': 100},
                                className="mb-3"
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Customer Agent Performance"),
                            dcc.RadioItems(
                                id='customer-agent-rating',
                                options=[
                                    {'label': 'Pass', 'value': 'pass'},
                                    {'label': 'Fail', 'value': 'fail'}
                                ],
                                className="mb-2"
                            ),
                            html.Label("Customer Agent Feedback"),
                            dcc.Textarea(
                                id='customer-agent-feedback',
                                placeholder="Provide detailed feedback on the customer agent's performance...",
                                style={'width': '100%', 'height': 100},
                                className="mb-3"
                            ),
                        ], width=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Overall Conversation Rating"),
                            dcc.RadioItems(
                                id='overall-rating',
                                options=[
                                    {'label': 'Pass', 'value': 'pass'},
                                    {'label': 'Fail', 'value': 'fail'}
                                ],
                                className="mb-2"
                            ),
                            html.Label("Overall Feedback"),
                            dcc.Textarea(
                                id='overall-feedback',
                                placeholder="Provide overall feedback on the conversation...",
                                style={'width': '100%', 'height': 100},
                                className="mb-3"
                            ),
                        ], width=12)
                    ]),
                    dbc.Button("Save Labels", id="save-labels", color="primary", className="mt-2"),
                    html.Div(id="save-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Auto-Label with AI"),
                dbc.CardBody([
                    html.P("Use AI to automatically generate labels and feedback for the selected conversation."),
                    dbc.Button("Generate AI Labels", id="generate-ai-labels", color="success", className="mt-2"),
                    html.Div(id="ai-label-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Labeled Conversations"),
                dbc.CardBody([
                    html.Div(id="labeled-conversations-count"),
                    html.Div(id="labeled-conversations-summary")
                ])
            ]),
        ], width=12)
    ]),
    
    # Store components for managing state
    dcc.Store(id='conversations-store'),
    dcc.Store(id='labeled-conversations-store'),
    
], fluid=True)

# Define callbacks
@app.callback(
    [Output('conversations-store', 'data'),
     Output('conversation-count', 'children'),
     Output('conversation-selector', 'options')],
    [Input('refresh-conversations', 'n_clicks')],
    prevent_initial_call=False
)
def refresh_conversations(n_clicks):
    conversations = load_conversations()
    
    # Create options for the dropdown
    options = []
    for i, conv in enumerate(conversations):
        conv_id = conv.get('id', f"conversation_{i}")
        scenario = conv.get('scenario', 'Unknown')
        timestamp = conv.get('timestamp', 'Unknown')
        
        # Format the timestamp
        if timestamp != 'Unknown':
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        label = f"{conv_id} - {scenario.replace('_', ' ').title()} - {timestamp}"
        options.append({'label': label, 'value': i})
    
    return conversations, f"Found {len(conversations)} conversations", options

@app.callback(
    Output('conversation-view', 'children'),
    [Input('conversation-selector', 'value'),
     Input('conversations-store', 'data')]
)
def update_conversation_view(selected_index, conversations):
    if selected_index is None or conversations is None or len(conversations) <= selected_index:
        return "No conversation selected"
    
    conversation = conversations[selected_index]
    
    # Create a list of messages
    messages = []
    
    if "conversation" in conversation:
        for msg in conversation["conversation"]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # Format the message
            messages.append(
                dbc.ListGroupItem([
                    html.Strong(f"{role.replace('_', ' ').title()}: "),
                    html.Span(content)
                ])
            )
    elif "conversation_text" in conversation:
        # If conversation parsing failed, show the raw text
        messages.append(
            dbc.ListGroupItem([
                html.Strong("Raw Conversation Text: "),
                html.Pre(conversation.get("conversation_text", ""))
            ])
        )
    
    # Create the list group
    return dbc.ListGroup(messages)

@app.callback(
    [Output('sales-agent-rating', 'value'),
     Output('sales-agent-feedback', 'value'),
     Output('customer-agent-rating', 'value'),
     Output('customer-agent-feedback', 'value'),
     Output('overall-rating', 'value'),
     Output('overall-feedback', 'value')],
    [Input('conversation-selector', 'value'),
     Input('labeled-conversations-store', 'data')]
)
def load_existing_labels(selected_index, labeled_conversations):
    if selected_index is None or labeled_conversations is None:
        return None, "", None, "", None, ""
    
    # Check if this conversation has already been labeled
    for labeled_conv in labeled_conversations or []:
        if labeled_conv.get('conversation_index') == selected_index:
            return (
                labeled_conv.get('sales_agent_rating'),
                labeled_conv.get('sales_agent_feedback', ""),
                labeled_conv.get('customer_agent_rating'),
                labeled_conv.get('customer_agent_feedback', ""),
                labeled_conv.get('overall_rating'),
                labeled_conv.get('overall_feedback', "")
            )
    
    return None, "", None, "", None, ""

@app.callback(
    [Output('labeled-conversations-store', 'data'),
     Output('save-status', 'children')],
    [Input('save-labels', 'n_clicks')],
    [State('conversation-selector', 'value'),
     State('conversations-store', 'data'),
     State('sales-agent-rating', 'value'),
     State('sales-agent-feedback', 'value'),
     State('customer-agent-rating', 'value'),
     State('customer-agent-feedback', 'value'),
     State('overall-rating', 'value'),
     State('overall-feedback', 'value'),
     State('labeled-conversations-store', 'data')]
)
def save_labels(n_clicks, selected_index, conversations, 
               sales_rating, sales_feedback, 
               customer_rating, customer_feedback,
               overall_rating, overall_feedback,
               labeled_conversations):
    if n_clicks is None or selected_index is None:
        return labeled_conversations or [], ""
    
    # Create directories if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/labeled_conversations", exist_ok=True)
    
    # Get the selected conversation
    conversation = conversations[selected_index]
    
    # Create the label data
    label_data = {
        'conversation_index': selected_index,
        'conversation_id': conversation.get('id', f"conversation_{selected_index}"),
        'timestamp': datetime.now().isoformat(),
        'sales_agent_rating': sales_rating,
        'sales_agent_feedback': sales_feedback,
        'customer_agent_rating': customer_rating,
        'customer_agent_feedback': customer_feedback,
        'overall_rating': overall_rating,
        'overall_feedback': overall_feedback
    }
    
    # Initialize labeled_conversations if it doesn't exist
    if labeled_conversations is None:
        labeled_conversations = []
    
    # Check if this conversation has already been labeled
    found = False
    for i, labeled_conv in enumerate(labeled_conversations):
        if labeled_conv.get('conversation_index') == selected_index:
            labeled_conversations[i] = label_data
            found = True
            break
    
    # If not found, add it
    if not found:
        labeled_conversations.append(label_data)
    
    # Save to file
    filename = f"data/labeled_conversations/labeled_{conversation.get('id', f'conversation_{selected_index}')}.json"
    
    # Combine the original conversation with the labels
    combined_data = {**conversation, 'labels': label_data}
    
    with open(filename, "w") as f:
        json.dump(combined_data, f, indent=2)
    
    return labeled_conversations, dbc.Alert("Labels saved successfully!", color="success", duration=4000)

@app.callback(
    [Output('ai-label-status', 'children'),
     Output('sales-agent-rating', 'value', allow_duplicate=True),
     Output('sales-agent-feedback', 'value', allow_duplicate=True),
     Output('customer-agent-rating', 'value', allow_duplicate=True),
     Output('customer-agent-feedback', 'value', allow_duplicate=True),
     Output('overall-rating', 'value', allow_duplicate=True),
     Output('overall-feedback', 'value', allow_duplicate=True)],
    [Input('generate-ai-labels', 'n_clicks')],
    [State('conversation-selector', 'value'),
     State('conversations-store', 'data')],
    prevent_initial_call=True
)
def generate_ai_labels(n_clicks, selected_index, conversations):
    if n_clicks is None or selected_index is None or not openai_api_key:
        return "", None, "", None, "", None, ""
    
    # Get the selected conversation
    conversation = conversations[selected_index]
    
    # Format the conversation for the AI
    conversation_text = ""
    
    if "conversation" in conversation:
        for msg in conversation["conversation"]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role.replace('_', ' ').title()}: {content}\n\n"
    elif "conversation_text" in conversation:
        conversation_text = conversation.get("conversation_text", "")
    
    # Create the system message
    system_message = """You are an expert at evaluating sales conversations. 
Your task is to analyze a conversation between a sales agent and a customer and provide ratings and feedback.
For each agent (sales and customer) and for the overall conversation, provide a PASS or FAIL rating and detailed feedback."""

    # Create the user message
    user_message = f"""Please analyze the following conversation and provide ratings and feedback:

CONVERSATION:
{conversation_text}

For each of the following, provide a rating (PASS or FAIL) and detailed feedback:
1. Sales Agent Performance
2. Customer Agent Performance
3. Overall Conversation

Format your response as follows:
SALES_AGENT_RATING: PASS or FAIL
SALES_AGENT_FEEDBACK: Your detailed feedback here...
CUSTOMER_AGENT_RATING: PASS or FAIL
CUSTOMER_AGENT_FEEDBACK: Your detailed feedback here...
OVERALL_RATING: PASS or FAIL
OVERALL_FEEDBACK: Your detailed feedback here...
"""

    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the response
        ai_response = response.choices[0].message.content
        
        # Parse the response
        sales_rating = None
        sales_feedback = ""
        customer_rating = None
        customer_feedback = ""
        overall_rating = None
        overall_feedback = ""
        
        # Extract ratings and feedback using simple parsing
        import re
        
        # Extract sales agent rating and feedback
        sales_rating_match = re.search(r'SALES_AGENT_RATING:\s*(PASS|FAIL)', ai_response, re.IGNORECASE)
        if sales_rating_match:
            sales_rating = sales_rating_match.group(1).lower()
        
        sales_feedback_match = re.search(r'SALES_AGENT_FEEDBACK:\s*(.*?)(?=CUSTOMER_AGENT_RATING:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        if sales_feedback_match:
            sales_feedback = sales_feedback_match.group(1).strip()
        
        # Extract customer agent rating and feedback
        customer_rating_match = re.search(r'CUSTOMER_AGENT_RATING:\s*(PASS|FAIL)', ai_response, re.IGNORECASE)
        if customer_rating_match:
            customer_rating = customer_rating_match.group(1).lower()
        
        customer_feedback_match = re.search(r'CUSTOMER_AGENT_FEEDBACK:\s*(.*?)(?=OVERALL_RATING:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        if customer_feedback_match:
            customer_feedback = customer_feedback_match.group(1).strip()
        
        # Extract overall rating and feedback
        overall_rating_match = re.search(r'OVERALL_RATING:\s*(PASS|FAIL)', ai_response, re.IGNORECASE)
        if overall_rating_match:
            overall_rating = overall_rating_match.group(1).lower()
        
        overall_feedback_match = re.search(r'OVERALL_FEEDBACK:\s*(.*?)(?=$)', ai_response, re.IGNORECASE | re.DOTALL)
        if overall_feedback_match:
            overall_feedback = overall_feedback_match.group(1).strip()
        
        return dbc.Alert("AI labels generated successfully!", color="success", duration=4000), sales_rating, sales_feedback, customer_rating, customer_feedback, overall_rating, overall_feedback
    
    except Exception as e:
        return dbc.Alert(f"Error generating AI labels: {str(e)}", color="danger"), None, "", None, "", None, ""

@app.callback(
    [Output('labeled-conversations-count', 'children'),
     Output('labeled-conversations-summary', 'children')],
    [Input('labeled-conversations-store', 'data')]
)
def update_labeled_conversations_summary(labeled_conversations):
    if not labeled_conversations:
        return "No labeled conversations", ""
    
    # Count pass/fail for each category
    sales_pass = sum(1 for conv in labeled_conversations if conv.get('sales_agent_rating') == 'pass')
    sales_fail = sum(1 for conv in labeled_conversations if conv.get('sales_agent_rating') == 'fail')
    
    customer_pass = sum(1 for conv in labeled_conversations if conv.get('customer_agent_rating') == 'pass')
    customer_fail = sum(1 for conv in labeled_conversations if conv.get('customer_agent_rating') == 'fail')
    
    overall_pass = sum(1 for conv in labeled_conversations if conv.get('overall_rating') == 'pass')
    overall_fail = sum(1 for conv in labeled_conversations if conv.get('overall_rating') == 'fail')
    
    # Create a summary table
    table = dbc.Table([
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
                html.Td(f"{sales_pass / (sales_pass + sales_fail) * 100:.1f}%" if sales_pass + sales_fail > 0 else "N/A")
            ]),
            html.Tr([
                html.Td("Customer Agent"),
                html.Td(customer_pass),
                html.Td(customer_fail),
                html.Td(f"{customer_pass / (customer_pass + customer_fail) * 100:.1f}%" if customer_pass + customer_fail > 0 else "N/A")
            ]),
            html.Tr([
                html.Td("Overall"),
                html.Td(overall_pass),
                html.Td(overall_fail),
                html.Td(f"{overall_pass / (overall_pass + overall_fail) * 100:.1f}%" if overall_pass + overall_fail > 0 else "N/A")
            ])
        ])
    ], bordered=True, hover=True)
    
    return f"Total labeled conversations: {len(labeled_conversations)}", table

# Initialize the labeled conversations store
@app.callback(
    Output('labeled-conversations-store', 'data', allow_duplicate=True),
    [Input('refresh-conversations', 'n_clicks')],
    prevent_initial_call=True
)
def load_labeled_conversations(n_clicks):
    labeled_conversations = []
    
    # Check if the labeled conversations directory exists
    labeled_dir = "data/labeled_conversations"
    if os.path.exists(labeled_dir):
        # Load labeled conversations
        for file_path in glob.glob(f"{labeled_dir}/*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'labels' in data:
                        labeled_conversations.append(data['labels'])
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
    
    return labeled_conversations

# Run the app
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/conversations", exist_ok=True)
    os.makedirs("data/labeled_conversations", exist_ok=True)
    
    port = int(os.environ.get("PORT", 8051))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run_server(debug=debug, port=port) 