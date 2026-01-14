#!/bin/bash

# Run Text Content Generation Flow
# Usage: ./run_text.sh [--override "key=value,key2=value2"]

# Activate virtual environment
source venv/bin/activate

# Run text flow with all arguments passed through
python3 src/scripts/run_text_flow.py "$@"
