# Python Runner Scripts

This directory contains Python runner scripts for the automation flows.

## Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `run_all_flows.py` | Run all 3 flows sequentially | `python3 src/scripts/run_all_flows.py [--override "..."]` |
| `run_text_flow.py` | Run text content generation only | `python3 src/scripts/run_text_flow.py [--override "..."]` |
| `run_meme_flow.py` | Run meme generation only | `python3 src/scripts/run_meme_flow.py --run-id <ID> [--override "..."]` |
| `run_animation_flow.py` | Run animation generation only | `python3 src/scripts/run_animation_flow.py --run-id <ID>` |

## Usage

**Recommended: Use shell scripts instead**

For easier execution with automatic venv activation, use the shell scripts in `scripts/`:
```bash
./scripts/run_all.sh
./scripts/run_text.sh
./scripts/run_meme.sh --run-id <ID>
./scripts/run_animation.sh --run-id <ID>
```

**Direct Python execution:**

Make sure to activate venv first:
```bash
source venv/bin/activate

# Run everything
python3 src/scripts/run_all_flows.py

# Or individual flows
python3 src/scripts/run_text_flow.py
python3 src/scripts/run_meme_flow.py --run-id run_20260113_072000_a1b2
python3 src/scripts/run_animation_flow.py --run-id run_20260113_072000_a1b2
```

## Configuration Overrides

All scripts support `--override` flag:
```bash
python3 src/scripts/run_all_flows.py --override "platforms=twitter,tone=edgy"
python3 src/scripts/run_text_flow.py --override "platforms=twitter"
python3 src/scripts/run_meme_flow.py --run-id <ID> --override "style=bold"
```

## Features

✅ Rich console output with colors  
✅ Progress tracking  
✅ Error handling  
✅ Next steps guidance  
✅ Support for run ID chaining  

See [../../QUICKSTART.md](../../QUICKSTART.md) for more examples.
