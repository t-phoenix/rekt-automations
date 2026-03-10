"""KOL Research Node 1: KOL Discovery."""
import os
import requests
from typing import Dict, Any, List

TWITTER_API_BASE = "https://api.twitterapi.io"

def kol_discovery_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Discover target KOLs matching the niches via twitterapi.io Advanced Search.
    """
    print("\n🔍 NODE 1: KOL Discovery")
    print("=" * 50)

    config = state.get("config", {})
    dry_run = config.get("dry_run", False)
    
    # We will search for high-engagement tweets in these topics
    target_topics = config.get("target_topics", ["memecoin", "crypto", "pumpfun", "solana", "trader"])
    if "target_niche" in config and config["target_niche"]:
        # Map single target_niche to target_topics
        target_topics = [config["target_niche"]]
        
    follower_range = config.get("follower_range", [5000, 150000])
    if "min_followers" in config and config["min_followers"] is not None:
        follower_range[0] = config["min_followers"]
    if "max_followers" in config and config["max_followers"] is not None:
        follower_range[1] = config["max_followers"]

    if dry_run:
        print("  🧪 DRY RUN: Injecting mock KOL handles")
        state["discovered_kols"] = ["@blknoiz06", "@keyboardmonkey3", "@Cryptocred", "@Pentosh1"]
        return state

    api_key = os.getenv("TWITTERAPI_IO_KEY", "")
    if not api_key:
        print("  ⚠️  TWITTERAPI_IO_KEY not set, using default handles")
        state["discovered_kols"] = ["@thecryptodog", "@cobie", "@blknoiz06", "@HsakaTrades"]
        return state

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    discovered = set()
    
    # Construct a broad query matching topics and minimum engagement to ensure it's a KOL
    # Example: (memecoin OR crypto OR pumpfun OR solana) min_faves:50 -filter:replies
    topics_query = " OR ".join(target_topics)
    query = f"({topics_query}) min_faves:50 -filter:replies"
    
    print(f"  📡 Searching Twitter API: {query}")
    
    try:
        # Make a SINGLE API Call here to get the 20 most recent viral tweets matching our query
        resp = requests.get(
            f"{TWITTER_API_BASE}/twitter/tweet/advanced_search",
            headers=headers,
            params={"query": query, "queryType": "Latest"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        tweets = data.get("tweets", [])
        
        for tw in tweets:
            author = tw.get("author", tw.get("user", {}))
            handle = author.get("userName")
            followers = author.get("followers", 0)
            
            # Filter handles by follower range (finding our core "up-and-coming" target audience, not celebs)
            if handle and follower_range[0] <= followers <= follower_range[1]:
                discovered.add(f"@{handle}")
                
            if len(discovered) >= 10:  # Cap at 10 to save API costs downstream
                break

    except Exception as e:
        print(f"    ⚠️  Twitter API search failed: {e}")

    final_kols = list(discovered)
    if not final_kols:
        print("  ⚠️ No matching KOLs found in API, using fallbacks")
        final_kols = ["@keyboardmonkey3", "@DegenSpartan", "@Ansem"]
        
    print(f"  ✅ Discovered {len(final_kols)} KOL handles: {final_kols[:5]}...")
    state["discovered_kols"] = final_kols
    return state
