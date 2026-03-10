"""Competition Research Node 2: Fetch Competitor Posts."""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List

TWITTER_API_BASE = "https://api.twitterapi.io"

def _get_headers() -> Dict[str, str]:
    api_key = os.getenv("TWITTERAPI_IO_KEY", "")
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

def fetch_competitor_posts_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Fetch recent tweets or retweets for discovered competitors over dynamic lookback_hours.
    """
    print("\n📡 NODE 2: Fetch Competitor Posts")
    print("=" * 50)

    config = state.get("config", {})
    lookback_hours = config.get("lookback_hours", 1)  # Default 1 hr
    dry_run = config.get("dry_run", False)
    competitors = state.get("discovered_competitors", [])

    api_key = os.getenv("TWITTERAPI_IO_KEY", "")
    if not api_key:
        print("  ⚠️  TWITTERAPI_IO_KEY not set")
        state["raw_twitter_data"] = []
        return state

    if dry_run:
        print("  🧪 DRY RUN: Injecting mock posts")
        state["raw_twitter_data"] = [
            {"id": "1", "author_handle": "keyboardmonkey3", "text": "Pump.fun is insane right now", "likes": 500, "followers": 6000, "verified": True},
            {"id": "2", "author_handle": "blknoiz06", "text": "I just bought the dip", "likes": 1200, "followers": 55000, "verified": True}
        ]
        return state

    time_limit = (datetime.utcnow() - timedelta(hours=lookback_hours)).strftime("%Y-%m-%d")
    
    fetched_tweets = []
    
    # We chunk handles to avoid query string too long
    chunk_size = 5
    for i in range(0, len(competitors), chunk_size):
        chunk = competitors[i:i+chunk_size]
        from_queries = " OR ".join([f"from:{handle.replace('@', '')}" for handle in chunk])
        query = f"({from_queries}) since:{time_limit} -filter:replies"
        
        print(f"  🌍 Fetching tweets for {chunk} since {time_limit}")
        try:
            resp = requests.get(
                f"{TWITTER_API_BASE}/twitter/tweet/advanced_search",
                headers=_get_headers(),
                params={"query": query, "queryType": "Latest", "cursor": ""},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            raw_tweets = data.get("tweets", [])
            
            for tw in raw_tweets:
                author = tw.get("author", {}) or tw.get("user", {})
                metrics = tw.get("public_metrics", {}) or tw.get("metrics", {})
                tweet_data = {
                    "id": tw.get("id", ""),
                    "text": tw.get("text", tw.get("full_text", "")),
                    "author_handle": author.get("userName", author.get("username", "")),
                    "author_name": author.get("name", ""),
                    "author_verified": author.get("isBlueVerified", author.get("isVerified", False)),
                    "author_followers": author.get("followers", author.get("public_metrics", {}).get("followers_count", 0)),
                    "likes": metrics.get("likes", tw.get("likeCount", 0)),
                    "retweets": metrics.get("retweets", tw.get("retweetCount", 0)),
                    "replies": metrics.get("replies", tw.get("replyCount", 0)),
                    "views": metrics.get("views", tw.get("viewCount", 0)),
                    "created_at": tw.get("createdAt", tw.get("created_at", datetime.utcnow().isoformat()))
                }
                tweet_data["url"] = f"https://twitter.com/{tweet_data['author_handle']}/status/{tweet_data['id']}"
                fetched_tweets.append(tweet_data)

        except Exception as e:
            print(f"    ⚠️  Tweet fetch failed for chunk: {e}")

    state["raw_twitter_data"] = fetched_tweets
    print(f"  ✅ Fetched {len(fetched_tweets)} raw tweets")
    return state
