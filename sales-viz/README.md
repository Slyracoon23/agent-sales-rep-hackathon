# Sales Simulation Dashboard

A dashboard for visualizing and optimizing sales agent and customer agent interactions from simulated conversations.

## Features

- Dashboard overview of simulation results
- Detailed conversation analysis
- Prompt optimization tools using OpenAI's GPT-4o-mini
- User feedback collection

## Setup

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

## Running the Application

Run the application with:

```
python app.py
```

The dashboard will be available at http://localhost:8050

## Using the Optimizer

The Optimizer tab allows you to improve system prompts and grader prompts using OpenAI's GPT-4o-mini model:

1. Select a simulation to optimize
2. Choose between optimizing the grader prompt or system prompts
3. Set your optimization parameters
4. Click "Generate Optimized Prompt"
5. Review the optimized prompt
6. Apply the optimized prompt if satisfied

Note: You must have a valid OpenAI API key set in your `.env` file to use the optimizer features.

## Directory Structure

```
sales-viz/
├── app.py                 # Main Dash application
├── data_loader.py         # Functions to load and process test data
├── visualizations.py      # Visualization components
├── assets/                # Static assets (CSS, images)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Requirements

- Python 3.8+
- Dash
- Plotly
- Pandas
- NumPy 