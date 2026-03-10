"""KOL Research Node 5: KOL Output Report & Storage"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from src.utils.supabase_client import get_supabase_client

def kol_research_output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 5: Output KOL markdown report and save to Supabase.
    """
    print("\n📦 NODE 5: KOL Research Output")
    print("=" * 50)

    run_id = state.get("execution_metadata", {}).get("execution_id", "unknown")
    kols = state.get("scored_kols", [])
    plans = state.get("engagement_plans", [])
    output_dir: Path = state.get("_kol_dir")

    # 1. Build Markdown Report
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# 🎯 KOL / Ideal Audience Target Report",
        f"> Generated: {now} | Run ID: `{run_id}`",
        "",
        "## 🔥 Top Matching KOLs",
        "| Ranking | Handle | Score | Followers | Alignment Reason |",
        "|---------|--------|-------|-----------|------------------|"
    ]
    
    for i, kol in enumerate(kols[:10]):
        reason = kol.get('alignment_reasoning', '').replace('\n', ' ')[:60] + "..."
        lines.append(f"| {i+1} | **@{kol.get('handle', '')}** | {kol.get('compatibility_score', 0)}% | {kol.get('followers', 0)} | _{reason}_ |")
        
    lines += [
        "",
        "## 💬 Master Engagement Plans (Copy/Paste)",
        ""
    ]
    
    for plan in plans:
        lines += [
            f"### Target: {plan.get('kol')} (Match: {plan.get('compatibility')}%)",
            f"**Recent Post:** _{plan.get('post', '')}_",
            f"**Post URL:** [Link]({plan.get('post_url', '#')})",
            "",
            f"**Strategic Angle:** {plan.get('strategy', 'N/A')}",
            "**Drafted Reply:**",
            "```text",
            plan.get('reply', 'N/A'),
            "```",
            "---",
            ""
        ]

    md_content = "\n".join(lines)
    
    if output_dir:
        md_path = output_dir / "kol_report.md"
        md_path.write_text(md_content, encoding="utf-8")
        json_path = output_dir / "kol_data.json"
        
        full_data = {
            "run_id": run_id,
            "generated_at": datetime.utcnow().isoformat(),
            "scored_kols": kols,
            "engagement_plans": plans
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
            "status": "kol_research_complete",
            "configuration": state.get("config", {})
        }).execute()
        
        sb.table("rekt_kol_research").insert({
            "run_id": run_id,
            "target_criteria": state.get("config", {}).get("target_topics", []),
            "identified_kols": kols,
            "engagement_plans": plans
        }).execute()
        
        print("  ✅ Saved KOL Research to Supabase")
    except Exception as e:
        print(f"  ⚠️  Failed to save to Supabase: {e}")

    state["kol_report_md"] = md_content
    return state
