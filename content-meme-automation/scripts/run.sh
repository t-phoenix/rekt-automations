#!/bin/bash
# Helper script to run the automation with the virtual environment

# Activate virtual environment
source venv/bin/activate

# Run the automation
python main.py "$@"
