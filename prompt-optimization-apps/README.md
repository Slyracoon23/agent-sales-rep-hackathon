# Prompt Optimization Apps

This project contains 7 separate Dash applications, each focused on a single step of the prompt optimization process for sales agent simulations.

## Overview of the Prompt Optimization Process

1. **Step 1: Create Agent Prompts & Generate Synthetic Data** - Create initial agent prompts and generate synthetic conversations.
2. **Step 2: Clean and Label Data** - Process conversation data with natural language feedback and structured pass/fail labels.
3. **Step 3: Build Grader System Prompt** - Create a grader system prompt that evaluates conversations.
4. **Step 4: Optimize Grader Prompt** - Improve the grader prompt for better evaluation accuracy.
5. **Step 5: Evaluate Grader Performance** - Test the grader against labeled synthetic data.
6. **Step 6: Optimize Agent System Prompt** - Update agent system prompts using newly generated synthetic data.
7. **Step 7: Evaluate Agent Performance** - Test agent performance against the grader prompt.

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
2. Set up your OpenAI API key:
   - Copy `.env.example` to `.env` in each app directory
   - Add your OpenAI API key to each `.env` file:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

## Running the Applications

Each application can be run independently:

```
cd prompt-optimization-apps/step1_agent_prompts
python app.py
```

The dashboard will be available at http://localhost:8050 (or another port if specified).

## Directory Structure

```
prompt-optimization-apps/
├── requirements.txt           # Common Python dependencies
├── README.md                  # This file
├── step1_agent_prompts/       # App for creating agent prompts
├── step2_data_cleaning/       # App for cleaning and labeling data
├── step3_grader_prompt/       # App for building grader system prompt
├── step4_grader_optimization/ # App for optimizing grader prompt
├── step5_grader_evaluation/   # App for evaluating grader performance
├── step6_agent_optimization/  # App for optimizing agent system prompt
└── step7_agent_evaluation/    # App for evaluating agent performance
```

## Requirements

- Python 3.8+
- Dash
- Plotly
- Pandas
- NumPy
- OpenAI API key 