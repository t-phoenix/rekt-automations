# API Keys Setup Guide

Step-by-step instructions for every credential the Meme API uses. Keys live **only on the server** (`.env` or Render secrets) — never commit them or expose them in frontend code.

---

## Overview

| Key / setting | Required? | Used for |
|---------------|-----------|----------|
| `GOOGLE_API_KEY` | Recommended | Gemini Flash (default LLM + vision) |
| `GROQ_API_KEY` | Optional | Groq Llama presets |
| `DEEPSEEK_API_KEY` | Optional | DeepSeek Chat preset |
| `OPENAI_API_KEY` | Optional | GPT-4o / GPT-4o Mini presets |
| `OPENROUTER_API_KEY` | Optional | Any model via `llm=openrouter` |
| `X402_EVM_PAY_TO` | Production | Wallet that receives USDC payments |
| `ADMIN_API_KEY` | Recommended | Free admin access (server-side only) |

You need **at least one LLM provider key**. For the best cost/quality balance, start with Google Gemini.

---

## 1. Google Gemini (recommended)

**Enables:** `gemini-flash`, `gemini-flash-lite`  
**Env var:** `GOOGLE_API_KEY`

### Steps

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **Create API key**
4. Choose an existing Google Cloud project or create a new one
5. Copy the key — it starts with `AIza...`
6. Add to `.env`:

   ```bash
   GOOGLE_API_KEY=AIzaSy...
   DEFAULT_LLM=gemini-flash
   DEFAULT_VISION_LLM=gemini-flash
   ```

### Notes

- Gemini 2.5 Flash is the recommended default: low cost, fast, supports vision for template image analysis
- Free tier available with rate limits; check [Google AI pricing](https://ai.google.dev/pricing)
- Enable billing in Google Cloud if you exceed free tier limits

---

## 2. Groq

**Enables:** `groq-llama-70b`, `groq-llama-8b`  
**Env var:** `GROQ_API_KEY`

### Steps

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up / sign in
3. Open **API Keys** in the left sidebar
4. Click **Create API Key**, name it (e.g. `meme-api`), copy the key
5. Add to `.env`:

   ```bash
   GROQ_API_KEY=gsk_...
   ```

### Notes

- Groq presets are text-only; image analysis falls back to `DEFAULT_VISION_LLM`
- Generous free tier with high rate limits on Llama models
- Best for speed and cost on text generation steps

---

## 3. DeepSeek

**Enables:** `deepseek` preset  
**Env var:** `DEEPSEEK_API_KEY`

### Steps

1. Go to [platform.deepseek.com](https://platform.deepseek.com)
2. Create an account and verify email
3. Open **API Keys** → **Create new API key**
4. Copy the key
5. Add to `.env`:

   ```bash
   DEEPSEEK_API_KEY=sk-...
   ```

### Notes

- Strong creative writing at very low cost
- Text-only — vision step uses `DEFAULT_VISION_LLM`
- Top up credits in the DeepSeek dashboard as needed

---

## 4. OpenAI

**Enables:** `gpt-4o-mini`, `gpt-4o`  
**Env var:** `OPENAI_API_KEY`

### Steps

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up / sign in
3. Navigate to **API keys** → **Create new secret key**
4. Copy the key (starts with `sk-`)
5. Add billing under **Settings → Billing** (required for API usage)
6. Add to `.env`:

   ```bash
   OPENAI_API_KEY=sk-...
   ```

### Notes

- Reliable fallback with vision support
- Higher cost than Gemini/Groq/DeepSeek for similar tasks
- Set usage limits in the OpenAI dashboard to avoid surprises

---

## 5. OpenRouter (optional — any model)

**Enables:** `llm=openrouter` + client-supplied `llm_model`  
**Env var:** `OPENROUTER_API_KEY`

### Steps

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign in (GitHub or Google)
3. Open **Keys** → **Create Key**
4. Copy the key (starts with `sk-or-`)
5. Add credits under **Credits**
6. Add to `.env`:

   ```bash
   OPENROUTER_API_KEY=sk-or-...
   ```

### Example client usage

```bash
curl -X POST .../api/meme/generate \
  -F "llm=openrouter" \
  -F "llm_model=google/gemini-2.5-flash" \
  -F "topic=..." \
  -F "template_image=@meme.jpg"
```

Browse models at [openrouter.ai/models](https://openrouter.ai/models).

---

## 6. x402 wallet (production payments)

**Enables:** USDC pay-per-call when `X402_ENABLED=true`  
**Env vars:** `X402_EVM_PAY_TO`, `X402_EVM_NETWORK`, `X402_FACILITATOR_URL`

### Steps

1. **Create a wallet** to receive payments:
   - EVM (Base): MetaMask, Coinbase Wallet, or any EVM wallet
   - Copy your **0x...** address

2. **Testnet first** (recommended):

   ```bash
   X402_ENABLED=true
   X402_EVM_PAY_TO=0xYourWalletAddress
   X402_EVM_NETWORK=eip155:84532          # Base Sepolia
   X402_FACILITATOR_URL=https://x402.org/facilitator
   X402_PRICE=$0.05
   ```

   Get testnet USDC on Base Sepolia via [Circle Faucet](https://faucet.circle.com/) to test payments.

3. **Mainnet** (real USDC):

   ```bash
   X402_EVM_NETWORK=eip155:8453           # Base mainnet
   X402_FACILITATOR_URL=https://facilitator.payai.network
   ```

4. **Optional — Solana USDC:**

   ```bash
   X402_SVM_PAY_TO=YourSolanaBase58Address
   X402_SVM_NETWORK=solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp
   ```

### Notes

- Do **not** use `x402.org/facilitator` on mainnet — testnet only
- Set `X402_PRICE` to cover LLM cost + margin (e.g. `$0.05`–`$0.25`)
- Payments settle only on successful (2xx) responses

---

## 7. Admin API key (internal free access)

**Enables:** bypass x402 for trusted server-side callers  
**Env var:** `ADMIN_API_KEY`

### Steps

1. Generate a long random secret:

   ```bash
   openssl rand -hex 32
   ```

2. Add to `.env` / Render secrets:

   ```bash
   ADMIN_API_KEY=a1b2c3d4e5f6...
   ```

3. Use **only from your backend** (never in browser JavaScript):

   ```bash
   curl -X POST .../api/meme/generate \
     -H "X-Admin-Key: a1b2c3d4e5f6..." \
     -F "topic=..." \
     -F "template_image=@meme.jpg"
   ```

### Notes

- Rotate periodically; treat like a password
- Use for internal tools, cron jobs, or a Next.js API route that proxies requests
- Do not embed in frontend env vars prefixed with `NEXT_PUBLIC_` or `VITE_`

---

## Verify your setup

```bash
# Start the server
python app.py

# Check LLM availability
curl http://localhost:8001/api/meme/health
# → { "llm_available": true, "default_llm": "gemini-flash", ... }

# List presets enabled by your keys
curl http://localhost:8001/api/meme/llms
# → { "presets": [...], "default": "gemini-flash" }
```

If `llm_available` is `false`, no LLM provider key was detected — double-check `.env` and restart the server.

---

## Render deployment checklist

In the Render dashboard → **Environment**:

| Variable | Sync from `.env` |
|----------|------------------|
| `GOOGLE_API_KEY` | Secret |
| `GROQ_API_KEY` | Secret (optional) |
| `DEFAULT_LLM` | `gemini-flash` |
| `X402_ENABLED` | `true` (production) |
| `X402_EVM_PAY_TO` | Secret |
| `X402_EVM_NETWORK` | `eip155:8453` |
| `X402_FACILITATOR_URL` | `https://facilitator.payai.network` |
| `X402_PRICE` | `$0.05` |
| `ADMIN_API_KEY` | Secret |
| `CORS_ORIGINS` | Your frontend URL |
