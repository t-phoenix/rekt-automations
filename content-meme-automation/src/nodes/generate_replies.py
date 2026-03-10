"""Twitter Engagement Node 3: Generate replies to top tweets."""
import json
from typing import Dict, Any, List

from ..utils.llm_utils import get_llm
from ..rag import query_brand_context
from langchain_core.prompts import ChatPromptTemplate

REPLY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "{brand_context}\n\nYou are the Rekt CEO. You are drafting replies to crypto/memecoin tweets to farm engagement.\nCRITICAL RULES:\n1. NO REPETITIVE TROPES. Every reply must be completely unique.\n2. Apply human emotional intelligence—read the room. If they are euphoric, be the grim reaper. If they are depressed about a rug, offer dark humor solidarity.\n3. Be edgy, savage, or deeply insightful about the degen condition. Never be cringe, and never sound like an AI.\n4. Do NOT use the exact same slang in every reply (avoid spamming 'WAGMI', 'NGMI', 'ser', etc.).\n5. {tone_instructions}"),
    ("user", """Draft a highly unique, engagement-farming reply for the following tweet.
Embody the Rekt CEO persona with high emotional intelligence and zero clichés.

Author: @{author_handle} ({author_followers} followers)
Original Tweet: "{tweet_text}"

Return ONLY a JSON object with:
- "suggested_reply": the actual text of the reply (max 280 chars)
- "reply_strategy": a 1-sentence psychological breakdown of why this specific emotional angle works here.
""")
])


def generate_replies_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Twitter Engagement Node 3: Generate savage replies to the best tweets.
    
    Acts on the top 3 scored tweets.
    Populates state["suggested_replies"] with the tweet data plus the generated reply.
    """
    print("\n✍️ NODE 3: Generate Replies")
    print("=" * 50)

    scored: List[Dict] = state.get("scored_tweets", [])
    dry_run: bool = state.get("config", {}).get("dry_run", False)

    if not scored:
        print("  ⚠️  No scored tweets available to reply to.")
        state["suggested_replies"] = []
        return state

    # Only draft replies for the top 3
    top_targets = scored[:3]
    replies = []

    if dry_run:
        print("  🧪 DRY RUN MODE — using simulated replies")
        for t in top_targets:
            replies.append({
                **t,
                "suggested_reply": f"bro your bag is practically a stablecoin at this point @{t.get('author_handle')}",
                "reply_strategy": "roast their portfolio",
            })
    else:
        print("  🧠 Retrieving brand tone context from RAG...")
        brand_context = query_brand_context(
            "Rekt CEO tone of voice communication style roast savage engagement",
            k=5,
        )
        
        llm = get_llm("drafting")
        
        reply_tone = state.get("config", {}).get("reply_tone")
        tone_instructions = f"Target tone/voice for this specific reply batch: {reply_tone}" if reply_tone else "Stick to the default brand persona."
        
        for i, tweet in enumerate(top_targets):
            print(f"  💬 Drafting reply {i+1}/3 to @{tweet.get('author_handle')}...")
            
            try:
                chain = REPLY_PROMPT | llm
                response = chain.invoke({
                    "brand_context": brand_context,
                    "author_handle": tweet.get("author_handle", "user"),
                    "author_followers": tweet.get("author_followers", 0),
                    "tweet_text": tweet.get("text", ""),
                    "tone_instructions": tone_instructions
                })

                content = response.content.strip()
                if content.startswith("```"):
                    lines = content.split("\n")
                    content = "\n".join(lines[1:-1])

                reply_data = json.loads(content)
                
                replies.append({
                    **tweet,
                    "suggested_reply": reply_data.get("suggested_reply", ""),
                    "reply_strategy": reply_data.get("reply_strategy", "LLM strategy"),
                })
            except Exception as e:
                print(f"  ⚠️  Failed to draft reply for {tweet.get('id')}: {e}")

    state["suggested_replies"] = replies
    print(f"  ✅ Drafted {len(replies)} engagement replies")
    return state
