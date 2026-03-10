"""Competition Research Node 5: Output Report & Storage"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from src.utils.supabase_client import get_supabase_client

def competition_research_output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 5: Output markdown report and save to Supabase.
    """
    print("\n📦 NODE 5: Competition Research Output")
    print("=" * 50)

    run_id = state.get("execution_metadata", {}).get("execution_id", "unknown")
    strategy = state.get("strategy_analysis", {})
    top_posts = state.get("filtered_metrics", [])
    output_dir: Path = state.get("_competition_dir")

    # 1. Build Markdown Report
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# 🕵️ Competition Research Report",
        f"> Generated: {now} | Run ID: `{run_id}`",
        "",
        "## 🧠 Strategy Extracted",
        f"**Summary:** {strategy.get('high_level_summary', 'N/A')}",
        "",
        "### Top Hooks",
    ]
    
    for hook in strategy.get('top_hooks', []):
        lines.append(f"- {hook}")
        
    lines += [
        "",
        "### Tone & Formatting",
        f"**Tone:** {strategy.get('tone_analysis', 'N/A')}",
        "**Formatting Trends:** " + ", ".join(strategy.get('formatting_trends', [])),
        "",
        "## 🔥 Top Competitor Posts Analyzed",
        "| Author | Likes | Retweets | Preview | URL |",
        "|--------|-------|----------|---------|-----|"
    ]
    
    for tw in top_posts[:15]:
        preview = tw.get('text', '').replace('\n', ' ')[:60] + "..."
        likes = tw.get('likes', 0)
        retweets = tw.get('retweets', 0)
        author = f"@{tw.get('author_handle', '')}"
        url = tw.get('url', '')
        lines.append(f"| **{author}** | {likes} | {retweets} | _{preview}_ | [Link]({url}) |")

    md_content = "\n".join(lines)
    
    # 2. Save locally
    if output_dir:
        md_path = output_dir / "competition_report.md"
        md_path.write_text(md_content, encoding="utf-8")
        json_path = output_dir / "competition_data.json"
        
        full_data = {
            "run_id": run_id,
            "generated_at": datetime.utcnow().isoformat(),
            "strategy": strategy,
            "top_posts": top_posts,
            "competitors": state.get("discovered_competitors", [])
        }
        json_path.write_text(json.dumps(full_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  📄 Saved markdown: {md_path}")
        print(f"  📦 Saved JSON: {json_path}")

    # 3. Save to Supabase
    try:
        print(f"  💾 Saving to Supabase...")
        sb = get_supabase_client()
        sb.table("rekt_meme_automation_runs").upsert({
            "id": run_id,
            "status": "competition_research_complete",
            "configuration": state.get("config", {})
        }).execute()
        
        sb.table("rekt_competition_research").insert({
            "run_id": run_id,
            "competitors": state.get("discovered_competitors", []),
            "intermediary_metadata": state.get("raw_twitter_data", {}),
            "processed_data": state.get("filtered_metrics", {}),
            "result_output": state.get("strategy_analysis", {})
        }).execute()
        
        print("  ✅ Saved Competition Research to Supabase")
    except Exception as e:
        print(f"  ⚠️  Failed to save to Supabase: {e}")

    state["competition_report_md"] = md_content
    return state
