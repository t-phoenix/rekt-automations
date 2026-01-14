"""Node 2: Trend Intelligence."""
import os
from pathlib import Path
from typing import List, Dict, Any
import json
from langchain_core.prompts import ChatPromptTemplate

from ..utils import get_llm, load_cached_with_expiry, save_cache_with_timestamp
from ..graph.state import GraphState, TrendIntelligence, TrendingTopic, BusinessContext


CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def fetch_trending_topics_with_llm(business_context: BusinessContext) -> List[TrendingTopic]:
    """
    Use LLM to generate trending topics (fallback when APIs unavailable).
    
    Args:
        business_context: Business context for relevance filtering
        
    Returns:
        List of trending topics
    """
    llm = get_llm("analysis")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Web3 trend intelligence expert with deep knowledge of crypto, blockchain, and memetic culture.

Generate 5 trending topics that are currently relevant in the Web3 space, focusing on these domains:
- **Memecoins:** New launches, viral coins, rug pulls, success stories, community-driven tokens
- **DeFi (Decentralized Finance):** Protocol launches, yield farming trends, liquidity events, TVL milestones, exploits
- **NFTs:** New collections, marketplace updates, creator economy, utility NFTs, gaming NFTs
- **RWA (Real World Assets):** Tokenization of real-world assets, adoption news, regulatory updates
- **Prediction Markets:** Platform updates, major prediction events, accuracy milestones
- **Tokenization:** New asset classes being tokenized, infrastructure developments
- **Blockchain Infrastructure:** Ethereum upgrades (EIPs, hard forks), Base chain updates, Solana developments, L2 solutions

## CHAIN FOCUS
Pay special attention to developments on:
- Ethereum (mainnet upgrades, EIPs, gas optimizations)
- Base (new projects, onboarding, ecosystem growth)
- Solana (network upgrades, DeFi on Solana, meme coins)
- Other notable: Arbitrum, Optimism, Polygon

For each topic provide:
- topic: Short, catchy topic name (e.g., "Ethereum Dencun Upgrade Slashes Gas Fees")
- domain: One of: "memecoins", "defi", "nfts", "rwa", "prediction_markets", "tokenization", "blockchain_infrastructure", "general_web3"
- chains_affected: Array of affected blockchains (e.g., ["ethereum", "base"] or ["solana"] or ["multi-chain"])
- description: 2-3 sentence description of what's happening
- reason: Why this is trending right now (technical, social, or market reasons)
- sentiment: "positive", "neutral", or "negative"
- relevance_score: 0-1 score for how well this fits the brand context
- virality_potential: 0-1 score for how viral/meme-worthy this topic is
- meme_angles: Array of 2-4 specific meme angles this topic enables (e.g., ["before/after comparison", "cost savings reactions", "speed boost celebration"])
- technical_depth: "low" (accessible to all), "medium" (some crypto knowledge needed), or "high" (technical/developer focused)

## BRAND CONSIDERATION
Brand Context: {brand_summary}
Tone: {tone}

Ensure topics align with the brand's tone and audience while being genuinely trending in Web3.

Return a JSON array of 5 trending topics with all fields above."""),
        ("user", """Business Context:
Brand: {brand_summary}
Tone: {tone}
Key Messages: {key_messages}

Generate Web3 trending topics as JSON array:""")
    ])
    
    chain = prompt | llm
    # Extract from nested business context
    brand_identity = business_context.get("brand_identity", {})
    communication_style = business_context.get("communication_style", {})
    strategic_messaging = business_context.get("strategic_messaging", {})
    
    response = chain.invoke({
        "brand_summary": brand_identity.get("core_narrative", "")[:500],  # Truncate for API limits
        "tone": ", ".join(communication_style.get("tone_descriptors", [])),
        "key_messages": ", ".join(strategic_messaging.get("key_messages", []))
    })
    
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    topics_data = json.loads(content)
    
    trending_topics = []
    for topic_data in topics_data:
        topic = TrendingTopic(
            topic=topic_data.get("topic", ""),
            domain=topic_data.get("domain", "general_web3"),
            chains_affected=topic_data.get("chains_affected", ["multi-chain"]),
            description=topic_data.get("description", ""),
            reason=topic_data.get("reason", ""),
            sentiment=topic_data.get("sentiment", "neutral"),
            relevance_score=topic_data.get("relevance_score", 0.5),
            virality_potential=topic_data.get("virality_potential", 0.5),
            meme_angles=topic_data.get("meme_angles", []),
            technical_depth=topic_data.get("technical_depth", "medium"),
            source="llm_generated"
        )
        trending_topics.append(topic)
    
    return trending_topics


def trend_intelligence_node(state: GraphState) -> GraphState:
    """
    Node 2: Detect trending topics relevant to brand.
    
    This node:
    - Fetches trending topics (currently using LLM, can add Twitter/Reddit)
    - Filters by relevance to business context
    - Selects top topic for content generation
    - Implements 1-hour caching
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with trend_intelligence populated
    """
    print("\n🔥 NODE 2: Trend Intelligence")
    print("=" * 50)
    
    force_refresh = state["config"].get("force_refresh_trends", False)
    cache_hours = int(os.getenv("TREND_CACHE_HOURS", "1"))
    
    # Check cache first
    if not force_refresh:
        cache_file = CACHE_DIR / "trending_topics.json"
        cached = load_cached_with_expiry(cache_file, cache_hours)
        
        if cached:
            state["trend_intelligence"] = TrendIntelligence(**cached)
            return state
    
    # Fetch fresh trends
    print("🌐 Fetching trending topics...")
    
    business_context = state.get("business_context", {})
    
    # TODO: Add Twitter scraping, Reddit API, Perplexity API
    # For now, using LLM to generate contextual trends
    trending_topics = fetch_trending_topics_with_llm(business_context)
    
    # Select top topic by relevance
    selected_topic = max(trending_topics, key=lambda t: t.get("relevance_score", 0))
    
    print(f"✓ Found {len(trending_topics)} trending topics")
    print(f"✓ Selected: {selected_topic['topic']}")
    print(f"  Relevance: {selected_topic['relevance_score']:.2f}")
    print(f"  Sentiment: {selected_topic['sentiment']}")
    
    trend_intelligence = TrendIntelligence(
        trending_topics=trending_topics,
        selected_topic=selected_topic
    )
    
    # Save to cache
    cache_file = CACHE_DIR / "trending_topics.json"
    save_cache_with_timestamp(cache_file, trend_intelligence)
    
    state["trend_intelligence"] = trend_intelligence
    return state
