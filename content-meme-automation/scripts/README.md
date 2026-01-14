# Scripts Directory

This directory contains shell scripts for running the automation flows.

## Available Scripts

### Main Flow Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `run_all.sh` | Run all 3 flows sequentially | `./scripts/run_all.sh [--override "..."]` |
| `run_text.sh` | Run text content generation only | `./scripts/run_text.sh [--override "..."]` |
| `run_meme.sh` | Run meme generation only | `./scripts/run_meme.sh --run-id <ID> [--override "..."]` |
| `run_animation.sh` | Run animation generation only | `./scripts/run_animation.sh --run-id <ID>` |

### Legacy Script

| Script | Description | Usage |
|--------|-------------|-------|
| `run.sh` | Legacy main.py runner | `./scripts/run.sh [--flow text]` |

## Quick Start

**Run everything:**
```bash
./scripts/run_all.sh
```

**Run individual flows:**
```bash
# Step 1: Generate content
./scripts/run_text.sh

# Step 2: Generate meme (use the Run ID from step 1)
./scripts/run_meme.sh --run-id run_20260113_072000_a1b2

# Step 3: Animate (use the same Run ID)
./scripts/run_animation.sh --run-id run_20260113_072000_a1b2
```

## Features

✅ Automatic venv activation  
✅ Uses `python3` command  
✅ Passes through all arguments  
✅ Proper error handling  

## Configuration Overrides

All scripts support `--override` flag:

```bash
./scripts/run_all.sh --override "platforms=twitter,tone=edgy"
./scripts/run_text.sh --override "platforms=twitter"
./scripts/run_meme.sh --run-id <ID> --override "style=bold"
```

See [../QUICKSTART.md](../QUICKSTART.md) for more examples.
