"""KOL Research Node 3: Alignment Scoring (RAG)"""
from typing import Dict, Any
from src.rag.retriever import query_brand_context
from src.utils.llm_utils import get_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def alignment_scoring_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Assess KOL compatibility with Rekt CEO brand using RAG.
    Assigns a compatibility score 0-100.
    """
    print("\n🎯 NODE 3: Rekt Alignment Scoring")
    print("=" * 50)

    kol_data = state.get("kol_data", [])
    if not kol_data:
        print("  ⚠️ No KOL data available to score.")
        state["scored_kols"] = []
        return state

    print("  📚 Fetching brand context via RAG...")
    brand_context = query_brand_context("sarcastic, degen vibe, target audience persona of Rekt CEO", k=3)

    scored_kols = []
    llm = get_llm(task_type="analysis")
    parser = JsonOutputParser()

    prompt_template = """
You are scoring KOLs (Key Opinion Leaders) for the 'Rekt CEO' brand.

--- Rekt CEO Brand Context ---
{brand_context}
------------------------------

--- KOL Profile ---
Handle: @{handle}
Bio: {bio}
Last 5 Tweets: {tweets}
-------------------

Evaluate this KOL's psychological alignment and tone against the Rekt CEO brand's funny, sarcastic, degen vibe.
Return a JSON object:
{{
    "compatibility_score": integer 0-100,
    "alignment_reasoning": "1-2 sentences on why they fit or don't fit"
}}
    """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | parser

    for kol in kol_data:
        print(f"  ⚖️ Scoring @{kol['handle']}...")
        tweet_summary = " | ".join([t['text'] for t in kol['recent_tweets']])
        try:
            res = chain.invoke({
                "brand_context": brand_context,
                "handle": kol['handle'],
                "bio": kol['bio'],
                "tweets": tweet_summary
            })
            
            # Merge score into kol dict
            enriched = {**kol, **res}
            scored_kols.append(enriched)

        except Exception as e:
            print(f"    ⚠️ failed to score @{kol['handle']}: {e}")
            scored_kols.append({**kol, "compatibility_score": 0, "alignment_reasoning": "Error scoring"})

    # Sort descending by score
    scored_kols.sort(key=lambda x: x.get("compatibility_score", 0), reverse=True)
    
    state["scored_kols"] = scored_kols
    print(f"  ✅ Scored {len(scored_kols)} KOLs")
    return state
