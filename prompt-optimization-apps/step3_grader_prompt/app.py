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
app.title = "Step 3: Build Grader System Prompt"

# Function to load labeled conversations
def load_labeled_conversations():
    labeled_conversations = []
    
    # Check if the labeled conversations directory exists in the step2 app
    step2_labeled_dir = "../step2_data_cleaning/data/labeled_conversations"
    if os.path.exists(step2_labeled_dir):
        # Load labeled conversations from step2
        for file_path in glob.glob(f"{step2_labeled_dir}/*.json"):
            try:
                with open(file_path, 'r') as f:
                    conversation = json.load(f)
                    labeled_conversations.append(conversation)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
    
    # Also check local data directory
    local_labeled_dir = "data/labeled_conversations"
    if os.path.exists(local_labeled_dir):
        # Load labeled conversations from local directory
        for file_path in glob.glob(f"{local_labeled_dir}/*.json"):
            try:
                with open(file_path, 'r') as f:
                    conversation = json.load(f)
                    labeled_conversations.append(conversation)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
    
    return labeled_conversations

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Step 3: Build Grader System Prompt", className="text-center my-4"),
            html.P("Create a grader system prompt that evaluates conversations based on labeled data.", className="text-center mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Labeled Data Summary"),
                dbc.CardBody([
                    html.Div(id="labeled-data-summary"),
                    dbc.Button("Refresh Labeled Data", id="refresh-data", color="secondary", className="mt-2"),
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Grader Prompt Builder"),
                dbc.CardBody([
                    html.Label("Grader System Prompt"),
                    dcc.Textarea(
                        id='grader-prompt',
                        value="""You are an expert evaluator of sales conversations. Your task is to analyze a conversation between a sales agent and a customer and provide ratings and feedback.

For each conversation, you should evaluate:
1. The sales agent's performance
2. The customer agent's performance
3. The overall conversation quality

For each of these categories, provide:
- A PASS or FAIL rating
- Detailed feedback explaining your rating

A good sales agent should:
- Be professional and courteous
- Understand the customer's needs
- Clearly explain product features and benefits
- Address customer concerns effectively
- Not be overly aggressive or make false promises

A good customer agent should:
- Ask relevant questions
- Express their needs and concerns clearly
- Engage meaningfully with the sales agent

The overall conversation should:
- Flow naturally
- Cover key product information
- Address customer needs
- Progress toward a clear outcome

Format your response as follows:
SALES_AGENT_RATING: PASS or FAIL
SALES_AGENT_FEEDBACK: Your detailed feedback here...
CUSTOMER_AGENT_RATING: PASS or FAIL
CUSTOMER_AGENT_FEEDBACK: Your detailed feedback here...
OVERALL_RATING: PASS or FAIL
OVERALL_FEEDBACK: Your detailed feedback here...""",
                        style={'width': '100%', 'height': 400},
                    ),
                    dbc.Button("Save Grader Prompt", id="save-grader-prompt", color="primary", className="mt-2"),
                    html.Div(id="save-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("AI-Generated Grader Prompt"),
                dbc.CardBody([
                    html.P("Generate a grader prompt based on the labeled conversations using AI."),
                    dbc.Button("Generate AI Grader Prompt", id="generate-ai-prompt", color="success", className="mt-2"),
                    html.Div(id="ai-prompt-status"),
                    html.Div(id="ai-prompt-container", className="mt-3")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Test Grader Prompt"),
                dbc.CardBody([
                    html.Label("Select a conversation to test the grader prompt"),
                    dcc.Dropdown(
                        id='test-conversation-selector',
                        options=[],
                        placeholder="Select a conversation to test",
                    ),
                    dbc.Button("Test Grader Prompt", id="test-grader-prompt", color="info", className="mt-2"),
                    html.Div(id="test-status"),
                    html.Div(id="test-results-container", className="mt-3")
                ])
            ]),
        ], width=12)
    ]),
    
    # Store components for managing state
    dcc.Store(id='labeled-conversations-store'),
    
], fluid=True)

# Define callbacks
@app.callback(
    [Output('labeled-conversations-store', 'data'),
     Output('labeled-data-summary', 'children'),
     Output('test-conversation-selector', 'options')],
    [Input('refresh-data', 'n_clicks')],
    prevent_initial_call=False
)
def refresh_labeled_data(n_clicks):
    labeled_conversations = load_labeled_conversations()
    
    if not labeled_conversations:
        return [], "No labeled conversations found. Please complete Step 2 first.", []
    
    # Count pass/fail for each category
    sales_pass = sum(1 for conv in labeled_conversations if conv.get('labels', {}).get('sales_agent_rating') == 'pass')
    sales_fail = sum(1 for conv in labeled_conversations if conv.get('labels', {}).get('sales_agent_rating') == 'fail')
    
    customer_pass = sum(1 for conv in labeled_conversations if conv.get('labels', {}).get('customer_agent_rating') == 'pass')
    customer_fail = sum(1 for conv in labeled_conversations if conv.get('labels', {}).get('customer_agent_rating') == 'fail')
    
    overall_pass = sum(1 for conv in labeled_conversations if conv.get('labels', {}).get('overall_rating') == 'pass')
    overall_fail = sum(1 for conv in labeled_conversations if conv.get('labels', {}).get('overall_rating') == 'fail')
    
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
    
    # Create options for the test conversation selector
    options = []
    for i, conv in enumerate(labeled_conversations):
        conv_id = conv.get('id', f"conversation_{i}")
        scenario = conv.get('scenario', 'Unknown')
        
        label = f"{conv_id} - {scenario.replace('_', ' ').title()}"
        options.append({'label': label, 'value': i})
    
    summary = [
        html.P(f"Found {len(labeled_conversations)} labeled conversations"),
        table
    ]
    
    return labeled_conversations, summary, options

@app.callback(
    Output('save-status', 'children'),
    [Input('save-grader-prompt', 'n_clicks')],
    [State('grader-prompt', 'value')],
    prevent_initial_call=True
)
def save_grader_prompt(n_clicks, prompt):
    if n_clicks is None:
        return ""
    
    # Create directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save the prompt to a file
    with open("data/grader_prompt.txt", "w") as f:
        f.write(prompt)
    
    return dbc.Alert("Grader prompt saved successfully!", color="success", duration=4000)

@app.callback(
    [Output('ai-prompt-status', 'children'),
     Output('ai-prompt-container', 'children')],
    [Input('generate-ai-prompt', 'n_clicks')],
    [State('labeled-conversations-store', 'data')],
    prevent_initial_call=True
)
def generate_ai_grader_prompt(n_clicks, labeled_conversations):
    if n_clicks is None or not labeled_conversations:
        return "", ""
    
    if not openai_api_key:
        return dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger"), ""
    
    # Format the labeled conversations for the AI
    formatted_examples = []
    
    for i, conv in enumerate(labeled_conversations[:5]):  # Limit to 5 examples to avoid token limits
        conversation_text = ""
        
        if "conversation" in conv:
            for msg in conv["conversation"]:
                role = msg.get("role", "")
                content = msg.get("content", "")
                conversation_text += f"{role.replace('_', ' ').title()}: {content}\n\n"
        elif "conversation_text" in conv:
            conversation_text = conv.get("conversation_text", "")
        
        labels = conv.get("labels", {})
        
        example = f"""EXAMPLE {i+1}:

CONVERSATION:
{conversation_text}

RATINGS:
Sales Agent: {labels.get('sales_agent_rating', 'Unknown').upper()}
Customer Agent: {labels.get('customer_agent_rating', 'Unknown').upper()}
Overall: {labels.get('overall_rating', 'Unknown').upper()}

FEEDBACK:
Sales Agent Feedback: {labels.get('sales_agent_feedback', 'N/A')}
Customer Agent Feedback: {labels.get('customer_agent_feedback', 'N/A')}
Overall Feedback: {labels.get('overall_feedback', 'N/A')}

---
"""
        formatted_examples.append(example)
    
    examples_text = "\n".join(formatted_examples)
    
    # Create the system message
    system_message = """You are an expert prompt engineer specializing in creating evaluation systems for sales conversations.
Your task is to create a grader system prompt that can evaluate sales conversations based on the provided examples."""

    # Create the user message
    user_message = f"""Please create a comprehensive grader system prompt that can evaluate sales conversations.
The grader should analyze conversations between sales agents and customers, and provide ratings and feedback.

Here are some labeled examples to guide your prompt creation:

{examples_text}

Based on these examples, create a detailed grader system prompt that:
1. Explains the evaluation criteria for sales agents, customer agents, and overall conversations
2. Provides clear guidelines on what constitutes a PASS or FAIL rating for each category
3. Instructs the grader to provide detailed feedback for each category
4. Specifies the exact output format (SALES_AGENT_RATING, SALES_AGENT_FEEDBACK, etc.)

The prompt should be comprehensive but concise, focusing on the patterns and criteria demonstrated in the examples."""

    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract the response
        ai_prompt = response.choices[0].message.content
        
        # Create a card with the AI-generated prompt
        prompt_card = dbc.Card([
            dbc.CardBody([
                html.H5("AI-Generated Grader Prompt"),
                html.Pre(ai_prompt, style={"white-space": "pre-wrap"}),
                dbc.Button("Use This Prompt", id="use-ai-prompt", color="primary", className="mt-2")
            ])
        ])
        
        # Save the AI-generated prompt to a file
        os.makedirs("data", exist_ok=True)
        with open("data/ai_generated_grader_prompt.txt", "w") as f:
            f.write(ai_prompt)
        
        return dbc.Alert("AI grader prompt generated successfully!", color="success", duration=4000), prompt_card
    
    except Exception as e:
        return dbc.Alert(f"Error generating AI grader prompt: {str(e)}", color="danger"), ""

@app.callback(
    Output('grader-prompt', 'value'),
    [Input('use-ai-prompt', 'n_clicks')],
    prevent_initial_call=True
)
def use_ai_prompt(n_clicks):
    if n_clicks is None:
        return dash.no_update
    
    # Load the AI-generated prompt
    try:
        with open("data/ai_generated_grader_prompt.txt", "r") as f:
            ai_prompt = f.read()
        return ai_prompt
    except:
        return dash.no_update

@app.callback(
    [Output('test-status', 'children'),
     Output('test-results-container', 'children')],
    [Input('test-grader-prompt', 'n_clicks')],
    [State('grader-prompt', 'value'),
     State('test-conversation-selector', 'value'),
     State('labeled-conversations-store', 'data')],
    prevent_initial_call=True
)
def test_grader_prompt(n_clicks, grader_prompt, selected_index, labeled_conversations):
    if n_clicks is None or selected_index is None or not grader_prompt:
        return "", ""
    
    if not openai_api_key:
        return dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger"), ""
    
    # Get the selected conversation
    conversation = labeled_conversations[selected_index]
    
    # Format the conversation for the AI
    conversation_text = ""
    
    if "conversation" in conversation:
        for msg in conversation["conversation"]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role.replace('_', ' ').title()}: {content}\n\n"
    elif "conversation_text" in conversation:
        conversation_text = conversation.get("conversation_text", "")
    
    # Get the human labels
    human_labels = conversation.get("labels", {})
    
    # Create the user message
    user_message = f"""Please analyze the following conversation:

CONVERSATION:
{conversation_text}"""

    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": grader_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the response
        ai_response = response.choices[0].message.content
        
        # Parse the AI response
        import re
        
        # Extract ratings
        sales_rating_match = re.search(r'SALES_AGENT_RATING:\s*(PASS|FAIL)', ai_response, re.IGNORECASE)
        sales_rating = sales_rating_match.group(1).lower() if sales_rating_match else "unknown"
        
        customer_rating_match = re.search(r'CUSTOMER_AGENT_RATING:\s*(PASS|FAIL)', ai_response, re.IGNORECASE)
        customer_rating = customer_rating_match.group(1).lower() if customer_rating_match else "unknown"
        
        overall_rating_match = re.search(r'OVERALL_RATING:\s*(PASS|FAIL)', ai_response, re.IGNORECASE)
        overall_rating = overall_rating_match.group(1).lower() if overall_rating_match else "unknown"
        
        # Extract feedback
        sales_feedback_match = re.search(r'SALES_AGENT_FEEDBACK:\s*(.*?)(?=CUSTOMER_AGENT_RATING:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        sales_feedback = sales_feedback_match.group(1).strip() if sales_feedback_match else ""
        
        customer_feedback_match = re.search(r'CUSTOMER_AGENT_FEEDBACK:\s*(.*?)(?=OVERALL_RATING:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        customer_feedback = customer_feedback_match.group(1).strip() if customer_feedback_match else ""
        
        overall_feedback_match = re.search(r'OVERALL_FEEDBACK:\s*(.*?)(?=$)', ai_response, re.IGNORECASE | re.DOTALL)
        overall_feedback = overall_feedback_match.group(1).strip() if overall_feedback_match else ""
        
        # Compare with human labels
        human_sales_rating = human_labels.get('sales_agent_rating', 'unknown')
        human_customer_rating = human_labels.get('customer_agent_rating', 'unknown')
        human_overall_rating = human_labels.get('overall_rating', 'unknown')
        
        # Calculate accuracy
        matches = 0
        total = 0
        
        if human_sales_rating != 'unknown' and sales_rating != 'unknown':
            matches += 1 if human_sales_rating == sales_rating else 0
            total += 1
        
        if human_customer_rating != 'unknown' and customer_rating != 'unknown':
            matches += 1 if human_customer_rating == customer_rating else 0
            total += 1
        
        if human_overall_rating != 'unknown' and overall_rating != 'unknown':
            matches += 1 if human_overall_rating == overall_rating else 0
            total += 1
        
        accuracy = (matches / total) * 100 if total > 0 else 0
        
        # Create comparison table
        comparison_table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Category"),
                    html.Th("Human Rating"),
                    html.Th("AI Rating"),
                    html.Th("Match")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td("Sales Agent"),
                    html.Td(human_sales_rating.upper()),
                    html.Td(sales_rating.upper()),
                    html.Td("✓" if human_sales_rating == sales_rating else "✗")
                ]),
                html.Tr([
                    html.Td("Customer Agent"),
                    html.Td(human_customer_rating.upper()),
                    html.Td(customer_rating.upper()),
                    html.Td("✓" if human_customer_rating == customer_rating else "✗")
                ]),
                html.Tr([
                    html.Td("Overall"),
                    html.Td(human_overall_rating.upper()),
                    html.Td(overall_rating.upper()),
                    html.Td("✓" if human_overall_rating == overall_rating else "✗")
                ])
            ])
        ], bordered=True, hover=True)
        
        # Create the results container
        results = [
            html.H5(f"Grader Accuracy: {accuracy:.1f}%"),
            html.H6("Rating Comparison:"),
            comparison_table,
            html.H6("AI Feedback:"),
            dbc.Card([
                dbc.CardHeader("Sales Agent Feedback"),
                dbc.CardBody(sales_feedback)
            ], className="mb-2"),
            dbc.Card([
                dbc.CardHeader("Customer Agent Feedback"),
                dbc.CardBody(customer_feedback)
            ], className="mb-2"),
            dbc.Card([
                dbc.CardHeader("Overall Feedback"),
                dbc.CardBody(overall_feedback)
            ])
        ]
        
        return dbc.Alert("Grader prompt tested successfully!", color="success", duration=4000), results
    
    except Exception as e:
        return dbc.Alert(f"Error testing grader prompt: {str(e)}", color="danger"), ""

# Run the app
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/labeled_conversations", exist_ok=True)
    
    port = int(os.environ.get("PORT", 8052))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run_server(debug=debug, port=port) 