"""KOL Research Node 2: Profile & Content Fetch."""
import os
import time
import requests
from typing import Dict, Any, List

TWITTER_API_BASE = "https://api.twitterapi.io"

def kol_profile_content_fetch_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Fetch profile metrics and last tweets for discovered KOLs.
    """
    print("\n📊 NODE 2: KOL Profile & Content Fetch")
    print("=" * 50)

    config = state.get("config", {})
    dry_run = config.get("dry_run", False)
    kols = state.get("discovered_kols", [])

    api_key = os.getenv("TWITTERAPI_IO_KEY", "")
    if not api_key:
        print("  ⚠️  TWITTERAPI_IO_KEY not set")
        state["kol_data"] = []
        return state

    if dry_run:
        print("  🧪 DRY RUN: Injecting mock KOL data")
        state["kol_data"] = [
            {"handle": "keyboardmonkey3", "followers": 25000, "bio": "Degen trading max", "recent_tweets": [{"id": "1", "text": "Bought the token", "likes": 50}]}
        ]
        return state

    fetched_data = []
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    
    # We process up to 5 handles here to keep API calls low.
    # 5 API calls in this step.
    target_handles = kols[:5]
    print(f"  💸 Processing top {len(target_handles)} KOLs to conserve API credits.")

    for handle in target_handles:
        clean_handle = handle.replace("@", "")
        print(f"  🧑‍💻 Fetching data for {clean_handle}")
        try:
            # Endpoint returns user profile mapped dynamically underneath the recent tweets
            resp = requests.get(
                f"{TWITTER_API_BASE}/twitter/user/last_tweets",
                headers=headers,
                params={"userName": clean_handle},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            # The twitterapi.io /twitter/user/last_tweets endpoint returns tweets nested inside "data", whereas advanced_search returns them at the root.
            tweets = data.get("tweets", []) if "tweets" in data else data.get("data", {}).get("tweets", [])
            
            if tweets:
                # Grab author bio from first tweet
                author = tweets[0].get("author", tweets[0].get("user", {}))
                
                parsed_tweets = []
                for tw in tweets[:5]: # Take last 5 tweets
                    parsed_tweets.append({
                        "id": tw.get("id"),
                        "text": tw.get("text", tw.get("full_text", "")),
                        "likes": tw.get("likeCount", 0),
                        "url": f"https://twitter.com/{clean_handle}/status/{tw.get('id')}"
                    })
                
                fetched_data.append({
                    "handle": clean_handle,
                    "followers": author.get("followers", author.get("followers_count", 0)),
                    "bio": author.get("description", "No bio available"),
                    "recent_tweets": parsed_tweets
                })
            else:
                print(f"    ⚠️  No tweets found for {clean_handle} (User might not exist or is inactive)")

        except Exception as e:
            print(f"    ⚠️  Fetch failed for {clean_handle}: {e}")
            
        time.sleep(0.5)  # Let's rate limit between searches

    state["kol_data"] = fetched_data
    print(f"  ✅ Compiled data for {len(fetched_data)} KOLs")
    return state
