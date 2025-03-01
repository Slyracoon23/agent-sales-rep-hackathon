import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import json
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
app.title = "Step 1: Create Agent Prompts & Generate Synthetic Data"

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Step 1: Create Agent Prompts & Generate Synthetic Data", className="text-center my-4"),
            html.P("Create initial agent prompts and generate synthetic conversations.", className="text-center mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Sales Agent Prompt"),
                dbc.CardBody([
                    dcc.Textarea(
                        id='sales-agent-prompt',
                        value="""You are a sales agent for a software company that sells project management software. 
Your goal is to understand the customer's needs and convince them that our software is the right solution.
Be professional, empathetic, and focus on how our product can solve their specific problems.
Do not be overly aggressive or make false promises about the product's capabilities.""",
                        style={'width': '100%', 'height': 200},
                    ),
                    dbc.Button("Save Sales Agent Prompt", id="save-sales-prompt", color="primary", className="mt-2"),
                    html.Div(id="sales-prompt-save-status")
                ])
            ], className="mb-4"),
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Customer Agent Prompt"),
                dbc.CardBody([
                    dcc.Textarea(
                        id='customer-agent-prompt',
                        value="""You are a potential customer interested in project management software for your team of 15 people.
You have some specific requirements and concerns that need to be addressed before making a purchase decision.
Ask relevant questions about the product's features, pricing, and support.
Be somewhat skeptical but open to being convinced if the sales agent addresses your concerns effectively.""",
                        style={'width': '100%', 'height': 200},
                    ),
                    dbc.Button("Save Customer Agent Prompt", id="save-customer-prompt", color="primary", className="mt-2"),
                    html.Div(id="customer-prompt-save-status")
                ])
            ], className="mb-4"),
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Synthetic Conversation Generation"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Number of Conversations to Generate"),
                            dcc.Slider(
                                id='num-conversations',
                                min=1,
                                max=10,
                                step=1,
                                value=3,
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
                                value=['small_business', 'medium_business'],
                                multi=True
                            ),
                        ], width=12, className="mt-3"),
                    ]),
                    dbc.Button("Generate Synthetic Conversations", id="generate-conversations", color="success", className="mt-3"),
                    html.Div(id="generation-status", className="mt-2")
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Generated Conversations"),
                dbc.CardBody([
                    html.Div(id="generated-conversations-container")
                ])
            ]),
        ], width=12)
    ]),
    
], fluid=True)

# Define callbacks
@app.callback(
    Output("sales-prompt-save-status", "children"),
    Input("save-sales-prompt", "n_clicks"),
    State("sales-agent-prompt", "value"),
    prevent_initial_call=True
)
def save_sales_prompt(n_clicks, prompt):
    if n_clicks is None:
        return ""
    
    # Create directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save the prompt to a file
    with open("data/sales_agent_prompt.txt", "w") as f:
        f.write(prompt)
    
    return dbc.Alert("Sales agent prompt saved successfully!", color="success", duration=4000)

@app.callback(
    Output("customer-prompt-save-status", "children"),
    Input("save-customer-prompt", "n_clicks"),
    State("customer-agent-prompt", "value"),
    prevent_initial_call=True
)
def save_customer_prompt(n_clicks, prompt):
    if n_clicks is None:
        return ""
    
    # Create directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save the prompt to a file
    with open("data/customer_agent_prompt.txt", "w") as f:
        f.write(prompt)
    
    return dbc.Alert("Customer agent prompt saved successfully!", color="success", duration=4000)

@app.callback(
    [Output("generation-status", "children"),
     Output("generated-conversations-container", "children")],
    Input("generate-conversations", "n_clicks"),
    [State("sales-agent-prompt", "value"),
     State("customer-agent-prompt", "value"),
     State("num-conversations", "value"),
     State("conversation-length", "value"),
     State("conversation-scenarios", "value")],
    prevent_initial_call=True
)
def generate_conversations(n_clicks, sales_prompt, customer_prompt, num_conversations, conversation_length, scenarios):
    if n_clicks is None:
        return "", ""
    
    if not openai_api_key:
        return dbc.Alert("OpenAI API key not found. Please set it in the .env file.", color="danger"), ""
    
    # Create directory if it doesn't exist
    os.makedirs("data/conversations", exist_ok=True)
    
    # Generate conversations
    conversations = []
    
    for i in range(num_conversations):
        # Select a random scenario
        scenario = np.random.choice(scenarios)
        
        # Create a system message for the conversation generation
        system_message = f"""Generate a realistic sales conversation between a sales agent and a customer.
The conversation should be about {conversation_length} messages long (alternating between sales agent and customer).

Sales Agent Prompt:
{sales_prompt}

Customer Agent Prompt:
{customer_prompt}

Scenario: {scenario.replace('_', ' ').title()}

Format the conversation as a JSON array of message objects, each with 'role' (either 'sales_agent' or 'customer') and 'content' fields.
"""

        try:
            # Call the OpenAI API
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
                
                # Add metadata
                conversation_data = {
                    "id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                    "timestamp": datetime.now().isoformat(),
                    "scenario": scenario,
                    "sales_agent_prompt": sales_prompt,
                    "customer_agent_prompt": customer_prompt,
                    "conversation": conversation_json
                }
                
                # Save to file
                filename = f"data/conversations/conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.json"
                with open(filename, "w") as f:
                    json.dump(conversation_data, f, indent=2)
                
                conversations.append(conversation_data)
                
            except json.JSONDecodeError:
                # If JSON parsing fails, save the raw text
                conversation_data = {
                    "id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                    "timestamp": datetime.now().isoformat(),
                    "scenario": scenario,
                    "sales_agent_prompt": sales_prompt,
                    "customer_agent_prompt": customer_prompt,
                    "conversation_text": conversation_text
                }
                
                # Save to file
                filename = f"data/conversations/conversation_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.json"
                with open(filename, "w") as f:
                    json.dump(conversation_data, f, indent=2)
                
                conversations.append(conversation_data)
        
        except Exception as e:
            return dbc.Alert(f"Error generating conversation {i+1}: {str(e)}", color="danger"), ""
    
    # Create conversation previews
    conversation_cards = []
    
    for i, conv in enumerate(conversations):
        # Create a card for each conversation
        messages = []
        
        if "conversation" in conv:
            for msg in conv["conversation"]:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                # Format the message
                messages.append(
                    dbc.ListGroupItem([
                        html.Strong(f"{role.replace('_', ' ').title()}: "),
                        html.Span(content)
                    ])
                )
        else:
            # If conversation parsing failed, show the raw text
            messages.append(
                dbc.ListGroupItem([
                    html.Strong("Raw Conversation Text: "),
                    html.Pre(conv.get("conversation_text", ""))
                ])
            )
        
        # Create the card
        card = dbc.Card([
            dbc.CardHeader(f"Conversation {i+1} - Scenario: {conv['scenario'].replace('_', ' ').title()}"),
            dbc.CardBody([
                dbc.ListGroup(messages)
            ])
        ], className="mb-4")
        
        conversation_cards.append(card)
    
    return dbc.Alert(f"Successfully generated {num_conversations} conversations!", color="success"), conversation_cards

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run_server(debug=debug, port=port) 