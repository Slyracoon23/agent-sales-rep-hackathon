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
app.title = "Step 4: Optimize Grader Prompt"

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
    # Check if the grader prompt exists in the step3 app
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
            html.H1("Step 4: Optimize Grader Prompt", className="text-center my-4"),
            html.P("Improve the grader prompt for better evaluation accuracy.", className="text-center mb-4"),
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
                dbc.CardHeader("Optimization Settings"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Optimization Focus"),
                            dcc.Dropdown(
                                id='optimization-focus',
                                options=[
                                    {'label': 'Improve Overall Accuracy', 'value': 'overall_accuracy'},
                                    {'label': 'Improve Sales Agent Evaluation', 'value': 'sales_agent'},
                                    {'label': 'Improve Customer Agent Evaluation', 'value': 'customer_agent'},
                                    {'label': 'Improve Feedback Quality', 'value': 'feedback_quality'},
                                    {'label': 'Reduce False Positives', 'value': 'reduce_false_positives'},
                                    {'label': 'Reduce False Negatives', 'value': 'reduce_false_negatives'}
                                ],
                                value='overall_accuracy',
                                multi=False
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Optimization Strength"),
                            dcc.Slider(
                                id='optimization-strength',
                                min=1,
                                max=10,
                                step=1,
                                value=5,
                                marks={i: str(i) for i in range(1, 11)},
                            ),
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Test Conversations"),
                            dcc.Dropdown(
                                id='test-conversations',
                                options=[],
                                placeholder="Select conversations to test optimization",
                                multi=True
                            ),
                        ], width=12, className="mt-3"),
                    ]),
                    dbc.Button("Optimize Grader Prompt", id="optimize-prompt", color="primary", className="mt-3"),
                    html.Div(id="optimization-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Optimized Grader Prompt"),
                dbc.CardBody([
                    html.Div(id="optimized-prompt-container"),
                    dbc.Button("Save Optimized Prompt", id="save-optimized-prompt", color="success", className="mt-2 me-2"),
                    dbc.Button("Test Optimized Prompt", id="test-optimized-prompt", color="info", className="mt-2"),
                    html.Div(id="save-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Optimization Results"),
                dbc.CardBody([
                    html.Div(id="optimization-results-container")
                ])
            ]),
        ], width=12)
    ]),
    
    # Store components for managing state
    dcc.Store(id='labeled-conversations-store'),
    dcc.Store(id='current-grader-prompt-store'),
    dcc.Store(id='optimized-grader-prompt-store'),
    dcc.Store(id='test-results-store'),
    
], fluid=True)

# Define callbacks
@app.callback(
    [Output('labeled-conversations-store', 'data'),
     Output('test-conversations', 'options')],
    [Input('load-grader-prompt', 'n_clicks')],
    prevent_initial_call=False
)
def load_conversations(n_clicks):
    labeled_conversations = load_labeled_conversations()
    
    # Create options for the test conversations dropdown
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
    [Output('optimization-status', 'children'),
     Output('optimized-grader-prompt-store', 'data'),
     Output('optimized-prompt-container', 'children')],
    [Input('optimize-prompt', 'n_clicks')],
    [State('current-grader-prompt-store', 'data'),
     State('labeled-conversations-store', 'data'),
     State('optimization-focus', 'value'),
     State('optimization-strength', 'value'),
     State('test-conversations', 'value')],
    prevent_initial_call=True
)
def optimize_grader_prompt(n_clicks, current_prompt, labeled_conversations, optimization_focus, optimization_strength, test_conversation_indices):
    if n_clicks is None or not current_prompt or not labeled_conversations:
        return "", "", ""
    
    if not openai_api_key:
        return dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger"), "", ""
    
    # Get the selected test conversations
    test_conversations = []
    if test_conversation_indices:
        for idx in test_conversation_indices:
            if idx < len(labeled_conversations):
                test_conversations.append(labeled_conversations[idx])
    else:
        # If no test conversations selected, use up to 3 random conversations
        import random
        test_conversations = random.sample(labeled_conversations, min(3, len(labeled_conversations)))
    
    # Format the test conversations for the AI
    formatted_examples = []
    
    for i, conv in enumerate(test_conversations):
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

HUMAN RATINGS:
Sales Agent: {labels.get('sales_agent_rating', 'Unknown').upper()}
Customer Agent: {labels.get('customer_agent_rating', 'Unknown').upper()}
Overall: {labels.get('overall_rating', 'Unknown').upper()}

HUMAN FEEDBACK:
Sales Agent Feedback: {labels.get('sales_agent_feedback', 'N/A')}
Customer Agent Feedback: {labels.get('customer_agent_feedback', 'N/A')}
Overall Feedback: {labels.get('overall_feedback', 'N/A')}

---
"""
        formatted_examples.append(example)
    
    examples_text = "\n".join(formatted_examples)
    
    # Map optimization focus to description
    focus_descriptions = {
        'overall_accuracy': "Improve the overall accuracy of the grader in matching human ratings",
        'sales_agent': "Improve the accuracy of sales agent evaluations",
        'customer_agent': "Improve the accuracy of customer agent evaluations",
        'feedback_quality': "Improve the quality and specificity of feedback",
        'reduce_false_positives': "Reduce instances where the grader gives PASS ratings when humans gave FAIL ratings",
        'reduce_false_negatives': "Reduce instances where the grader gives FAIL ratings when humans gave PASS ratings"
    }
    
    focus_description = focus_descriptions.get(optimization_focus, "Improve overall accuracy")
    
    # Create the system message
    system_message = """You are an expert prompt engineer specializing in optimizing evaluation systems for sales conversations.
Your task is to improve a grader system prompt based on human-labeled examples."""

    # Create the user message
    user_message = f"""Please optimize the following grader system prompt to {focus_description}.
The optimization strength is {optimization_strength}/10, where higher values mean more aggressive changes.

CURRENT GRADER PROMPT:
{current_prompt}

Here are some human-labeled examples to guide your optimization:

{examples_text}

Please provide an improved version of the grader prompt that:
1. Maintains the same general structure and output format
2. Focuses specifically on {focus_description}
3. Incorporates patterns and criteria from the human-labeled examples
4. Makes changes proportional to the optimization strength of {optimization_strength}/10

The optimized prompt should help the grader better match human evaluations."""

    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract the response
        optimized_prompt = response.choices[0].message.content
        
        # Create a card with the optimized prompt
        prompt_display = html.Pre(optimized_prompt, style={"white-space": "pre-wrap", "max-height": "300px", "overflow-y": "auto"})
        
        return dbc.Alert("Grader prompt optimized successfully!", color="success", duration=4000), optimized_prompt, prompt_display
    
    except Exception as e:
        return dbc.Alert(f"Error optimizing grader prompt: {str(e)}", color="danger"), "", ""

@app.callback(
    Output('save-status', 'children'),
    [Input('save-optimized-prompt', 'n_clicks')],
    [State('optimized-grader-prompt-store', 'data')],
    prevent_initial_call=True
)
def save_optimized_prompt(n_clicks, optimized_prompt):
    if n_clicks is None or not optimized_prompt:
        return ""
    
    # Create directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save the optimized prompt to a file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/optimized_grader_prompt_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(optimized_prompt)
    
    # Also save as the current grader prompt
    with open("data/grader_prompt.txt", "w") as f:
        f.write(optimized_prompt)
    
    return dbc.Alert(f"Optimized grader prompt saved successfully as {filename} and as the current grader prompt!", color="success", duration=4000)

@app.callback(
    [Output('test-results-store', 'data'),
     Output('optimization-results-container', 'children')],
    [Input('test-optimized-prompt', 'n_clicks')],
    [State('current-grader-prompt-store', 'data'),
     State('optimized-grader-prompt-store', 'data'),
     State('labeled-conversations-store', 'data'),
     State('test-conversations', 'value')],
    prevent_initial_call=True
)
def test_optimized_prompt(n_clicks, current_prompt, optimized_prompt, labeled_conversations, test_conversation_indices):
    if n_clicks is None or not current_prompt or not optimized_prompt or not labeled_conversations:
        return {}, ""
    
    if not openai_api_key:
        return {}, dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger")
    
    # Get the selected test conversations
    test_conversations = []
    if test_conversation_indices:
        for idx in test_conversation_indices:
            if idx < len(labeled_conversations):
                test_conversations.append(labeled_conversations[idx])
    else:
        # If no test conversations selected, use up to 3 random conversations
        import random
        test_conversations = random.sample(labeled_conversations, min(3, len(labeled_conversations)))
    
    # Test both prompts on the selected conversations
    current_results = []
    optimized_results = []
    
    for conv in test_conversations:
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
            # Test current prompt
            current_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": current_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Test optimized prompt
            optimized_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": optimized_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the responses
            import re
            
            # Parse current response
            current_ai_response = current_response.choices[0].message.content
            
            current_sales_rating_match = re.search(r'SALES_AGENT_RATING:\s*(PASS|FAIL)', current_ai_response, re.IGNORECASE)
            current_sales_rating = current_sales_rating_match.group(1).lower() if current_sales_rating_match else "unknown"
            
            current_customer_rating_match = re.search(r'CUSTOMER_AGENT_RATING:\s*(PASS|FAIL)', current_ai_response, re.IGNORECASE)
            current_customer_rating = current_customer_rating_match.group(1).lower() if current_customer_rating_match else "unknown"
            
            current_overall_rating_match = re.search(r'OVERALL_RATING:\s*(PASS|FAIL)', current_ai_response, re.IGNORECASE)
            current_overall_rating = current_overall_rating_match.group(1).lower() if current_overall_rating_match else "unknown"
            
            # Parse optimized response
            optimized_ai_response = optimized_response.choices[0].message.content
            
            optimized_sales_rating_match = re.search(r'SALES_AGENT_RATING:\s*(PASS|FAIL)', optimized_ai_response, re.IGNORECASE)
            optimized_sales_rating = optimized_sales_rating_match.group(1).lower() if optimized_sales_rating_match else "unknown"
            
            optimized_customer_rating_match = re.search(r'CUSTOMER_AGENT_RATING:\s*(PASS|FAIL)', optimized_ai_response, re.IGNORECASE)
            optimized_customer_rating = optimized_customer_rating_match.group(1).lower() if optimized_customer_rating_match else "unknown"
            
            optimized_overall_rating_match = re.search(r'OVERALL_RATING:\s*(PASS|FAIL)', optimized_ai_response, re.IGNORECASE)
            optimized_overall_rating = optimized_overall_rating_match.group(1).lower() if optimized_overall_rating_match else "unknown"
            
            # Get human ratings
            human_sales_rating = human_labels.get('sales_agent_rating', 'unknown')
            human_customer_rating = human_labels.get('customer_agent_rating', 'unknown')
            human_overall_rating = human_labels.get('overall_rating', 'unknown')
            
            # Calculate accuracy for current prompt
            current_matches = 0
            current_total = 0
            
            if human_sales_rating != 'unknown' and current_sales_rating != 'unknown':
                current_matches += 1 if human_sales_rating == current_sales_rating else 0
                current_total += 1
            
            if human_customer_rating != 'unknown' and current_customer_rating != 'unknown':
                current_matches += 1 if human_customer_rating == current_customer_rating else 0
                current_total += 1
            
            if human_overall_rating != 'unknown' and current_overall_rating != 'unknown':
                current_matches += 1 if human_overall_rating == current_overall_rating else 0
                current_total += 1
            
            current_accuracy = (current_matches / current_total) * 100 if current_total > 0 else 0
            
            # Calculate accuracy for optimized prompt
            optimized_matches = 0
            optimized_total = 0
            
            if human_sales_rating != 'unknown' and optimized_sales_rating != 'unknown':
                optimized_matches += 1 if human_sales_rating == optimized_sales_rating else 0
                optimized_total += 1
            
            if human_customer_rating != 'unknown' and optimized_customer_rating != 'unknown':
                optimized_matches += 1 if human_customer_rating == optimized_customer_rating else 0
                optimized_total += 1
            
            if human_overall_rating != 'unknown' and optimized_overall_rating != 'unknown':
                optimized_matches += 1 if human_overall_rating == optimized_overall_rating else 0
                optimized_total += 1
            
            optimized_accuracy = (optimized_matches / optimized_total) * 100 if optimized_total > 0 else 0
            
            # Store results
            current_results.append({
                'conversation_id': conv.get('id', ''),
                'human_sales_rating': human_sales_rating,
                'human_customer_rating': human_customer_rating,
                'human_overall_rating': human_overall_rating,
                'current_sales_rating': current_sales_rating,
                'current_customer_rating': current_customer_rating,
                'current_overall_rating': current_overall_rating,
                'current_accuracy': current_accuracy
            })
            
            optimized_results.append({
                'conversation_id': conv.get('id', ''),
                'human_sales_rating': human_sales_rating,
                'human_customer_rating': human_customer_rating,
                'human_overall_rating': human_overall_rating,
                'optimized_sales_rating': optimized_sales_rating,
                'optimized_customer_rating': optimized_customer_rating,
                'optimized_overall_rating': optimized_overall_rating,
                'optimized_accuracy': optimized_accuracy
            })
            
        except Exception as e:
            print(f"Error testing prompts: {str(e)}")
    
    # Calculate overall accuracy
    current_overall_accuracy = sum(result['current_accuracy'] for result in current_results) / len(current_results) if current_results else 0
    optimized_overall_accuracy = sum(result['optimized_accuracy'] for result in optimized_results) / len(optimized_results) if optimized_results else 0
    
    # Create results display
    results_data = {
        'current_results': current_results,
        'optimized_results': optimized_results,
        'current_overall_accuracy': current_overall_accuracy,
        'optimized_overall_accuracy': optimized_overall_accuracy
    }
    
    # Create accuracy comparison chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Current Prompt', 'Optimized Prompt'],
        y=[current_overall_accuracy, optimized_overall_accuracy],
        text=[f"{current_overall_accuracy:.1f}%", f"{optimized_overall_accuracy:.1f}%"],
        textposition='auto',
        marker_color=['#1f77b4', '#2ca02c']
    ))
    
    fig.update_layout(
        title='Accuracy Comparison',
        xaxis_title='Prompt Version',
        yaxis_title='Accuracy (%)',
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    # Create detailed results table
    table_rows = []
    
    for i in range(len(current_results)):
        current = current_results[i]
        optimized = optimized_results[i]
        
        table_rows.append(html.Tr([
            html.Td(current['conversation_id']),
            html.Td(f"{current['current_accuracy']:.1f}%"),
            html.Td(f"{optimized['optimized_accuracy']:.1f}%"),
            html.Td(f"{optimized['optimized_accuracy'] - current['current_accuracy']:.1f}%")
        ]))
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Conversation ID"),
                html.Th("Current Accuracy"),
                html.Th("Optimized Accuracy"),
                html.Th("Improvement")
            ])
        ]),
        html.Tbody(table_rows)
    ], bordered=True, hover=True)
    
    # Create the results container
    results_display = [
        html.H5("Optimization Results"),
        dcc.Graph(figure=fig),
        html.H6("Detailed Results by Conversation"),
        table,
        html.Div([
            html.Strong("Overall Improvement: "),
            html.Span(f"{optimized_overall_accuracy - current_overall_accuracy:.1f}%")
        ], className="mt-3")
    ]
    
    return results_data, results_display

# Run the app
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    
    port = int(os.environ.get("PORT", 8053))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run_server(debug=debug, port=port) 