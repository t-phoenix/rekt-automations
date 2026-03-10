"""Competition Research Node 4: Strategy Extraction (RAG)"""
import json
from typing import Dict, Any, List
from src.rag.retriever import query_brand_context
from src.utils.llm_utils import get_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

def strategy_extraction_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 4: Analyze high-performing competitor posts using RAG brand context
    to extract psychological hooks, formatting, and engagement strategies.
    """
    print("\n🧠 NODE 4: Strategy Extraction (RAG)")
    print("=" * 50)

    top_posts = state.get("filtered_metrics", [])
    if not top_posts:
        print("  ⚠️ No posts met the engagement threshold. Skipping strategy extraction.")
        state["strategy_analysis"] = {"hooks": [], "tone": "N/A", "summary": "No data"}
        return state

    # 1. Fetch Rekt CEO's brand vibe using RAG
    print("  📚 Fetching brand context via RAG...")
    brand_context = query_brand_context(
        "competitor analysis, tone of voice, formatting for engagement, how Rekt CEO hooks their audience",
        k=3
    )

    # 2. Format the top posts for the LLM
    posts_text = "\n\n".join([f"Author: @{p['author_handle']}\nLikes: {p['likes']}\nText: {p['text']}" for p in top_posts[:10]])

    prompt_template = """
You are a master Web3 marketing analyst and strategist advising the 'Rekt CEO' brand.

--- Rekt CEO Brand Context ---
{brand_context}
------------------------------

--- Competitor Top Performing Posts ---
{competitor_posts}
---------------------------------------

Analyze these highly engaged competitor posts in the context of our Rekt CEO brand.
Identify the overarching strategies that made them successful, specifically formatting, psychological hooks, and tone.

Return a JSON object matching this schema exactly:
{{
    "high_level_summary": "1 paragraph summary of what's working right now across competitors",
    "top_hooks": ["Hook strategy 1 (e.g., Calling out VC dumps)", "Hook strategy 2"],
    "tone_analysis": "How these posts match or differ from our brand tone",
    "formatting_trends": ["Short sentences", "Heavy line breaks", "No emojis"]
}}

Do not include any Markdown fencing around the JSON output.
    """

    prompt = PromptTemplate.from_template(prompt_template)
    llm = get_llm(task_type="analysis")
    parser = JsonOutputParser()

    chain = prompt | llm | parser

    print("  🤖 Extracting strategies from top competitor posts...")
    try:
        strategy_analysis = chain.invoke({
            "brand_context": brand_context,
            "competitor_posts": posts_text
        })
        print("  ✅ Strategy extraction complete")
        state["strategy_analysis"] = strategy_analysis
    except Exception as e:
        print(f"    ⚠️  LLM strategy extraction failed: {e}")
        state["strategy_analysis"] = {
            "error": str(e),
            "high_level_summary": "Failed to extract strategies.",
            "top_hooks": [],
            "tone_analysis": "Error analyzing tone.",
            "formatting_trends": []
        }

    return state
