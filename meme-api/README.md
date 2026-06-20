# Meme Generation API

FastAPI service that generates viral meme text from a topic + template image. Supports **on-demand LLM selection**, **x402 USDC pay-per-call**, and **admin bypass** for internal use.

## Features

- **4-node AI pipeline**: sentiment analysis → image analysis → 10 text options → top 3 ranked
- **Multi-LLM**: users pick model per request (`gemini-flash`, `groq-llama-70b`, `deepseek`, `openrouter`, etc.)
- **x402 payments**: optional USDC micropayments per call (Base / Solana)
- **Admin bypass**: free access via server-side API key
- **Rate limiting**: 1 generate request per 2 minutes per IP

## Documentation

| Doc | Description |
|-----|-------------|
| [API_KEYS.md](./API_KEYS.md) | Step-by-step guide to obtain every API key and wallet address |
| [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) | Required frontend changes (LLM picker, x402, admin proxy) |
| [API.md](./API.md) | Detailed API reference |
| `/docs` | Interactive Swagger UI (when server is running) |

## Quick Start

### 1. Install

```bash
cd meme-api
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

At minimum, set one LLM provider key (see [API_KEYS.md](./API_KEYS.md)):

```bash
GOOGLE_API_KEY=your_key          # recommended — enables gemini-flash
DEFAULT_LLM=gemini-flash
```

For local dev, leave payments off:

```bash
X402_ENABLED=false
```

### 3. Run

```bash
python app.py
# or
uvicorn app:app --reload --port 8001
```

Open http://localhost:8001/docs

### 4. Test

```bash
# List available LLM presets
curl http://localhost:8001/api/meme/llms

# Generate meme text
curl -X POST http://localhost:8001/api/meme/generate \
  -F "topic=When you finally understand DeFi" \
  -F "llm=gemini-flash" \
  -F "template_image=@path/to/template.jpg"
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | API info (+ payment metadata when x402 enabled) |
| `GET` | `/health` | Simple health check |
| `GET` | `/api/meme/health` | Service health + LLM availability |
| `GET` | `/api/meme/llms` | List LLM presets available on this server |
| `POST` | `/api/meme/generate` | Generate top 3 meme text options |

### `POST /api/meme/generate`

**Content-Type:** `multipart/form-data`

| Field | Required | Description |
|-------|----------|-------------|
| `topic` | Yes | Topic text or full Twitter post |
| `template_image` | Yes | Meme template (JPEG, PNG, WebP, max 10MB) |
| `is_twitter_post` | No | `true` if `topic` is a full tweet (default: `false`) |
| `tone` | No | `edgy`, `professional`, `casual` |
| `humor_type` | No | `sarcastic`, `witty`, `ironic` |
| `llm` | No | Preset id — see `GET /api/meme/llms` (default: server `DEFAULT_LLM`) |
| `llm_model` | No | Required when `llm=openrouter` (e.g. `google/gemini-2.5-flash`) |

**Response (200):**

```json
{
  "options": [
    {
      "top_text": "WHEN YOU FINALLY",
      "bottom_text": "UNDERSTAND DEFI",
      "ranking_score": 0.89,
      "virality_score": 0.85,
      "image_coherence_score": 0.92,
      "text_alignment_score": 0.87,
      "humor_pattern_used": "triumphant_flex"
    }
  ],
  "metadata": {
    "dominant_emotion": "confidence",
    "humor_type": "witty",
    "meme_format": "top_bottom_classic",
    "total_options_considered": 10,
    "weighting": "60% text input, 40% image coherence",
    "llm": {
      "preset": "gemini-flash",
      "provider": "google",
      "model": "gemini-2.5-flash",
      "vision_fallback": false
    }
  }
}
```

**Other status codes:**

| Code | Meaning |
|------|---------|
| `402` | Payment required (x402 enabled, no valid `PAYMENT-SIGNATURE`) |
| `429` | Rate limit exceeded (1 req / 2 min per IP) |
| `400` | Validation error (missing topic, bad LLM preset, etc.) |

## LLM Presets

Configure provider keys on the server; clients choose per request via the `llm` field.

| Preset | Provider | Best for | Vision |
|--------|----------|----------|--------|
| `gemini-flash` | Google | **Recommended default** — cheap, fast, vision | Yes |
| `gemini-flash-lite` | Google | Highest volume / lowest cost | Yes |
| `groq-llama-70b` | Groq | Fast creative text | Fallback* |
| `groq-llama-8b` | Groq | Fastest / cheapest text | Fallback* |
| `deepseek` | DeepSeek | Strong meme copy | Fallback* |
| `gpt-4o-mini` | OpenAI | Reliable fallback | Yes |
| `gpt-4o` | OpenAI | Highest quality | Yes |
| `openrouter` | OpenRouter | Any model via `llm_model` | Depends |

\*Text-only presets use `DEFAULT_VISION_LLM` (e.g. `gemini-flash`) for the image analysis step.

## x402 Payments

When `X402_ENABLED=true`, `POST /api/meme/generate` requires a USDC payment per call.

1. Client sends request → server responds **402** with `PAYMENT-REQUIRED` header
2. Client signs payment and retries with `PAYMENT-SIGNATURE` header
3. Server verifies via facilitator, runs generation, settles on success

**Admin bypass** (server-side only — never expose in browser):

```
X-Admin-Key: <ADMIN_API_KEY>
# or
Authorization: Bearer <ADMIN_API_KEY>
```

See [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) for client-side payment flows.

### Production x402 env vars

```bash
X402_ENABLED=true
X402_PRICE=$0.05
X402_EVM_PAY_TO=0xYourWallet
X402_EVM_NETWORK=eip155:8453              # Base mainnet
X402_FACILITATOR_URL=https://facilitator.payai.network
ADMIN_API_KEY=<long-random-secret>
```

Testnet: `eip155:84532` + `https://x402.org/facilitator`

## Configuration

All settings via environment variables — see `.env.example`.

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY`, `GROQ_API_KEY`, etc. | LLM provider keys ([guide](./API_KEYS.md)) |
| `DEFAULT_LLM` | Default preset when client omits `llm` |
| `DEFAULT_VISION_LLM` | Vision fallback for text-only presets |
| `CORS_ORIGINS` | Comma-separated frontend URLs |
| `X402_*` | Payment settings |
| `ADMIN_API_KEY` | Admin bypass secret |

## Deployment

### Render.com

Use the included `render.yaml` or:

- **Build:** `pip install -r requirements.txt`
- **Start:** `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Health check:** `/health`

Set secrets in the Render dashboard: LLM keys, `ADMIN_API_KEY`, `X402_EVM_PAY_TO`.

### Docker

```bash
docker build -t meme-api .
docker run -p 8001:8001 --env-file .env meme-api
```

## Architecture

```
POST /api/meme/generate
        │
        ▼
  [x402 middleware] ──402──► client pays & retries
        │ (or admin bypass)
        ▼
  Node 1: Sentiment Analysis     (user's llm preset)
  Node 2: Template Image Analysis (vision model)
  Node 3: Text Generation        (10 options)
  Node 4: Text Selection         (top 3, 60/40 ranking)
```

## License

MIT
