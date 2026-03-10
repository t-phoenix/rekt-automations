# Scripts Directory

This directory contains the internal automation flow Python scripts that provide an easy way to run different parts of the automation pipeline.

## Available Scripts

### Main Flow Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `run_all.py` | Run all 3 flows sequentially | `python scripts/run_all.py [--override "..."]` |
| `run_text.py` | Run text content generation only | `python scripts/run_text.py [--override "..."]` |
| `run_meme.py` | Run meme generation only | `python scripts/run_meme.py --run-id <ID> [--override "..."]` |
| `run_animation.py` | Run animation generation only | `python scripts/run_animation.py --run-id <ID>` |
| `run_trends.py` | Run trends generation | `python scripts/run_trends.py` |

### Utility Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `ingest_brand_knowledge.py` | Rebuild internal RAG index | `python scripts/ingest_brand_knowledge.py` |

## Quick Start

Before running any script, ensure the virtual environment is activated:
```bash
source venv/bin/activate
```

**Run everything:**
```bash
python scripts/run_all.py
```

**Run individual flows:**
```bash
# Step 1: Generate content
python scripts/run_text.py

# Step 2: Generate meme (use the Run ID from step 1)
python scripts/run_meme.py --run-id run_20260113_072000_a1b2

# Step 3: Animate (use the same Run ID)
python scripts/run_animation.py --run-id run_20260113_072000_a1b2
```

## Supabase Configuration

This project can automatically save completed runs and media to Supabase. To set it up:

1. **Create the Schema:** Log into your Supabase project, go to the SQL Editor, and execute the queries inside [`scripts/supabase_schema.sql`](supabase_schema.sql). This will build the needed tables and storage bucket (`rekt_media`).
2. **Environment Variables:** Provide `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in your `.env`.
3. **Verify Connection:**
   Run the test script to ensure your database and storage are reachable.

```bash
python scripts/check_supabase.py
```

## Configuration Overrides

Most scripts support the `--override` flag for inline parameter overrides:

```bash
python scripts/run_all.py --override "platforms=twitter,tone=edgy"
python scripts/run_text.py --override "platforms=twitter"
python scripts/run_meme.py --run-id <ID> --override "style=bold"
```

See [../QUICKSTART.md](../QUICKSTART.md) for more examples.
