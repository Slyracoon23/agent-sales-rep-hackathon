# Sales Simulation Visualization

A dashboard for visualizing sales simulation test results using Dash and Plotly.

## Overview

This tool reads test results from the `test-results` directory and visualizes:
- Simulation success rates
- Conversation flows
- Agent evaluations
- Performance metrics

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd sales-viz

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

Then open your browser and navigate to `http://localhost:8050`.

## Features

- Summary dashboard of simulation results
- Detailed conversation viewer
- Agent evaluation metrics
- Performance analysis
- Historical comparison of test runs

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