# Quick Start Guide - Flow-Based Architecture

## 🚀 Quick Start (3 Ways to Run)

### Option 1: Run Everything at Once (Simplest)

**Using Shell Script (Recommended - uses venv):**
```bash
./scripts/run_all.sh
```

**Or directly:**
```bash
python3 src/scripts/run_all_flows.py
```

This runs all 3 flows sequentially:
1. Text Content Generation
2. Meme Generation  
3. Animation

**Output:** `output/runs/run_YYYYMMDD_HHMMSS_XXXX/`

---

### Option 2: Run Individual Flows (Maximum Control)

**Using Shell Scripts (Recommended - uses venv):**

#### Step 1: Generate Text Content
```bash
./scripts/run_text.sh
# Outputs: Run ID (e.g., run_20260113_072000_a1b2)
```

#### Step 2: Generate Meme (using Run ID from Step 1)
```bash
./scripts/run_meme.sh --run-id run_20260113_072000_a1b2
```

#### Step 3: Animate Meme (using same Run ID)
```bash
./scripts/run_animation.sh --run-id run_20260113_072000_a1b2
```

**Or run Python scripts directly (in src/scripts/):**
```bash
python3 src/scripts/run_text_flow.py
python3 src/scripts/run_meme_flow.py --run-id run_20260113_072000_a1b2
python3 src/scripts/run_animation_flow.py --run-id run_20260113_072000_a1b2
```

---

### Option 3: Use Main CLI (Flexible)

**Note:** Make sure to use `python3` and activate venv first:
```bash
source venv/bin/activate
python3 main.py

# Or run specific flow
python3 main.py --flow text
python3 main.py --flow meme --run-id run_20260113_072000_a1b2
python3 main.py --flow animation --run-id run_20260113_072000_a1b2
```

---

## 🎯 Common Use Cases

### Use Case 1: Generate Only Text Content
```bash
./scripts/run_text.sh --override "platforms=twitter"
```

### Use Case 2: Skip Animation (Faster)
```bash
./scripts/run_all.sh --skip-animation
```

### Use Case 3: Custom Configuration
```bash
./scripts/run_text.sh --override "platforms=twitter,tone=professional"
./scripts/run_meme.sh --run-id <RUN_ID> --override "style=minimal"
```

### Use Case 4: Generate Multiple Memes from Same Content
```bash
# Step 1: Generate content once
./scripts/run_text.sh
# Save this Run ID!

# Step 2: Generate different memes using the same content
./scripts/run_meme.sh --run-id <RUN_ID>
./scripts/run_meme.sh --run-id <RUN_ID> --override "style=bold"
./scripts/run_meme.sh --run-id <RUN_ID> --override "template=stonks"
```

---

## 📁 Understanding Output Structure

After running flows, your output directory looks like this:

```
output/
└── runs/
    └── run_20260113_072000_a1b2/
        ├── run_metadata.json           # Overall run info
        ├── content/                    # Text Flow outputs
        │   ├── platform_content.json
        │   ├── twitter_content.txt
        │   ├── instagram_content.txt
        │   ├── trends.json
        │   └── business_context.json
        ├── memes/                      # Meme Flow outputs
        │   ├── final_meme.png
        │   ├── branded_template.png
        │   └── meme_metadata.json
        ├── video/                      # Animation Flow outputs
        │   ├── animated_meme.mp4
        │   └── animation_metadata.json
        └── metadata/                   # Inter-flow data
            ├── text_output.json
            ├── meme_output.json
            └── animation_output.json
```

---

## 🔧 Configuration Overrides

Override any configuration parameter using the `--override` flag:

### Available Override Keys:

**Content Generation:**
- `platforms` - Comma-separated list: `twitter,instagram,linkedin`
- `tone` - Brand tone: `edgy`, `professional`, `casual`, etc.

**Meme Generation:**
- `style` - Visual style: `bold`, `minimal`, `vibrant`
- `humor_type` - Humor style: `sarcastic`, `witty`, `ironic`
- `template` - Force specific template name

**Animation:**
- `animation_style` - Style: `auto`, `blink`, `bounce`, `shake`, `glow`, `zoom`
- `skip_animation` - Skip animation: `true` or `false`

**Global:**
- `force_refresh_context` - Force reload business context: `true`
- `force_refresh_trends` - Force reload trends: `true`

### Examples:
```bash
# Single override (using shell scripts)
./scripts/run_text.sh --override "platforms=twitter"

# Multiple overrides
./scripts/run_all.sh --override "platforms=twitter,tone=edgy,skip_animation=true"

# Flow-specific override
./scripts/run_meme.sh --run-id <ID> --override "humor_type=sarcastic"

# Or with python3 directly (remember to activate venv first)
source venv/bin/activate
python3 src/scripts/run_text_flow.py --override "platforms=twitter"
```

---

## 🎓 Understanding Flows

### Flow 1: Text Content Generation
**What it does:**
- Loads your business context and brand identity
- Fetches trending topics
- Generates platform-optimized content

**Nodes:**
1. Business Context
2. Trend Intelligence  
3. Content Curation

**Outputs:** Platform-specific text content

---

### Flow 2: Meme Generation
**What it does:**
- Analyzes content sentiment
- Selects appropriate meme template
- Applies brand identity
- Generates meme text
- Renders final meme

**Nodes:**
1. Sentiment Analysis
2. Template Selection
3. Brand Blending
4. Text Generation
5. Meme Rendering

**Inputs:** Can use Flow 1 outputs OR run standalone
**Outputs:** Branded meme image

---

### Flow 3: Animation
**What it does:**
- Animates the generated meme

**Nodes:**
1. Meme Animation

**Inputs:** Requires Flow 2 meme output
**Outputs:** Animated video

---

## ❓ Troubleshooting

### "Run ID does not exist"
- Check the Run ID you're using
- Make sure you ran the previous flow first
- List available runs: `ls output/runs/`

### "No LLM API keys found"
- Set `GOOGLE_API_KEY` or `OPENAI_API_KEY` in `.env`
- Copy `.env.example` to `.env` if needed

### "Directory not found"
- Create required directories:
  ```bash
  mkdir -p business_documents brand_identity rekt_meme_templates
  ```

### Want to see what's happening?
- Check node output in terminal (verbose logging)
- Review metadata files in `output/runs/<RUN_ID>/metadata/`
- Open generated images/videos directly

---

## 🎨 Next Steps

1. **Customize your brand:** Edit `brand_identity/brand_config.json`
2. **Add business context:** Add files to `business_documents/`
3. **Add meme templates:** Add images to `rekt_meme_templates/`
4. **Schedule runs:** Set up cron jobs to run flows automatically
5. **Integrate with frontend:** Use the JSON outputs for web UI

---

**Need help?** Check the full [README.md](README.md) for detailed documentation.
