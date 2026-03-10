"""Trend Research Node 3: Rekt CEO brand relevance scoring via LLM."""
import json
from typing import Dict, Any, List

from ..utils.llm_utils import get_llm
from ..rag import query_brand_context
from langchain_core.prompts import ChatPromptTemplate


# Dynamic SCORING_PROMPT — brand context injected at runtime from RAG
SCORING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "{brand_context}\n\nScore topics for Rekt CEO brand relevance as described above."),
    ("user", """Score the following {count} crypto Twitter trending topic(s) for Rekt CEO brand.

Topics:
{topics_json}

For each topic, return a JSON array with objects containing:
- "topic": exact topic name as given
- "brand_relevance": 0.0–1.0
- "meme_potential": 0.0–1.0
- "meme_angles": array of 2–3 specific meme angles Rekt CEO could use
- "one_liner": a sample Rekt CEO tweet/caption for this topic (edgy, punchy, max 280 chars)

Return ONLY a valid JSON array, no markdown fences, no explanation.""")
])


def _score_batch(topics: List[Dict], llm, brand_context: str) -> List[Dict]:
    """Score a batch of topics using the LLM with live RAG brand context."""
    topics_input = [
        {
            "topic": t["topic"],
            "momentum": t.get("momentum", "stable"),
            "today_volume": t.get("today_volume", 0),
            "locations": t.get("locations", []),
            "forecast_7d_probability": t.get("forecast_7d_probability", 0.5),
        }
        for t in topics
    ]

    chain = SCORING_PROMPT | llm
    response = chain.invoke({
        "brand_context": brand_context,
        "count": len(topics_input),
        "topics_json": json.dumps(topics_input, indent=2),
    })

    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])

    return json.loads(content)


def rekt_relevance_scoring_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trend Research Node 3: Score topics for Rekt CEO brand relevance.

    Uses the LLM to evaluate:
    - brand_relevance: fit with Rekt CEO's dark-humor, degen voice
    - meme_potential: virality potential as a meme
    - composite_score: weighted average used for final ranking

    Populates state["scored_trends"] with ranked, enriched topics.
    """
    print("\n🎯 NODE 3: Rekt Relevance Scoring")
    print("=" * 50)

    researched: List[Dict] = state.get("researched_trends", [])
    dry_run: bool = state.get("config", {}).get("dry_run", False)

    if not researched:
        print("  ⚠️  No researched topics found, skipping scoring")
        state["scored_trends"] = []
        return state

    if dry_run:
        print("  🧪 DRY RUN MODE — using simplified scoring")
        # Create deterministic scores based on known crypto topics
        scored = []
        preset_scores = {
            "#Bitcoin":    (0.70, 0.65),
            "#BTC":        (0.72, 0.65),
            "#Ethereum":   (0.80, 0.75),
            "#ETH":        (0.78, 0.72),
            "#Solana":     (0.85, 0.90),
            "#DeFi":       (0.88, 0.82),
            "#NFT":        (0.75, 0.70),
            "#Memecoin":   (0.95, 0.98),
            "#Web3":       (0.72, 0.68),
            "#Altcoin":    (0.80, 0.85),
            "#Blockchain": (0.55, 0.45),
            "#Crypto":     (0.78, 0.75),
        }
        dry_run_meme_angles = {
            "#Memecoin": ["degen FOMO", "rug pull incoming", "100x or food stamps"],
            "#DeFi":     ["Aping into pools", "impermanent loss hurts", "yield farm and chill"],
            "#NFT":      ["floor is lava (and melting)", "JPEG gains", "right-click save moment"],
        }
        for t in researched:
            brand_r, meme_p = preset_scores.get(t["topic"], (0.60, 0.60))
            composite = round(0.4 * brand_r + 0.35 * meme_p + 0.25 * t.get("forecast_7d_probability", 0.5), 3)
            scored.append({
                **t,
                "brand_relevance": brand_r,
                "meme_potential": meme_p,
                "composite_score": composite,
                "meme_angles": dry_run_meme_angles.get(t["topic"], ["general crypto roast", "market chaos"]),
                "one_liner": f"gm everyone, {t['topic']} is trending again. stay rekt. 💀",
            })
    else:
        # Load brand context from RAG once for all batches
        print("  🧠 Retrieving brand context from RAG...")
        brand_context = query_brand_context(
            "Rekt CEO brand identity tone meme style audience crypto degen scoring criteria",
            k=6,
        )

        llm = get_llm("analysis")
        scored = []

        # Process in batches of 5 to stay within token limits
        batch_size = 5
        for i in range(0, len(researched), batch_size):
            batch = researched[i:i + batch_size]
            print(f"  🤖 Scoring batch {i // batch_size + 1}/{(len(researched) + batch_size - 1) // batch_size} ({len(batch)} topics)...")
            try:
                scores = _score_batch(batch, llm, brand_context)
                # Map scores back to full topic dicts
                score_map = {s["topic"]: s for s in scores}
                for topic in batch:
                    s = score_map.get(topic["topic"], {})
                    brand_r = float(s.get("brand_relevance", 0.5))
                    meme_p = float(s.get("meme_potential", 0.5))
                    forecast_p = topic.get("forecast_7d_probability", 0.5)
                    composite = round(0.4 * brand_r + 0.35 * meme_p + 0.25 * forecast_p, 3)
                    scored.append({
                        **topic,
                        "brand_relevance": brand_r,
                        "meme_potential": meme_p,
                        "composite_score": composite,
                        "meme_angles": s.get("meme_angles", []),
                        "one_liner": s.get("one_liner", ""),
                    })
            except Exception as e:
                print(f"  ⚠️  Batch scoring failed: {e} — using defaults")
                for topic in batch:
                    scored.append({
                        **topic,
                        "brand_relevance": 0.5,
                        "meme_potential": 0.5,
                        "composite_score": 0.5,
                        "meme_angles": [],
                        "one_liner": "",
                    })

    # Sort by composite score descending
    scored.sort(key=lambda x: x.get("composite_score", 0), reverse=True)

    state["scored_trends"] = scored

    print(f"\n  ✅ Scoring complete — top topic: {scored[0]['topic']} (score: {scored[0].get('composite_score', 0):.2f})")
    return state
