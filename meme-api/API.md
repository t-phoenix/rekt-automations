# Meme Generation API Reference

Accurate API reference for the currently implemented routes.

See also: [README.md](./README.md), [API_KEYS.md](./API_KEYS.md), and [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md).

## Base URL

- Local: `http://localhost:8001`
- Production: your deployed host (for example Render URL)

## Authentication and Payments

When `X402_ENABLED=true`, `POST /api/meme/generate` is protected by x402 and can return `402 Payment Required` until the client retries with a valid `PAYMENT-SIGNATURE` header.

Admin bypass is supported for protected routes:

- `X-Admin-Key: <ADMIN_API_KEY>`
- `Authorization: Bearer <ADMIN_API_KEY>`

When `X402_ENABLED=false` (local default), no payment/admin header is required.

## Endpoints

### `GET /`

Returns API metadata:

- `message`
- `version`
- `docs`
- `health`
- optional `payment` object when x402 is enabled

### `GET /health`

Simple root health check.

Example response:

```json
{
  "status": "ok"
}
```

### `GET /api/meme/health`

Service health with LLM status.

Example response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "llm_available": true,
  "default_llm": "gemini-flash"
}
```

### `GET /api/meme/llms`

Lists available server-side LLM presets and default preset.

Example response:

```json
{
  "presets": [
    {
      "id": "gemini-flash",
      "label": "Gemini Flash",
      "provider": "google",
      "model": "gemini-2.5-flash",
      "supports_vision": true,
      "tier": "default",
      "description": "Fast, low-cost multimodal model"
    }
  ],
  "default": "gemini-flash"
}
```

### `POST /api/meme/generate`

Generate top 3 meme text options from user text and an uploaded template image.

Content type: `multipart/form-data`

Request fields:

- `topic` (required): topic text or full post text
- `template_image` (required): image file (`image/jpeg`, `image/png`, `image/webp`, max configured size)
- `is_twitter_post` (optional, default `false`)
- `tone` (optional)
- `humor_type` (optional)
- `llm` (optional preset id)
- `llm_model` (optional model override; generally used with `llm=openrouter`)

Example curl:

```bash
curl -X POST http://localhost:8001/api/meme/generate \
  -F "topic=When you finally understand DeFi" \
  -F "llm=gemini-flash" \
  -F "template_image=@./stonks.jpg"
```

Example success response:

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

## Error Behavior

Common status codes:

- `400`: invalid request (missing `topic`, unsupported file type, oversized file, invalid LLM selection)
- `402`: payment required when x402 is enabled and request is unpaid
- `429`: rate limit exceeded (`1/2minutes` per IP on generate route)
- `500`: internal server error during generation

Note: there is no `/api/meme/templates` endpoint in the current implementation.
