"""Competition Research Node 3: Filter & Rank Competitor Posts."""
from typing import Dict, Any, List

def filter_and_rank_competitor_posts_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Filter verified accounts > 5000 followers and calculate dynamic engagement thresholds.
    """
    print("\n⚙️ NODE 3: Filter & Rank Competitor Posts")
    print("=" * 50)

    raw_tweets = state.get("raw_twitter_data", [])
    config = state.get("config", {})
    lookback_hours = config.get("lookback_hours", 1)

    # Calculate dynamic threshold based on timeframe
    # E.g., 1hr needs 50 likes, 12 hr needs 500 likes, 24 hr needs 1000 likes.
    base_like_threshold = max(config.get("engagement_threshold", 50), 50)
    dynamic_threshold = int(base_like_threshold * (lookback_hours / 1.0))

    print(f"  🎯 Dynamic Like Threshold for {lookback_hours}h window: {dynamic_threshold}")

    filtered = []
    for tw in raw_tweets:
        followers = tw.get("author_followers", 0)
        verified = tw.get("author_verified", False)
        likes = tw.get("likes", 0)

        # Filter: > 5000 followers & Verified & meets threshold
        # if followers >= 5000 and verified and likes >= dynamic_threshold:
        # NOTE: We can relax 'verified' requirement for crypto since many anon founders exist
        if followers >= 5000 and likes >= dynamic_threshold:
            filtered.append(tw)

    # Sort descending by likes
    filtered.sort(key=lambda x: x.get("likes", 0), reverse=True)
    top_metrics = filtered[:20]  # Take top 20 for analysis

    state["filtered_metrics"] = top_metrics
    print(f"  ✅ Retained {len(top_metrics)} high-performing posts")
    return state
