#!/bin/bash

# Run Animation Flow
# Usage: ./run_animation.sh --run-id <ID> [--override "animation_style=bounce"]

# Activate virtual environment
source venv/bin/activate

# Run animation flow with all arguments passed through
python3 src/scripts/run_animation_flow.py "$@"
