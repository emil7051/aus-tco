#!/bin/bash
# Script to activate virtual environment and run the TCO modeller

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Run the Streamlit app
streamlit run app.py 