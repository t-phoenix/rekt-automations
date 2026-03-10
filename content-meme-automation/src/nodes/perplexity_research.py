"""Trend Research Node 2: Perplexity research — history, momentum, forecast."""
import os
import json
import time
import requests
from typing import Dict, Any, List


PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar"  # Real-time web search model


# ── Dry-run fixture ────────────────────────────────────────────────────────
DRY_RUN_RESEARCH = {
    "#Bitcoin": {
        "history_7d_summary": "Bitcoin surged 12% over the past week driven by ETF inflows and macro tailwinds. Institutional buying pressure has been consistently strong.",
        "momentum": "rising",
        "forecast_7d_probability": 0.92,
        "forecast_reason": "ETF demand remains elevated; next FOMC meeting may further catalyze price action.",
    },
    "#Ethereum": {
        "history_7d_summary": "Ethereum has traded sideways with moderate DeFi activity. The upcoming upgrade has sparked developer interest.",
        "momentum": "stable",
        "forecast_7d_probability": 0.78,
        "forecast_reason": "Pectra upgrade scheduled for next week will dominate conversation.",
    },
    "#Solana": {
        "history_7d_summary": "Solana memecoins drove massive volume spikes. BONK and WIF both saw 2x+ moves in the last 7 days.",
        "momentum": "rising",
        "forecast_7d_probability": 0.85,
        "forecast_reason": "Memecoin season on Solana appears to be in full swing with new launches daily.",
    },
    "#DeFi": {
        "history_7d_summary": "DeFi TVL increased 8% week-over-week. Uniswap v4 and new yield protocols drove engagement.",
        "momentum": "rising",
        "forecast_7d_probability": 0.70,
        "forecast_reason": "New protocol launches and governance votes scheduled this week.",
    },
    "#NFT": {
        "history_7d_summary": "NFT volumes remain suppressed compared to 2021-2022 peaks, but niche gaming NFTs saw uptick.",
        "momentum": "fading",
        "forecast_7d_probability": 0.35,
        "forecast_reason": "Market sentiment is still bearish on PFP NFTs; utility NFTs may buck the trend.",
    },
    "#Memecoin": {
        "history_7d_summary": "Memecoins are the dominant crypto narrative. Multiple 100x stories in the last week drove massive Twitter engagement.",
        "momentum": "rising",
        "forecast_7d_probability": 0.88,
        "forecast_reason": "Memecoin mania shows no signs of slowing; new projects launching daily on pump.fun.",
    },
}


def _call_perplexity(prompt: str, api_key: str) -> str:
    """Make a single Perplexity API call and return the text response."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a crypto market intelligence analyst. "
                    "Provide concise, factual, data-driven analysis. "
                    "Always respond in valid JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
        "temperature": 0.2,
        "search_recency_filter": "week",
    }
    resp = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _research_topic(topic_name: str, api_key: str, dry_run: bool) -> Dict[str, Any]:
    """Research a single topic: history, momentum, forecast."""
    if dry_run:
        # Use fixture if available, otherwise generate a generic one
        if topic_name in DRY_RUN_RESEARCH:
            return DRY_RUN_RESEARCH[topic_name]
        return {
            "history_7d_summary": f"{topic_name} has been moderately active in the past 7 days within crypto circles.",
            "momentum": "stable",
            "forecast_7d_probability": 0.5,
            "forecast_reason": "No major catalyst identified for the next 7 days.",
        }

    clean_name = topic_name.lstrip("#")
    prompt = f"""Research the crypto/Web3 topic "{clean_name}" and return JSON with exactly these fields:

{{
  "history_7d_summary": "2-3 sentence summary of what happened with this topic in the LAST 7 DAYS on crypto Twitter and in the market",
  "momentum": "rising|stable|fading — based on recent engagement trend",
  "forecast_7d_probability": 0.0-1.0 probability this topic will trend on crypto Twitter in the NEXT 7 DAYS,
  "forecast_reason": "1-2 sentence explanation of why this topic will or won't trend next week (upcoming events, scheduled news, etc.)"
}}

Focus specifically on crypto/Web3 relevance. Be data-driven. Return ONLY valid JSON, no markdown."""

    try:
        raw = _call_perplexity(prompt, api_key)
        # Strip markdown fences if present
        if raw.strip().startswith("```"):
            lines = raw.strip().split("\n")
            raw = "\n".join(lines[1:-1])
        return json.loads(raw.strip())
    except Exception as e:
        print(f"    ⚠️  Perplexity research failed for {topic_name}: {e}")
        return {
            "history_7d_summary": "Research unavailable.",
            "momentum": "stable",
            "forecast_7d_probability": 0.5,
            "forecast_reason": "Could not fetch forecast data.",
        }


def perplexity_research_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trend Research Node 2: Research each topic with Perplexity.

    For each topic in state["raw_trends"]:
    - Fetches 7-day history summary
    - Determines momentum (rising/stable/fading)
    - Estimates probability of trending in next 7 days

    Populates state["researched_trends"] with enriched topic dicts.
    """
    print("\n🔬 NODE 2: Perplexity Research")
    print("=" * 50)

    dry_run: bool = state.get("config", {}).get("dry_run", False)
    raw_trends: List[Dict] = state.get("raw_trends", [])

    api_key = os.getenv("PERPLEXITY_API_KEY", "")
    if not api_key and not dry_run:
        print("  ⚠️  PERPLEXITY_API_KEY not set — falling back to dry-run mode")
        dry_run = True

    if dry_run:
        print("  🧪 DRY RUN MODE — using fixture research data")

    researched: List[Dict] = []

    for i, topic in enumerate(raw_trends):
        topic_name = topic["topic"]
        print(f"  📖 [{i+1}/{len(raw_trends)}] Researching: {topic_name}")

        research = _research_topic(topic_name, api_key, dry_run)

        enriched = {
            **topic,
            "history_7d_summary": research.get("history_7d_summary", "N/A"),
            "momentum": research.get("momentum", "stable"),
            "forecast_7d_probability": float(research.get("forecast_7d_probability", 0.5)),
            "forecast_reason": research.get("forecast_reason", "N/A"),
        }
        researched.append(enriched)

        # Rate limiting — Perplexity free tier: ~5 req/min
        if not dry_run and i < len(raw_trends) - 1:
            time.sleep(13)  # ~4.5 req/min to stay safe

    state["researched_trends"] = researched
    print(f"\n  ✅ Perplexity research complete — {len(researched)} topics enriched")
    return state
