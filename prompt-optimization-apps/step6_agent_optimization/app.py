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
app.title = "Step 6: Optimize Agent System Prompt"

# Function to load agent prompts
def load_agent_prompts():
    prompts = {
        'sales_agent': '',
        'customer_agent': ''
    }
    
    # Check if the prompts exist in the step1 app
    step1_dir = "../step1_agent_prompts/data"
    if os.path.exists(f"{step1_dir}/sales_agent_prompt.txt"):
        with open(f"{step1_dir}/sales_agent_prompt.txt", 'r') as f:
            prompts['sales_agent'] = f.read()
    
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

# Function to generate optimized prompt with OpenAI
def generate_optimized_prompt_with_openai(current_prompt, conversation_text, optimization_goal, optimization_areas, agent_type):
    # Create the system message
    system_message = """You are an expert prompt engineer specializing in optimizing system prompts for AI agents.
Your task is to optimize a system prompt based on the provided conversation examples and optimization goals."""

    # Create the user message
    user_message = f"""Please optimize the following {agent_type.replace('_', ' ')} system prompt based on the provided conversation examples and optimization goals.

CURRENT PROMPT:
{current_prompt}

CONVERSATION EXAMPLE:
{conversation_text}

OPTIMIZATION GOAL: {optimization_goal}

AREAS TO OPTIMIZE:
{', '.join(optimization_areas)}

Please provide an optimized version of the prompt that addresses the optimization goal and focuses on the specified areas.
The optimized prompt should be comprehensive but concise, and should maintain the original purpose of the prompt while improving its effectiveness.
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
            max_tokens=1500
        )
        
        # Extract the response
        optimized_prompt = response.choices[0].message.content
        
        return optimized_prompt
    
    except Exception as e:
        print(f"Error generating optimized prompt: {str(e)}")
        return current_prompt

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Step 6: Optimize Agent System Prompt", className="text-center my-4"),
            html.P("Update agent system prompts using newly generated synthetic data.", className="text-center mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Agent Selection"),
                dbc.CardBody([
                    html.Label("Select Agent Type to Optimize"),
                    dcc.RadioItems(
                        id='agent-type-selector',
                        options=[
                            {'label': 'Sales Agent', 'value': 'sales_agent'},
                            {'label': 'Customer Agent', 'value': 'customer_agent'}
                        ],
                        value='sales_agent',
                        className="mb-2"
                    ),
                    dbc.Button("Load Agent Prompts", id="load-agent-prompts", color="secondary", className="mt-2"),
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Current Agent Prompt"),
                dbc.CardBody([
                    html.Div(id="current-agent-prompt-container"),
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
                            html.Label("Optimization Goal"),
                            dcc.Dropdown(
                                id='optimization-goal',
                                options=[
                                    {'label': 'Improve Clarity and Specificity', 'value': 'clarity'},
                                    {'label': 'Enhance Persuasiveness', 'value': 'persuasiveness'},
                                    {'label': 'Increase Empathy and Rapport', 'value': 'empathy'},
                                    {'label': 'Strengthen Technical Knowledge', 'value': 'technical'},
                                    {'label': 'Improve Objection Handling', 'value': 'objections'},
                                    {'label': 'Enhance Overall Effectiveness', 'value': 'effectiveness'}
                                ],
                                value='effectiveness',
                                className="mb-2"
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Areas to Optimize"),
                            dcc.Checklist(
                                id='optimization-areas',
                                options=[
                                    {'label': 'Tone and Language', 'value': 'tone'},
                                    {'label': 'Structure and Organization', 'value': 'structure'},
                                    {'label': 'Content and Information', 'value': 'content'},
                                    {'label': 'Instructions and Guidelines', 'value': 'instructions'},
                                    {'label': 'Examples and Scenarios', 'value': 'examples'}
                                ],
                                value=['tone', 'content', 'instructions'],
                                className="mb-2"
                            ),
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Conversations for Optimization"),
                            dcc.Dropdown(
                                id='optimization-conversations',
                                options=[],
                                multi=True,
                                placeholder="Select conversations to use for optimization",
                                className="mb-2"
                            ),
                        ], width=12),
                    ]),
                    dbc.Button("Generate Optimized Prompt", id="generate-optimized-prompt", color="primary", className="mt-3"),
                    html.Div(id="optimization-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Optimized Agent Prompt"),
                dbc.CardBody([
                    html.Div(id="optimized-agent-prompt-container"),
                    dbc.Button("Save Optimized Prompt", id="save-optimized-prompt", color="success", className="mt-3"),
                    html.Div(id="save-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Test Optimized Prompt"),
                dbc.CardBody([
                    html.P("Generate a test conversation using the optimized prompt and evaluate it with the grader."),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Conversation Scenario"),
                            dcc.Dropdown(
                                id='test-scenario',
                                options=[
                                    {'label': 'Small Business (5-20 employees)', 'value': 'small_business'},
                                    {'label': 'Medium Business (20-100 employees)', 'value': 'medium_business'},
                                    {'label': 'Enterprise (100+ employees)', 'value': 'enterprise'},
                                    {'label': 'Startup', 'value': 'startup'},
                                    {'label': 'Non-profit', 'value': 'nonprofit'}
                                ],
                                value='small_business',
                                className="mb-2"
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Conversation Length"),
                            dcc.Slider(
                                id='test-conversation-length',
                                min=5,
                                max=20,
                                step=1,
                                value=10,
                                marks={i: str(i) for i in [5, 10, 15, 20]},
                            ),
                        ], width=6),
                    ]),
                    dbc.Button("Generate and Test Conversation", id="generate-test-conversation", color="info", className="mt-3"),
                    html.Div(id="test-status")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Test Results"),
                dbc.CardBody([
                    html.Div(id="test-results-container")
                ])
            ]),
        ], width=12)
    ]),
    
    # Store components for managing state
    dcc.Store(id='agent-prompts-store'),
    dcc.Store(id='grader-prompt-store'),
    dcc.Store(id='labeled-conversations-store'),
    dcc.Store(id='optimized-prompt-store'),
    dcc.Store(id='test-conversation-store'),
    dcc.Store(id='test-results-store'),
    
], fluid=True)

# Define callbacks
@app.callback(
    [Output('agent-prompts-store', 'data'),
     Output('grader-prompt-store', 'data'),
     Output('labeled-conversations-store', 'data'),
     Output('optimization-conversations', 'options')],
    [Input('load-agent-prompts', 'n_clicks')],
    prevent_initial_call=False
)
def load_data(n_clicks):
    agent_prompts = load_agent_prompts()
    grader_prompt = load_grader_prompt()
    labeled_conversations = load_labeled_conversations()
    
    # Create options for the optimization conversations dropdown
    options = []
    for i, conv in enumerate(labeled_conversations):
        conv_id = conv.get('id', f"conversation_{i}")
        scenario = conv.get('scenario', 'Unknown')
        
        # Get the labels
        labels = conv.get('labels', {})
        sales_rating = labels.get('sales_agent_rating', 'unknown')
        customer_rating = labels.get('customer_agent_rating', 'unknown')
        overall_rating = labels.get('overall_rating', 'unknown')
        
        # Add ratings to the label
        label = f"{conv_id} - {scenario.replace('_', ' ').title()} - Sales: {sales_rating.upper()}, Customer: {customer_rating.upper()}, Overall: {overall_rating.upper()}"
        options.append({'label': label, 'value': i})
    
    return agent_prompts, grader_prompt, labeled_conversations, options

@app.callback(
    Output('current-agent-prompt-container', 'children'),
    [Input('agent-prompts-store', 'data'),
     Input('agent-type-selector', 'value')]
)
def update_current_agent_prompt(agent_prompts, agent_type):
    if not agent_prompts:
        return "No agent prompts loaded. Please load agent prompts first."
    
    current_prompt = agent_prompts.get(agent_type, "")
    
    if not current_prompt:
        return f"No {agent_type.replace('_', ' ')} prompt found. Please create one in Step 1."
    
    # Create a card with the current agent prompt
    return html.Pre(current_prompt, style={"white-space": "pre-wrap", "max-height": "300px", "overflow-y": "auto"})

@app.callback(
    [Output('optimization-status', 'children'),
     Output('optimized-prompt-store', 'data'),
     Output('optimized-agent-prompt-container', 'children')],
    [Input('generate-optimized-prompt', 'n_clicks')],
    [State('agent-prompts-store', 'data'),
     State('agent-type-selector', 'value'),
     State('optimization-goal', 'value'),
     State('optimization-areas', 'value'),
     State('optimization-conversations', 'value'),
     State('labeled-conversations-store', 'data')],
    prevent_initial_call=True
)
def generate_optimized_prompt(n_clicks, agent_prompts, agent_type, optimization_goal, optimization_areas, selected_indices, labeled_conversations):
    if n_clicks is None or not agent_prompts or not optimization_goal or not optimization_areas:
        return "", None, ""
    
    if not openai_api_key:
        return dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger"), None, ""
    
    if not selected_indices:
        return dbc.Alert("Please select at least one conversation for optimization.", color="warning"), None, ""
    
    # Get the current prompt
    current_prompt = agent_prompts.get(agent_type, "")
    
    if not current_prompt:
        return dbc.Alert(f"No {agent_type.replace('_', ' ')} prompt found. Please create one in Step 1.", color="danger"), None, ""
    
    # Format the selected conversations
    formatted_conversations = []
    
    for idx in selected_indices:
        if idx < len(labeled_conversations):
            conv = labeled_conversations[idx]
            conversation_text = ""
            
            if "conversation" in conv:
                for msg in conv["conversation"]:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    conversation_text += f"{role.replace('_', ' ').title()}: {content}\n\n"
            elif "conversation_text" in conv:
                conversation_text = conv.get("conversation_text", "")
            
            formatted_conversations.append(conversation_text)
    
    # Join the conversations
    all_conversations = "\n\n---\n\n".join(formatted_conversations)
    
    # Map optimization goal to a more descriptive text
    goal_descriptions = {
        'clarity': "Improve the clarity and specificity of the prompt to provide more detailed guidance",
        'persuasiveness': "Enhance the persuasiveness of the agent to better convince customers",
        'empathy': "Increase empathy and rapport-building capabilities to better connect with customers",
        'technical': "Strengthen technical knowledge and product information to better answer customer questions",
        'objections': "Improve objection handling to better address customer concerns",
        'effectiveness': "Enhance overall effectiveness to achieve better conversation outcomes"
    }
    
    optimization_goal_text = goal_descriptions.get(optimization_goal, optimization_goal)
    
    # Generate the optimized prompt
    try:
        optimized_prompt = generate_optimized_prompt_with_openai(
            current_prompt, 
            all_conversations, 
            optimization_goal_text, 
            optimization_areas,
            agent_type
        )
        
        # Create a card with the optimized prompt
        optimized_display = html.Pre(optimized_prompt, style={"white-space": "pre-wrap", "max-height": "300px", "overflow-y": "auto"})
        
        return dbc.Alert("Optimized prompt generated successfully!", color="success"), optimized_prompt, optimized_display
    
    except Exception as e:
        return dbc.Alert(f"Error generating optimized prompt: {str(e)}", color="danger"), None, ""

@app.callback(
    Output('save-status', 'children'),
    [Input('save-optimized-prompt', 'n_clicks')],
    [State('optimized-prompt-store', 'data'),
     State('agent-type-selector', 'value')],
    prevent_initial_call=True
)
def save_optimized_prompt(n_clicks, optimized_prompt, agent_type):
    if n_clicks is None or not optimized_prompt:
        return ""
    
    # Create directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save the prompt to a file
    filename = f"data/{agent_type}_prompt.txt"
    with open(filename, "w") as f:
        f.write(optimized_prompt)
    
    return dbc.Alert(f"{agent_type.replace('_', ' ').title()} prompt saved successfully!", color="success", duration=4000)

@app.callback(
    [Output('test-status', 'children'),
     Output('test-conversation-store', 'data'),
     Output('test-results-store', 'data'),
     Output('test-results-container', 'children')],
    [Input('generate-test-conversation', 'n_clicks')],
    [State('agent-prompts-store', 'data'),
     State('optimized-prompt-store', 'data'),
     State('agent-type-selector', 'value'),
     State('grader-prompt-store', 'data'),
     State('test-scenario', 'value'),
     State('test-conversation-length', 'value')],
    prevent_initial_call=True
)
def generate_and_test_conversation(n_clicks, agent_prompts, optimized_prompt, agent_type, grader_prompt, scenario, conversation_length):
    if n_clicks is None or not agent_prompts or not optimized_prompt or not grader_prompt:
        return "", None, None, ""
    
    if not openai_api_key:
        return dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger"), None, None, ""
    
    # Get the current prompts
    current_agent_prompt = agent_prompts.get(agent_type, "")
    other_agent_type = "customer_agent" if agent_type == "sales_agent" else "sales_agent"
    other_agent_prompt = agent_prompts.get(other_agent_type, "")
    
    if not current_agent_prompt or not other_agent_prompt:
        return dbc.Alert("Missing agent prompts. Please create them in Step 1.", color="danger"), None, None, ""
    
    # Generate a conversation with the optimized prompt
    try:
        # Create a system message for the conversation generation
        if agent_type == "sales_agent":
            system_message = f"""Generate a realistic sales conversation between a sales agent and a customer.
The conversation should be about {conversation_length} messages long (alternating between sales agent and customer).

Sales Agent Prompt:
{optimized_prompt}

Customer Agent Prompt:
{other_agent_prompt}

Scenario: {scenario.replace('_', ' ').title()}

Format the conversation as a JSON array of message objects, each with 'role' (either 'sales_agent' or 'customer') and 'content' fields.
"""
        else:  # agent_type == "customer_agent"
            system_message = f"""Generate a realistic sales conversation between a sales agent and a customer.
The conversation should be about {conversation_length} messages long (alternating between sales agent and customer).

Sales Agent Prompt:
{other_agent_prompt}

Customer Agent Prompt:
{optimized_prompt}

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
            
            # Format the conversation for display
            conversation_display = []
            conversation_text_formatted = ""
            
            for msg in conversation_json:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                conversation_display.append(
                    dbc.ListGroupItem([
                        html.Strong(f"{role.replace('_', ' ').title()}: "),
                        html.Span(content)
                    ])
                )
                
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
            test_results = {
                'sales_rating': sales_rating,
                'customer_rating': customer_rating,
                'overall_rating': overall_rating,
                'sales_feedback': sales_feedback,
                'customer_feedback': customer_feedback,
                'overall_feedback': overall_feedback
            }
            
            # Create the results display
            results_display = [
                html.H5("Generated Conversation"),
                dbc.ListGroup(conversation_display, className="mb-4"),
                html.H5("Grader Evaluation"),
                dbc.Card([
                    dbc.CardHeader(f"Sales Agent Rating: {sales_rating.upper()}"),
                    dbc.CardBody(sales_feedback)
                ], className="mb-2"),
                dbc.Card([
                    dbc.CardHeader(f"Customer Agent Rating: {customer_rating.upper()}"),
                    dbc.CardBody(customer_feedback)
                ], className="mb-2"),
                dbc.Card([
                    dbc.CardHeader(f"Overall Rating: {overall_rating.upper()}"),
                    dbc.CardBody(overall_feedback)
                ], className="mb-2")
            ]
            
            return dbc.Alert("Conversation generated and evaluated successfully!", color="success"), conversation_json, test_results, results_display
        
        except json.JSONDecodeError:
            return dbc.Alert("Error parsing the generated conversation. Please try again.", color="danger"), None, None, ""
    
    except Exception as e:
        return dbc.Alert(f"Error generating or evaluating conversation: {str(e)}", color="danger"), None, None, ""

# Run the app
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    
    port = int(os.environ.get("PORT", 8055))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run_server(debug=debug, port=port) 