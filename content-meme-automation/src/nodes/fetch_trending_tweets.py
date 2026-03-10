"""Twitter Engagement Node 1: Fetch trending tweets via twitterapi.io."""
import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List

TWITTER_API_BASE = "https://api.twitterapi.io"

CRYPTO_SEARCH_TERMS = (
    "memecoin OR memecoins OR shitcoin OR 100x OR gem OR moon OR "
    "rekt OR liquidations OR rugged OR rugpull OR pump OR ape OR degen"
)

def _get_headers() -> Dict[str, str]:
    api_key = os.getenv("TWITTERAPI_IO_KEY", "")
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }


def fetch_trending_tweets_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Twitter Engagement Node 1: Fetch live trending tweets.

    Sources:
    - twitterapi.io /twitter/tweet/advanced_search 

    Populates state["scraped_tweets"] with a list of trending tweets with engagement metrics.
    """
    print("\n📡 NODE 1: Fetch Trending Tweets")
    print("=" * 50)

    api_key = os.getenv("TWITTERAPI_IO_KEY", "")
    if not api_key:
        print("  ⚠️  TWITTERAPI_IO_KEY not set")
        state["scraped_tweets"] = []
        return state

    print("  🌍 Fetching top recent crypto tweets...")
    
    # Search for tweets in the last 24 hours with high engagement
    one_day_ago = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Check overrides
    config = state.get("config", {})
    target_accounts = config.get("target_accounts")
    if target_accounts:
        from_queries = " OR ".join([f"from:{acc.replace('@', '')}" for acc in target_accounts])
        query = f"({from_queries}) since:{one_day_ago} -filter:replies"
        print(f"  🔧 Injected {len(target_accounts)} target accounts for reply engagement")
    else:
        query = f"({CRYPTO_SEARCH_TERMS}) since:{one_day_ago} min_faves:500 -filter:replies"
    
    fetched_tweets = []
    
    try:
        resp = requests.get(
            f"{TWITTER_API_BASE}/twitter/tweet/advanced_search",
            headers=_get_headers(),
            params={"query": query, "queryType": "Top", "cursor": ""},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        raw_tweets = data.get("tweets", [])
        
        # Parse the response into our required format
        for tw in raw_tweets:
            # Depending on twitterapi.io's exact response structure, you might need to adjust these accessors
            # Here assuming a standard expanded tweet object
            author = tw.get("author", {}) or tw.get("user", {})
            metrics = tw.get("public_metrics", {}) or tw.get("metrics", {})
            
            tweet_data = {
                "id": tw.get("id", ""),
                "text": tw.get("text", tw.get("full_text", "")),
                "author_handle": author.get("userName", author.get("username", author.get("screen_name", ""))),
                "author_name": author.get("name", ""),
                "author_verified": author.get("isBlueVerified", author.get("isVerified", author.get("verified", False))),
                "author_followers": author.get("followers", author.get("public_metrics", {}).get("followers_count", author.get("followers_count", 0))),
                "likes": metrics.get("likes", metrics.get("favorite_count", tw.get("likeCount", tw.get("favorite_count", 0)))),
                "retweets": metrics.get("retweets", metrics.get("retweet_count", tw.get("retweetCount", tw.get("retweet_count", 0)))),
                "replies": metrics.get("replies", metrics.get("reply_count", tw.get("replyCount", tw.get("reply_count", 0)))),
                "views": metrics.get("views", metrics.get("view_count", tw.get("viewCount", tw.get("view_count", 0)))),
                "created_at": tw.get("createdAt", tw.get("created_at", datetime.utcnow().isoformat()))
            }
            
            # Construct URL
            tweet_data["url"] = f"https://twitter.com/{tweet_data['author_handle']}/status/{tweet_data['id']}"
            
            fetched_tweets.append(tweet_data)

    except Exception as e:
        print(f"    ⚠️  Tweet search failed: {e}")
        fetched_tweets = []

    # Take top 20 by engagement (likes for simplicity)
    fetched_tweets.sort(key=lambda x: x.get("likes", 0) or x.get("views", 0), reverse=True)
    top_tweets = fetched_tweets[:20]

    state["scraped_tweets"] = top_tweets
    state["execution_metadata"]["tweets_fetched_at"] = datetime.utcnow().isoformat()

    print(f"\n  ✅ Fetched {len(top_tweets)} top trending tweets")
    return state
