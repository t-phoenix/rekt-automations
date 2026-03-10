"""Twitter Engagement Node 4: Format and output the engagement report as table."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box


console = Console()


def _score_bar(score: float, width: int = 8) -> str:
    """Convert 0-1 score to a compact bar string."""
    filled = round(score * width)
    return "█" * filled + "░" * (width - filled)


def _build_rich_table(scored_tweets: List[Dict]) -> Table:
    """Build a rich console table from scored tweets."""
    table = Table(
        title="🔥 Rekt CEO Twitter Engagement Targets",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        title_style="bold cyan",
        border_style="bright_black",
        min_width=120,
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Author", style="bold white", min_width=14)
    table.add_column("Followers", justify="right", min_width=9)
    table.add_column("Likes", justify="right", min_width=9)
    table.add_column("Replies", justify="right", min_width=9)
    table.add_column("Relevancy", justify="center", min_width=10)
    table.add_column("Virality", justify="center", min_width=10)
    table.add_column("⭐ Score", justify="center", min_width=9)

    for i, t in enumerate(scored_tweets, 1):
        rel_score = t.get("relevancy_score", 0.5)
        viral_score = t.get("virality_potential", 0.5)
        composite = t.get("composite_score", 0.5)

        # Colour the composite score
        if composite >= 0.80:
            score_style = "bold green"
        elif composite >= 0.60:
            score_style = "bold yellow"
        else:
            score_style = "dim red"

        # Number formatting
        followers = t.get("author_followers", 0)
        followers_str = f"{followers / 1000:.1f}K" if followers >= 1000 else str(followers)
        
        likes = t.get("likes", 0)
        likes_str = f"{likes / 1000:.1f}K" if likes >= 1000 else str(likes)
        
        replies = t.get("replies", 0)
        replies_str = f"{replies / 1000:.1f}K" if replies >= 1000 else str(replies)

        author_str = f"@{t.get('author_handle', '')}"

        table.add_row(
            str(i),
            author_str,
            followers_str,
            likes_str,
            replies_str,
            _score_bar(rel_score),
            _score_bar(viral_score),
            Text(f"{composite:.2f}", style=score_style),
        )

    return table


def _build_markdown_table(suggested_replies: List[Dict], run_id: str) -> str:
    """Build a Markdown table report."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# 🔥 Rekt CEO Twitter Engagement Targets",
        f"> Generated: {now} | Run ID: `{run_id}`",
        "",
        "## Top Tweets to Engage With",
        "",
        "| # | Author | Followers | Likes | Relevancy | Virality | ⭐ Score |",
        "|---|--------|-----------|-------|-----------|----------|---------|",
    ]

    for i, t in enumerate(suggested_replies, 1):
        rel_score = t.get("relevancy_score", 0.5)
        viral_score = t.get("virality_potential", 0.5)
        composite = t.get("composite_score", 0.5)

        followers = t.get("author_followers", 0)
        followers_str = f"{followers / 1000:.1f}K" if followers >= 1000 else str(followers)
        
        likes = t.get("likes", 0)
        likes_str = f"{likes / 1000:.1f}K" if likes >= 1000 else str(likes)

        author_str = f"@{t.get('author_handle', '')}"

        lines.append(
            f"| {i} | **{author_str}** | {followers_str} | {likes_str} | "
            f"{rel_score:.2f} | {viral_score:.2f} | **{composite:.2f}** |"
        )

    lines += [
        "",
        "---",
        "",
        "## Suggested Replies",
        "",
        "*Click the Tweet URL, copy the suggested reply, and paste to engage.*",
        "",
    ]

    for i, t in enumerate(suggested_replies, 1):
        lines += [
            f"### {i}. @{t.get('author_handle', '')}",
            "",
            f"**Original Tweet:** _{t.get('text', '')}_",
            f"**URL:** [Link]({t.get('url', '')})",
            "",
            f"**Reply Strategy:** {t.get('reply_strategy', 'N/A')}",
            "",
            "**Suggested Reply to Copy:**",
            "```text",
            t.get('suggested_reply', ''),
            "```",
            "",
            "---",
            "",
        ]

    return "\n".join(lines)


def twitter_engagement_output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Twitter Engagement Node 4: Render final table and save files.

    Outputs:
    - Rich console table (printed live)
    - Markdown report  →  output/runs/<run-id>/twitter_engagement/engagement_report.md
    - Structured JSON  →  output/runs/<run-id>/twitter_engagement/engagement_data.json
    """
    print("\n📊 NODE 4: Twitter Engagement Output")
    print("=" * 50)

    scored: List[Dict] = state.get("scored_tweets", [])
    replies: List[Dict] = state.get("suggested_replies", [])
    run_id: str = state.get("execution_metadata", {}).get("execution_id", "unknown")
    engagement_dir: Path = state.get("_engagement_dir")

    if not scored:
        print("  ⚠️  No target tweets to display")
        return state

    # ── Console table ─────────────────────────────────────────────────────
    rich_table = _build_rich_table(scored)
    console.print()
    console.print(rich_table)
    console.print()
    
    # Also print out the top reply directly to console for instant copy-paste
    if replies:
        top = replies[0]
        console.print(f"[bold cyan]🎯 Top Engagement Target:[/bold cyan] @{top.get('author_handle')} ([link={top.get('url')}]View Tweet[/link])")
        console.print(f"[bold]Strategy:[/bold] {top.get('reply_strategy')}")
        console.print(f"[bold green]Reply:[/bold green]")
        console.print(f"  {top.get('suggested_reply')}")
        console.print()

    # ── Markdown file ─────────────────────────────────────────────────────
    md_content = _build_markdown_table(replies, run_id)

    if engagement_dir:
        md_path = engagement_dir / "engagement_report.md"
        md_path.write_text(md_content, encoding="utf-8")
        print(f"  📄 Saved Markdown report: {md_path}")

        # ── JSON file ─────────────────────────────────────────────────────
        json_path = engagement_dir / "engagement_data.json"
        json_path.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "generated_at": datetime.utcnow().isoformat(),
                    "top_targets": replies,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"  📦 Saved JSON data:     {json_path}")
    else:
        print("  ⚠️  No engagement_dir in state — skipping file saves")

    print(f"\n  ✅ Report complete — {len(replies)} targets ready")
    return state
