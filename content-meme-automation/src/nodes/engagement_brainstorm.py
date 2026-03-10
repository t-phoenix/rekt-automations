"""KOL Research Node 4: Engagement Brainstorm (RAG & Latest Output)."""
import json
from typing import Dict, Any, List
from src.rag.retriever import query_brand_context
from src.utils.llm_utils import get_llm
from src.utils.supabase_client import get_supabase_client
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def engagement_brainstorm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 4: Brainstorm engagement replies using RAG & latest competition output.
    """
    print("\n💡 NODE 4: Engagement Brainstorm")
    print("=" * 50)

    scored_kols = state.get("scored_kols", [])
    if not scored_kols:
        print("  ⚠️ No KOLs to brainstorm for.")
        state["engagement_plans"] = []
        return state

    # 1. Fetch Rekt CEO's brand vibe using RAG
    print("  📚 Fetching brand context via RAG...")
    brand_context = query_brand_context("sarcastic, reply strategy, interaction format of Rekt CEO", k=3)

    # 2. Fetch latest competition strategy from Supabase
    print("  🗄️ Fetching latest competitor strategy output...")
    competition_strategy = "Be highly engaging. (Mock fallback)"
    try:
        sb = get_supabase_client()
        resp = sb.table("rekt_competition_research").select("result_output").order("created_at", desc=True).limit(1).execute()
        if resp.data and len(resp.data) > 0:
            competition_strategy = json.dumps(resp.data[0].get("result_output", {}))
            print("  ✅ Successfully fetched latest strategies from Supabase")
        else:
            print("  ⚠️ No previous competition strategy found in DB")
    except Exception as e:
        print(f"  ⚠️ Supabase fetch failed: {e}")

    engagement_plans = []
    llm = get_llm(task_type="content_generation")
    parser = JsonOutputParser()

    prompt_template = """
You are acting as the social media manager for the 'Rekt CEO' brand.

--- Rekt CEO Brand Context & Tone ---
{brand_context}
-------------------------------------

--- Best-in-Class Competitor Strategy (Use this psychology!) ---
{competition_strategy}
----------------------------------------------------------------

--- Target KOL Profile ---
Handle: @{handle}
Bio: {bio}
Compatibility Score: {score}/100
Reasoning: {reason}
--------------------------

--- Latest KOL Post ---
Post Text: {latest_tweet}
Post URL: {tweet_url}
-----------------------

Draft a highly customized, authentic reply to this exact post.
Do NOT sound like a typical corporate bot or generic "good post bro".
Use our RAG brand context and apply the competitor strategy hooks. It must sound degen, slightly sarcastic, but engaging enough to get a response or retweet.

Return a JSON object:
{{
    "reply_strategy": "1 sentence explanation of the psychological angle for this reply",
    "suggested_reply": "The exact wording of the reply (max 150 characters, no hashtags)"
}}
    """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | parser

    # Take top 5 KOLs by compatibility
    top_kols = [k for k in scored_kols if k.get("compatibility_score", 0) > 50][:5]

    for kol in top_kols:
        print(f"  ✍️ Brainstorming reply to @{kol['handle']}...")
        if not kol.get("recent_tweets"):
            continue

        latest_tweet = kol["recent_tweets"][0]

        try:
            res = chain.invoke({
                "brand_context": brand_context,
                "competition_strategy": competition_strategy,
                "handle": kol['handle'],
                "bio": kol.get('bio', ''),
                "score": kol.get("compatibility_score", 0),
                "reason": kol.get("alignment_reasoning", ""),
                "latest_tweet": latest_tweet.get("text", ""),
                "tweet_url": latest_tweet.get("url", "Link unavailable")
            })
            
            enrich = {
                "kol": f"@{kol['handle']}",
                "compatibility": kol.get("compatibility_score", 0),
                "post": latest_tweet.get("text", ""),
                "post_url": latest_tweet.get("url", "Link unavailable"),
                "strategy": res.get("reply_strategy", "N/A"),
                "reply": res.get("suggested_reply", "N/A")
            }
            engagement_plans.append(enrich)

        except Exception as e:
            print(f"    ⚠️ failed to brainstorm for @{kol['handle']}: {e}")
            
    state["engagement_plans"] = engagement_plans
    print(f"  ✅ Brainstormed {len(engagement_plans)} custom engagement plans.")
    return state
