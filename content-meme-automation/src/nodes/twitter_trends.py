"""Trend Research Node 1: Fetch Twitter trending topics via twitterapi.io."""
import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, TypedDict


# ── WOEID map: worldwide + top crypto-heavy countries ──────────────────────
CRYPTO_LOCATIONS: Dict[str, int] = {
    "Worldwide": 1,
    "USA": 23424977,
    "India": 23424848,
    "Nigeria": 23424908,
    "Brazil": 23424768,
    "UAE": 23424971,
    "Singapore": 23424948,
}

CRYPTO_SEARCH_TERMS = (
    "crypto OR bitcoin OR ethereum OR solana OR defi OR nft OR "
    "memecoin OR altcoin OR web3 OR blockchain OR btc OR eth"
)

TWITTER_API_BASE = "https://api.twitterapi.io"


# ── Dry-run fixture ────────────────────────────────────────────────────────
DRY_RUN_TOPICS = [
    {"name": "#Bitcoin", "tweet_volume": 450000, "locations": ["Worldwide", "USA"]},
    {"name": "#Ethereum", "tweet_volume": 180000, "locations": ["Worldwide", "USA"]},
    {"name": "#Solana", "tweet_volume": 95000, "locations": ["Worldwide", "India"]},
    {"name": "#DeFi", "tweet_volume": 60000, "locations": ["Worldwide", "Singapore"]},
    {"name": "#NFT", "tweet_volume": 45000, "locations": ["USA", "UAE"]},
    {"name": "#Memecoin", "tweet_volume": 38000, "locations": ["Worldwide", "Nigeria"]},
    {"name": "#Web3", "tweet_volume": 32000, "locations": ["USA", "India"]},
    {"name": "#Altcoin", "tweet_volume": 28000, "locations": ["Nigeria", "Brazil"]},
    {"name": "#Crypto", "tweet_volume": 250000, "locations": ["Worldwide", "USA"]},
    {"name": "#Blockchain", "tweet_volume": 21000, "locations": ["India", "Singapore"]},
    {"name": "#BTC", "tweet_volume": 310000, "locations": ["Worldwide"]},
    {"name": "#ETH", "tweet_volume": 130000, "locations": ["Worldwide", "UAE"]},
]


def _get_headers() -> Dict[str, str]:
    api_key = os.getenv("TWITTERAPI_IO_KEY", "")
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }


def _fetch_trends_for_woeid(woeid: int, location_name: str, dry_run: bool) -> List[Dict]:
    """Fetch trending topics for a single WOEID."""
    if dry_run:
        # Return a subset of the fixture depending on location
        return [
            {"name": t["name"], "tweet_volume": t["tweet_volume"]}
            for t in DRY_RUN_TOPICS
            if location_name in t["locations"]
        ]

    try:
        resp = requests.get(
            f"{TWITTER_API_BASE}/twitter/trends",
            headers=_get_headers(),
            params={"woeid": woeid, "count": 50},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        # API returns list of trend objects with .name and .tweet_volume
        trends = data if isinstance(data, list) else data.get("trends", [])
        return [
            {
                "name": t.get("name", ""),
                "tweet_volume": t.get("tweet_volume") or 0,
            }
            for t in trends
        ]
    except Exception as e:
        print(f"    ⚠️  Failed to fetch trends for {location_name} (WOEID {woeid}): {e}")
        return []


def _fetch_tweet_volume_7d(topic_name: str, dry_run: bool) -> int:
    """Estimate 7-day tweet volume for a topic via advanced search."""
    if dry_run:
        fixture = next((t for t in DRY_RUN_TOPICS if t["name"] == topic_name), None)
        return (fixture["tweet_volume"] or 0) * 7 if fixture else 0

    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    query = f"{topic_name} since:{seven_days_ago} ({CRYPTO_SEARCH_TERMS}) -filter:replies"
    count = 0
    cursor = ""

    try:
        for _ in range(2):  # Max 2 pages to control cost
            resp = requests.get(
                f"{TWITTER_API_BASE}/twitter/tweet/advanced_search",
                headers=_get_headers(),
                params={"query": query, "queryType": "Latest", "cursor": cursor},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            tweets = data.get("tweets", [])
            count += len(tweets)
            cursor = data.get("next_cursor", "")
            if not cursor or not tweets:
                break
            time.sleep(0.5)  # Rate-limit courtesy sleep
    except Exception as e:
        print(f"    ⚠️  7-day search failed for {topic_name}: {e}")

    return count


def twitter_trends_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trend Research Node 1: Fetch live Twitter trending topics.

    Sources:
    - twitterapi.io /twitter/trends  (per-location WOEID)
    - twitterapi.io /twitter/tweet/advanced_search  (7-day volume estimates)

    Populates state["raw_trends"] with a deduplicated list of enriched topics.
    """
    print("\n📡 NODE 1: Twitter Trends Fetch")
    print("=" * 50)

    dry_run: bool = state.get("config", {}).get("dry_run", False)

    if dry_run:
        print("  🧪 DRY RUN MODE — using fixture data")
    else:
        api_key = os.getenv("TWITTERAPI_IO_KEY", "")
        if not api_key:
            print("  ⚠️  TWITTERAPI_IO_KEY not set — falling back to dry-run fixtures")
            dry_run = True

    # ── Step 1: Fetch trends per location ─────────────────────────────────
    all_trends: Dict[str, Dict] = {}  # name → enriched topic dict

    for location_name, woeid in CRYPTO_LOCATIONS.items():
        print(f"  🌍 Fetching trends: {location_name} (WOEID {woeid})...")
        trends = _fetch_trends_for_woeid(woeid, location_name, dry_run)

        for t in trends:
            name = t["name"].strip()
            if not name:
                continue
            if name not in all_trends:
                all_trends[name] = {
                    "topic": name,
                    "today_volume": t.get("tweet_volume", 0) or 0,
                    "locations": [],
                    "volume_7d": 0,
                }
            # Track which locations this topic is trending in
            if location_name not in all_trends[name]["locations"]:
                all_trends[name]["locations"].append(location_name)
            # Keep max volume seen across locations
            vol = t.get("tweet_volume", 0) or 0
            if vol > all_trends[name]["today_volume"]:
                all_trends[name]["today_volume"] = vol

        if not dry_run:
            time.sleep(0.3)

    print(f"\n  ✓ Found {len(all_trends)} unique trending topics across all locations")

    # ── Step 2: Filter to crypto-relevant topics ───────────────────────────
    crypto_keywords = {
        "bitcoin", "btc", "ethereum", "eth", "solana", "sol", "defi", "nft",
        "crypto", "blockchain", "web3", "altcoin", "memecoin", "token",
        "binance", "coinbase", "doge", "shib", "pepe", "ape", "base",
        "layer2", "l2", "dao", "yield", "airdrop", "rwa", "wagmi", "gm",
        "rug", "pump", "dump", "bull", "bear",
    }
    
    # Apply custom overrides
    config = state.get("config", {})
    custom_keywords = config.get("custom_keywords")
    if custom_keywords:
        crypto_keywords.update(kw.lower() for kw in custom_keywords)
        print(f"  🔧 Injected {len(custom_keywords)} custom keywords from user input")

    filtered = []
    for name, data in all_trends.items():
        lower = name.lower().lstrip("#")
        is_crypto = any(kw in lower for kw in crypto_keywords)
        # Also keep if trending in 2+ locations (broader signal)
        multi_location = len(data["locations"]) >= 2
        if is_crypto or multi_location:
            filtered.append(data)

    # Sort by today_volume desc, take top 'limit' (default 30 for raw fetch)
    limit = config.get("limit", 30)
    filtered.sort(key=lambda x: x["today_volume"], reverse=True)
    filtered = filtered[:limit]

    print(f"  ✓ {len(filtered)} topics after crypto relevance filter")

    # ── Step 3: Enrich with 7-day volume ──────────────────────────────────
    print(f"\n  📊 Fetching 7-day tweet volumes (sample)...")
    sample_limit = min(15, limit)  # Limit API calls to max 15 or config limit
    for i, topic in enumerate(filtered[:sample_limit]):  # Limit API calls
        vol_7d = _fetch_tweet_volume_7d(topic["topic"], dry_run)
        topic["volume_7d"] = vol_7d
        if not dry_run and i < 14:
            time.sleep(0.5)

    # ── Update state ───────────────────────────────────────────────────────
    state["raw_trends"] = filtered
    state["execution_metadata"]["fetched_at"] = datetime.utcnow().isoformat()
    state["execution_metadata"]["locations_queried"] = list(CRYPTO_LOCATIONS.keys())

    print(f"\n  ✅ Twitter trends fetch complete — {len(filtered)} topics ready")
    return state
