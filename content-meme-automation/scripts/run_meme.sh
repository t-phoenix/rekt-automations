#!/bin/bash

# Run Meme Generation Flow
# Usage: ./run_meme.sh --run-id <ID> [--override "key=value"]

# Activate virtual environment
source venv/bin/activate

# Run meme flow with all arguments passed through
python3 src/scripts/run_meme_flow.py "$@"
