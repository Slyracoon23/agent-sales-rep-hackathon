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
app.title = "Step 5: Evaluate Grader Performance"

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
    return """You are an expert evaluator of sales conversations. Your task is to analyze a conversation between a sales agent and a customer and provide ratings and feedback.

For each conversation, you should evaluate:
1. The sales agent's performance
2. The customer agent's performance
3. The overall conversation quality

For each of these categories, provide:
- A PASS or FAIL rating
- Detailed feedback explaining your rating

Format your response as follows:
SALES_AGENT_RATING: PASS or FAIL
SALES_AGENT_FEEDBACK: Your detailed feedback here...
CUSTOMER_AGENT_RATING: PASS or FAIL
CUSTOMER_AGENT_FEEDBACK: Your detailed feedback here...
OVERALL_RATING: PASS or FAIL
OVERALL_FEEDBACK: Your detailed feedback here..."""

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Step 5: Evaluate Grader Performance", className="text-center my-4"),
            html.P("Test the grader against labeled synthetic data to ensure it meets accuracy thresholds.", className="text-center mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Current Grader Prompt"),
                dbc.CardBody([
                    html.Div(id="current-grader-prompt-container"),
                    dbc.Button("Load Grader Prompt", id="load-grader-prompt", color="secondary", className="mt-2"),
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
                            html.Label("Evaluation Dataset"),
                            dcc.RadioItems(
                                id='evaluation-dataset',
                                options=[
                                    {'label': 'All Labeled Conversations', 'value': 'all'},
                                    {'label': 'Select Specific Conversations', 'value': 'select'}
                                ],
                                value='all',
                                className="mb-2"
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Accuracy Threshold (%)"),
                            dcc.Slider(
                                id='accuracy-threshold',
                                min=50,
                                max=100,
                                step=5,
                                value=90,
                                marks={i: str(i) for i in range(50, 101, 10)},
                            ),
                        ], width=6),
                    ]),
                    html.Div(
                        dcc.Dropdown(
                            id='selected-conversations',
                            options=[],
                            placeholder="Select conversations to evaluate",
                            multi=True
                        ),
                        id="selected-conversations-container",
                        style={"display": "none"},
                        className="mt-3"
                    ),
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
    
    # Store components for managing state
    dcc.Store(id='labeled-conversations-store'),
    dcc.Store(id='current-grader-prompt-store'),
    dcc.Store(id='evaluation-results-store'),
    
], fluid=True)

# Define callbacks
@app.callback(
    [Output('labeled-conversations-store', 'data'),
     Output('selected-conversations', 'options')],
    [Input('load-grader-prompt', 'n_clicks')],
    prevent_initial_call=False
)
def load_conversations(n_clicks):
    labeled_conversations = load_labeled_conversations()
    
    # Create options for the selected conversations dropdown
    options = []
    for i, conv in enumerate(labeled_conversations):
        conv_id = conv.get('id', f"conversation_{i}")
        scenario = conv.get('scenario', 'Unknown')
        
        label = f"{conv_id} - {scenario.replace('_', ' ').title()}"
        options.append({'label': label, 'value': i})
    
    return labeled_conversations, options

@app.callback(
    [Output('current-grader-prompt-store', 'data'),
     Output('current-grader-prompt-container', 'children')],
    [Input('load-grader-prompt', 'n_clicks')],
    prevent_initial_call=False
)
def update_current_grader_prompt(n_clicks):
    grader_prompt = load_grader_prompt()
    
    # Create a card with the current grader prompt
    prompt_display = html.Pre(grader_prompt, style={"white-space": "pre-wrap", "max-height": "300px", "overflow-y": "auto"})
    
    return grader_prompt, prompt_display

@app.callback(
    Output('selected-conversations-container', 'style'),
    [Input('evaluation-dataset', 'value')],
    prevent_initial_call=False
)
def toggle_conversation_selector(dataset_type):
    if dataset_type == 'select':
        return {"display": "block"}
    else:
        return {"display": "none"}

@app.callback(
    [Output('evaluation-status', 'children'),
     Output('evaluation-results-store', 'data'),
     Output('evaluation-results-container', 'children'),
     Output('detailed-analysis-container', 'children')],
    [Input('run-evaluation', 'n_clicks')],
    [State('current-grader-prompt-store', 'data'),
     State('labeled-conversations-store', 'data'),
     State('evaluation-dataset', 'value'),
     State('selected-conversations', 'value'),
     State('accuracy-threshold', 'value')],
    prevent_initial_call=True
)
def run_evaluation(n_clicks, grader_prompt, labeled_conversations, dataset_type, selected_indices, accuracy_threshold):
    if n_clicks is None or not grader_prompt or not labeled_conversations:
        return "", {}, "", ""
    
    if not openai_api_key:
        return dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger"), {}, "", ""
    
    # Get the evaluation dataset
    evaluation_conversations = []
    if dataset_type == 'all':
        evaluation_conversations = labeled_conversations
    else:  # dataset_type == 'select'
        if not selected_indices:
            return dbc.Alert("Please select at least one conversation to evaluate.", color="warning"), {}, "", ""
        
        for idx in selected_indices:
            if idx < len(labeled_conversations):
                evaluation_conversations.append(labeled_conversations[idx])
    
    # Evaluate the grader prompt on the selected conversations
    evaluation_results = []
    
    for i, conv in enumerate(evaluation_conversations):
        # Format the conversation for the AI
        conversation_text = ""
        
        if "conversation" in conv:
            for msg in conv["conversation"]:
                role = msg.get("role", "")
                content = msg.get("content", "")
                conversation_text += f"{role.replace('_', ' ').title()}: {content}\n\n"
        elif "conversation_text" in conv:
            conversation_text = conv.get("conversation_text", "")
        
        # Get the human labels
        human_labels = conv.get("labels", {})
        
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
            
            # Get human ratings
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
            
            # Store results
            evaluation_results.append({
                'conversation_id': conv.get('id', f"conversation_{i}"),
                'scenario': conv.get('scenario', 'Unknown'),
                'human_sales_rating': human_sales_rating,
                'human_customer_rating': human_customer_rating,
                'human_overall_rating': human_overall_rating,
                'ai_sales_rating': sales_rating,
                'ai_customer_rating': customer_rating,
                'ai_overall_rating': overall_rating,
                'ai_sales_feedback': sales_feedback,
                'ai_customer_feedback': customer_feedback,
                'ai_overall_feedback': overall_feedback,
                'accuracy': accuracy
            })
            
        except Exception as e:
            print(f"Error evaluating conversation {i}: {str(e)}")
    
    # Calculate overall accuracy
    overall_accuracy = sum(result['accuracy'] for result in evaluation_results) / len(evaluation_results) if evaluation_results else 0
    
    # Calculate category-specific accuracy
    sales_matches = sum(1 for result in evaluation_results 
                      if result['human_sales_rating'] != 'unknown' 
                      and result['ai_sales_rating'] != 'unknown'
                      and result['human_sales_rating'] == result['ai_sales_rating'])
    
    sales_total = sum(1 for result in evaluation_results 
                    if result['human_sales_rating'] != 'unknown' 
                    and result['ai_sales_rating'] != 'unknown')
    
    customer_matches = sum(1 for result in evaluation_results 
                         if result['human_customer_rating'] != 'unknown' 
                         and result['ai_customer_rating'] != 'unknown'
                         and result['human_customer_rating'] == result['ai_customer_rating'])
    
    customer_total = sum(1 for result in evaluation_results 
                       if result['human_customer_rating'] != 'unknown' 
                       and result['ai_customer_rating'] != 'unknown')
    
    overall_matches = sum(1 for result in evaluation_results 
                        if result['human_overall_rating'] != 'unknown' 
                        and result['ai_overall_rating'] != 'unknown'
                        and result['human_overall_rating'] == result['ai_overall_rating'])
    
    overall_total = sum(1 for result in evaluation_results 
                      if result['human_overall_rating'] != 'unknown' 
                      and result['ai_overall_rating'] != 'unknown')
    
    sales_accuracy = (sales_matches / sales_total) * 100 if sales_total > 0 else 0
    customer_accuracy = (customer_matches / customer_total) * 100 if customer_total > 0 else 0
    overall_rating_accuracy = (overall_matches / overall_total) * 100 if overall_total > 0 else 0
    
    # Check if the accuracy threshold is met
    threshold_met = overall_accuracy >= accuracy_threshold
    
    # Create results data
    results_data = {
        'evaluation_results': evaluation_results,
        'overall_accuracy': overall_accuracy,
        'sales_accuracy': sales_accuracy,
        'customer_accuracy': customer_accuracy,
        'overall_rating_accuracy': overall_rating_accuracy,
        'threshold_met': threshold_met,
        'accuracy_threshold': accuracy_threshold
    }
    
    # Create accuracy gauge chart
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_accuracy,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Grader Accuracy"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkgreen" if threshold_met else "darkred"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, accuracy_threshold], 'color': "yellow"},
                {'range': [accuracy_threshold, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': accuracy_threshold
            }
        }
    ))
    
    gauge_fig.update_layout(height=300)
    
    # Create category accuracy chart
    categories = ['Sales Agent', 'Customer Agent', 'Overall Rating']
    accuracies = [sales_accuracy, customer_accuracy, overall_rating_accuracy]
    
    category_fig = go.Figure(go.Bar(
        x=categories,
        y=accuracies,
        text=[f"{acc:.1f}%" for acc in accuracies],
        textposition='auto',
        marker_color=['blue', 'green', 'purple']
    ))
    
    category_fig.update_layout(
        title='Accuracy by Category',
        xaxis_title='Category',
        yaxis_title='Accuracy (%)',
        yaxis=dict(range=[0, 100]),
        height=300
    )
    
    # Create results summary
    results_summary = [
        dbc.Alert(
            f"Evaluation complete! Overall accuracy: {overall_accuracy:.1f}% - {'Threshold met!' if threshold_met else 'Threshold not met!'}",
            color="success" if threshold_met else "danger"
        ),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=gauge_fig)
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=category_fig)
            ], width=6)
        ])
    ]
    
    # Create detailed analysis
    # Confusion matrix for each category
    sales_tp = sum(1 for result in evaluation_results if result['human_sales_rating'] == 'pass' and result['ai_sales_rating'] == 'pass')
    sales_fp = sum(1 for result in evaluation_results if result['human_sales_rating'] == 'fail' and result['ai_sales_rating'] == 'pass')
    sales_tn = sum(1 for result in evaluation_results if result['human_sales_rating'] == 'fail' and result['ai_sales_rating'] == 'fail')
    sales_fn = sum(1 for result in evaluation_results if result['human_sales_rating'] == 'pass' and result['ai_sales_rating'] == 'fail')
    
    customer_tp = sum(1 for result in evaluation_results if result['human_customer_rating'] == 'pass' and result['ai_customer_rating'] == 'pass')
    customer_fp = sum(1 for result in evaluation_results if result['human_customer_rating'] == 'fail' and result['ai_customer_rating'] == 'pass')
    customer_tn = sum(1 for result in evaluation_results if result['human_customer_rating'] == 'fail' and result['ai_customer_rating'] == 'fail')
    customer_fn = sum(1 for result in evaluation_results if result['human_customer_rating'] == 'pass' and result['ai_customer_rating'] == 'fail')
    
    overall_tp = sum(1 for result in evaluation_results if result['human_overall_rating'] == 'pass' and result['ai_overall_rating'] == 'pass')
    overall_fp = sum(1 for result in evaluation_results if result['human_overall_rating'] == 'fail' and result['ai_overall_rating'] == 'pass')
    overall_tn = sum(1 for result in evaluation_results if result['human_overall_rating'] == 'fail' and result['ai_overall_rating'] == 'fail')
    overall_fn = sum(1 for result in evaluation_results if result['human_overall_rating'] == 'pass' and result['ai_overall_rating'] == 'fail')
    
    # Create confusion matrix tables
    sales_matrix = dbc.Table([
        html.Thead([
            html.Tr([html.Th(""), html.Th("AI: PASS"), html.Th("AI: FAIL")])
        ]),
        html.Tbody([
            html.Tr([html.Td("Human: PASS"), html.Td(sales_tp), html.Td(sales_fn)]),
            html.Tr([html.Td("Human: FAIL"), html.Td(sales_fp), html.Td(sales_tn)])
        ])
    ], bordered=True, hover=True)
    
    customer_matrix = dbc.Table([
        html.Thead([
            html.Tr([html.Th(""), html.Th("AI: PASS"), html.Th("AI: FAIL")])
        ]),
        html.Tbody([
            html.Tr([html.Td("Human: PASS"), html.Td(customer_tp), html.Td(customer_fn)]),
            html.Tr([html.Td("Human: FAIL"), html.Td(customer_fp), html.Td(customer_tn)])
        ])
    ], bordered=True, hover=True)
    
    overall_matrix = dbc.Table([
        html.Thead([
            html.Tr([html.Th(""), html.Th("AI: PASS"), html.Th("AI: FAIL")])
        ]),
        html.Tbody([
            html.Tr([html.Td("Human: PASS"), html.Td(overall_tp), html.Td(overall_fn)]),
            html.Tr([html.Td("Human: FAIL"), html.Td(overall_fp), html.Td(overall_tn)])
        ])
    ], bordered=True, hover=True)
    
    # Create detailed results table
    table_rows = []
    
    for result in evaluation_results:
        table_rows.append(html.Tr([
            html.Td(result['conversation_id']),
            html.Td(result['scenario'].replace('_', ' ').title()),
            html.Td(f"{result['human_sales_rating'].upper()} / {result['ai_sales_rating'].upper()}"),
            html.Td(f"{result['human_customer_rating'].upper()} / {result['ai_customer_rating'].upper()}"),
            html.Td(f"{result['human_overall_rating'].upper()} / {result['ai_overall_rating'].upper()}"),
            html.Td(f"{result['accuracy']:.1f}%")
        ]))
    
    results_table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Conversation ID"),
                html.Th("Scenario"),
                html.Th("Sales Rating (Human/AI)"),
                html.Th("Customer Rating (Human/AI)"),
                html.Th("Overall Rating (Human/AI)"),
                html.Th("Accuracy")
            ])
        ]),
        html.Tbody(table_rows)
    ], bordered=True, hover=True, responsive=True)
    
    # Create the detailed analysis container
    detailed_analysis = [
        html.H5("Confusion Matrices"),
        dbc.Row([
            dbc.Col([
                html.H6("Sales Agent Ratings", className="text-center"),
                sales_matrix
            ], width=4),
            dbc.Col([
                html.H6("Customer Agent Ratings", className="text-center"),
                customer_matrix
            ], width=4),
            dbc.Col([
                html.H6("Overall Ratings", className="text-center"),
                overall_matrix
            ], width=4)
        ]),
        html.H5("Detailed Results by Conversation", className="mt-4"),
        results_table
    ]
    
    # Create status message
    if threshold_met:
        status_message = dbc.Alert(
            [
                html.H4("Success! Grader Accuracy Threshold Met", className="alert-heading"),
                html.P(f"The grader achieved an overall accuracy of {overall_accuracy:.1f}%, which meets or exceeds the threshold of {accuracy_threshold}%."),
                html.Hr(),
                html.P("You can now proceed to Step 6: Optimize Agent System Prompt.")
            ],
            color="success"
        )
    else:
        status_message = dbc.Alert(
            [
                html.H4("Grader Accuracy Threshold Not Met", className="alert-heading"),
                html.P(f"The grader achieved an overall accuracy of {overall_accuracy:.1f}%, which is below the threshold of {accuracy_threshold}%."),
                html.Hr(),
                html.P("Consider returning to Step 4 to further optimize the grader prompt.")
            ],
            color="warning"
        )
    
    return status_message, results_data, results_summary, detailed_analysis

# Run the app
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    
    port = int(os.environ.get("PORT", 8054))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run_server(debug=debug, port=port) 