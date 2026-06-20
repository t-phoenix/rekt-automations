# Frontend Integration Guide

Changes required when integrating a web or mobile app with the Meme API, including the new **LLM picker**, **x402 payments**, and **admin proxy** patterns.

---

## Summary of breaking / new changes

| Change | Impact |
|--------|--------|
| `llm` form field | Optional — add model picker UI |
| `llm_model` form field | Required when `llm=openrouter` |
| `GET /api/meme/llms` | New — populate model dropdown dynamically |
| `metadata.llm` in response | New — show which model was used |
| x402 `402` responses | New when `X402_ENABLED=true` — payment flow required |
| `X-Admin-Key` header | Server-side only — use backend proxy, not browser |

Existing fields (`topic`, `template_image`, `is_twitter_post`, `tone`, `humor_type`) are unchanged.

---

## Environment variables (frontend)

```bash
# .env.local (Next.js) or .env (Vite)
NEXT_PUBLIC_MEME_API_URL=https://your-meme-api.onrender.com
# Do NOT put ADMIN_API_KEY or LLM keys here
```

| Variable | Where | Notes |
|----------|-------|-------|
| `NEXT_PUBLIC_MEME_API_URL` | Frontend | Public API base URL |
| `ADMIN_API_KEY` | **Backend only** | Next.js API route / serverless function |
| LLM provider keys | **Backend only** | Never in frontend |

---

## 1. Basic generate call (no payments)

Works when `X402_ENABLED=false` (local dev) or for admin-proxied requests.

### TypeScript helper

```typescript
const API_URL = process.env.NEXT_PUBLIC_MEME_API_URL!;

export type MemeOption = {
  top_text: string;
  bottom_text: string;
  ranking_score: number;
  virality_score: number;
  image_coherence_score: number;
  text_alignment_score: number;
  humor_pattern_used: string;
};

export type GenerateMemeParams = {
  topic: string;
  templateImage: File;
  isTwitterPost?: boolean;
  tone?: string;
  humorType?: string;
  llm?: string;       // preset id from GET /api/meme/llms
  llmModel?: string;  // required when llm === "openrouter"
};

export async function generateMeme(params: GenerateMemeParams) {
  const form = new FormData();
  form.append("topic", params.topic);
  form.append("template_image", params.templateImage);
  if (params.isTwitterPost) form.append("is_twitter_post", "true");
  if (params.tone) form.append("tone", params.tone);
  if (params.humorType) form.append("humor_type", params.humorType);
  if (params.llm) form.append("llm", params.llm);
  if (params.llmModel) form.append("llm_model", params.llmModel);

  const res = await fetch(`${API_URL}/api/meme/generate`, {
    method: "POST",
    body: form,
  });

  if (res.status === 429) {
    throw new Error("Rate limited — try again in 2 minutes");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Request failed (${res.status})`);
  }

  return res.json() as Promise<{
    options: MemeOption[];
    metadata: {
      dominant_emotion?: string;
      meme_format?: string;
      llm?: { preset: string; provider: string; model: string; vision_fallback: boolean };
    };
  }>;
}
```

---

## 2. LLM model picker UI

Fetch available presets on mount — don't hardcode the list (availability depends on server keys).

```typescript
export type LLMPreset = {
  id: string;
  label: string;
  provider: string;
  model: string | null;
  supports_vision: boolean;
  tier: "budget" | "balanced" | "premium";
  description: string;
};

export async function fetchAvailableLLMs(): Promise<{
  presets: LLMPreset[];
  default: string | null;
}> {
  const res = await fetch(`${API_URL}/api/meme/llms`);
  if (!res.ok) throw new Error("Failed to load LLM options");
  return res.json();
}
```

### React example

```tsx
function LLMSelector({
  value,
  onChange,
}: {
  value: string;
  onChange: (id: string) => void;
}) {
  const [presets, setPresets] = useState<LLMPreset[]>([]);
  const [defaultId, setDefaultId] = useState<string>("");

  useEffect(() => {
    fetchAvailableLLMs().then(({ presets, default: d }) => {
      setPresets(presets);
      setDefaultId(d ?? presets[0]?.id ?? "");
      if (!value && d) onChange(d);
    });
  }, []);

  return (
    <select value={value || defaultId} onChange={(e) => onChange(e.target.value)}>
      {presets.map((p) => (
        <option key={p.id} value={p.id}>
          {p.label} — {p.tier}
        </option>
      ))}
    </select>
  );
}
```

### OpenRouter custom model input

When user selects `openrouter`, show a text input for `llm_model`:

```tsx
{selectedLlm === "openrouter" && (
  <input
    placeholder="google/gemini-2.5-flash"
    value={llmModel}
    onChange={(e) => setLlmModel(e.target.value)}
  />
)}
```

---

## 3. x402 payment flow (production)

When the API has `X402_ENABLED=true`, the first `POST /api/meme/generate` returns **402** with payment instructions in the `PAYMENT-REQUIRED` response header.

**Do not implement raw x402 signing in browser JavaScript** unless you are building a wallet-connected dApp. Recommended approaches:

### Option A: Backend proxy with admin key (internal app)

Your Next.js API route holds `ADMIN_API_KEY` and calls the Meme API on behalf of logged-in users. You handle billing separately (subscription, credits, etc.).

```typescript
// app/api/meme/generate/route.ts (Next.js App Router)
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const incoming = await req.formData();
  const outgoing = new FormData();

  for (const [key, value] of incoming.entries()) {
    outgoing.append(key, value);
  }

  const res = await fetch(`${process.env.MEME_API_URL}/api/meme/generate`, {
    method: "POST",
    headers: {
      "X-Admin-Key": process.env.ADMIN_API_KEY!,
    },
    body: outgoing,
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
```

Frontend calls `/api/meme/generate` (your proxy) — no x402 changes needed in the browser.

### Option B: x402 client SDK (wallet / agent apps)

For crypto-native apps where users pay per call:

1. Use [@x402/fetch](https://docs.x402.org) or [agentcash](https://agentcash.dev) on the **client or agent**
2. The SDK handles 402 → sign USDC payment → retry with `PAYMENT-SIGNATURE`

```bash
# Agent / CLI
npx agentcash@latest fetch https://your-api.onrender.com/api/meme/generate \
  -m POST \
  -F "topic=crypto winter" \
  -F "llm=gemini-flash" \
  -F "template_image=@meme.jpg"
```

Browser wallet flow (high level):

```typescript
// Pseudocode — use official x402 client for your framework
import { wrapFetchWithPayment } from "@x402/fetch"; // example

const fetchWithPay = wrapFetchWithPayment(fetch, walletClient);

const res = await fetchWithPay(`${API_URL}/api/meme/generate`, {
  method: "POST",
  body: formData,
});
```

Check [x402 docs](https://docs.x402.org) for the current browser SDK.

### Option C: Disable x402 for dev, enable in prod

- **Dev frontend** → API with `X402_ENABLED=false`
- **Prod frontend** → proxy (Option A) or x402 SDK (Option B)

---

## 4. Handle new response metadata

Display which model ran (useful for debugging and user trust):

```tsx
{result.metadata?.llm && (
  <p className="text-sm text-gray-500">
    Generated with {result.metadata.llm.model}
    {result.metadata.llm.vision_fallback && " (vision via fallback model)"}
  </p>
)}
```

---

## 5. Error handling checklist

| Status | UI action |
|--------|-----------|
| `400` | Show validation message (`detail` field) — e.g. missing `llm_model` for openrouter |
| `402` | Trigger payment flow or redirect to "upgrade / pay" UI |
| `429` | Show countdown — rate limit is 1 request per 2 minutes per IP |
| `500` | Generic error + retry button |

```typescript
if (res.status === 402) {
  // x402: show payment UI or use SDK to retry
  const paymentRequired = res.headers.get("payment-required");
  // decode paymentRequired (base64 JSON) for price/network display
}
```

---

## 6. CORS

Ensure your frontend origin is in the API's `CORS_ORIGINS`:

```bash
# meme-api .env
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

If calling through your own backend proxy, CORS is between browser ↔ your backend only — the proxy server-to-server call to Meme API doesn't need CORS.

---

## 7. Migration checklist

- [ ] Add `NEXT_PUBLIC_MEME_API_URL` to frontend env
- [ ] Replace hardcoded model assumptions — API no longer guarantees Gemini/GPT only
- [ ] Call `GET /api/meme/llms` and add model picker (optional but recommended)
- [ ] Pass `llm` in FormData when user selects a model
- [ ] Add `llm_model` field when `llm === "openrouter"`
- [ ] Decide payment strategy: admin proxy vs x402 wallet SDK
- [ ] If using admin proxy: create backend route with `ADMIN_API_KEY` (never expose to client)
- [ ] Handle `402` and `429` status codes in UI
- [ ] Display `metadata.llm` in results (optional)
- [ ] Update `CORS_ORIGINS` on the API for your frontend domain

---

## Full React flow (admin proxy + LLM picker)

```tsx
"use client";

import { useState, useEffect } from "react";

export function MemeGenerator() {
  const [topic, setTopic] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [llm, setLlm] = useState("");
  const [presets, setPresets] = useState<{ id: string; label: string }[]>([]);
  const [options, setOptions] = useState<MemeOption[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/meme/llms") // your BFF proxies to meme-api /api/meme/llms
      .then((r) => r.json())
      .then(({ presets, default: d }) => {
        setPresets(presets);
        setLlm(d ?? presets[0]?.id);
      });
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!image) return;
    setLoading(true);
    try {
      const form = new FormData();
      form.append("topic", topic);
      form.append("template_image", image);
      form.append("llm", llm);

      const res = await fetch("/api/meme/generate", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail ?? "Generation failed");
      setOptions(data.options);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Topic" />
      <input type="file" accept="image/*" onChange={(e) => setImage(e.target.files?.[0] ?? null)} />
      <select value={llm} onChange={(e) => setLlm(e.target.value)}>
        {presets.map((p) => (
          <option key={p.id} value={p.id}>{p.label}</option>
        ))}
      </select>
      <button type="submit" disabled={loading}>{loading ? "Generating…" : "Generate"}</button>
      {options.map((o, i) => (
        <div key={i}>
          <strong>{o.top_text}</strong> / {o.bottom_text}
        </div>
      ))}
    </form>
  );
}
```

This pattern keeps `ADMIN_API_KEY` on your `/api/meme/generate` route while the React app stays key-free.
