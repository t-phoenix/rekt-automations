#!/bin/bash

# Run ALL Flows Sequentially
# Usage: ./run_all.sh [--override "platforms=twitter,tone=edgy"] [--skip-animation]

# Activate virtual environment
source venv/bin/activate

# Run all flows with all arguments passed through
python3 src/scripts/run_all_flows.py "$@"
