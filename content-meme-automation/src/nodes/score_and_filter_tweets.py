"""Twitter Engagement Node 2: Rekt CEO tweet relevance scoring via LLM."""
import json
from typing import Dict, Any, List

from ..utils.llm_utils import get_llm
from ..rag import query_brand_context
from langchain_core.prompts import ChatPromptTemplate


# Dynamic SCORING_PROMPT — brand context injected at runtime from RAG
SCORING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "{brand_context}\n\nYou are the Rekt CEO strategist. Your goal is to find the most exploitable, degen-heavy, or emotionally charged crypto tweets to farm engagement off of. Reject boring, generic, or corporate tweets."),
    ("user", """Evaluate the following {count} trending tweets for the Rekt CEO brand's engagement strategy.

Tweets:
{tweets_json}

For each tweet, return a JSON array with objects containing:
- "id": the exact tweet id as given
- "relevancy_score": 0.0–1.0 (Higher if it involves memecoins, getting rekt, liquidations, euphoria, or pure degen behavior. Lower if it's generic news or corporate announcements.)
- "virality_potential": 0.0–1.0 (How likely is a savage, counter-trade, or emotionally raw reply to catch fire here?)
- "reasoning": 1 sentence explaining the angle (e.g. "Perfect setup to roast their 100x leverage liquidation").

Return ONLY a valid JSON array, no markdown fences, no explanation.""")
])


def _score_batch(tweets: List[Dict], llm, brand_context: str) -> List[Dict]:
    """Score a batch of tweets using the LLM with live RAG brand context."""
    tweets_input = [
        {
            "id": t["id"],
            "text": t.get("text", ""),
            "author_followers": t.get("author_followers", 0),
            "likes": t.get("likes", 0),
            "replies": t.get("replies", 0),
        }
        for t in tweets
    ]

    chain = SCORING_PROMPT | llm
    response = chain.invoke({
        "brand_context": brand_context,
        "count": len(tweets_input),
        "tweets_json": json.dumps(tweets_input, indent=2),
    })

    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])

    return json.loads(content)


def score_and_filter_tweets_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Twitter Engagement Node 2: Score tweets for engagement potential.

    Uses the LLM to evaluate:
    - relevancy_score: fit with our audience
    - virality_potential: chance of our reply getting traction
    - composite_score: weighted average (includes author size)

    Populates state["scored_tweets"] with ranked, enriched tweets.
    """
    print("\n🎯 NODE 2: Score & Filter Tweets")
    print("=" * 50)

    scraped: List[Dict] = state.get("scraped_tweets", [])
    dry_run: bool = state.get("config", {}).get("dry_run", False)

    if not scraped:
        print("  ⚠️  No scraped tweets found, skipping scoring")
        state["scored_tweets"] = []
        return state

    if dry_run:
        print("  🧪 DRY RUN MODE — using simplified scoring")
        scored = []
        for t in scraped:
            # Fake semi-random scoring
            relevance = 0.70 + (t.get("likes", 0) % 3) / 10
            virality = 0.65 + (t.get("replies", 0) % 4) / 10
            
            # Author follower count provides a small boost (log scale roughly)
            author_boost = min(t.get("author_followers", 0) / 1000000, 0.2)
            
            composite = round(0.4 * relevance + 0.4 * virality + 0.2 * author_boost, 3)
            scored.append({
                **t,
                "relevancy_score": round(relevance, 2),
                "virality_potential": round(virality, 2),
                "composite_score": composite,
                "scoring_reasoning": "High engagement tweet in the crypto space.",
            })
    else:
        print("  🧠 Retrieving brand context from RAG...")
        brand_context = query_brand_context(
            "Rekt CEO brand identity tone audience crypto degen engagement strategy",
            k=5,
        )

        llm = get_llm("analysis")
        scored = []

        batch_size = 5
        for i in range(0, len(scraped), batch_size):
            batch = scraped[i:i + batch_size]
            print(f"  🤖 Scoring batch {i // batch_size + 1}/{(len(scraped) + batch_size - 1) // batch_size} ({len(batch)} tweets)...")
            try:
                scores = _score_batch(batch, llm, brand_context)
                score_map = {s["id"]: s for s in scores}
                for tweet in batch:
                    s = score_map.get(tweet["id"], {})
                    rel_score = float(s.get("relevancy_score", 0.5))
                    viral_score = float(s.get("virality_potential", 0.5))
                    
                    # Author follower count provides a small boost
                    author_boost = min(tweet.get("author_followers", 0) / 1000000, 0.2)
                    
                    composite = round(0.4 * rel_score + 0.4 * viral_score + 0.2 * author_boost, 3)
                    scored.append({
                        **tweet,
                        "relevancy_score": rel_score,
                        "virality_potential": viral_score,
                        "composite_score": composite,
                        "scoring_reasoning": s.get("reasoning", ""),
                    })
            except Exception as e:
                print(f"  ⚠️  Batch scoring failed: {e} — using defaults")
                for tweet in batch:
                    scored.append({
                        **tweet,
                        "relevancy_score": 0.5,
                        "virality_potential": 0.5,
                        "composite_score": 0.5,
                        "scoring_reasoning": "Scoring failed.",
                    })

    # Sort by composite score descending and keep top 10
    scored.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
    top_scored = scored[:10]

    state["scored_tweets"] = top_scored

    print(f"\n  ✅ Scoring complete — top tweet from @{top_scored[0].get('author_handle', 'unknown')} (score: {top_scored[0].get('composite_score', 0):.2f})")
    return state
