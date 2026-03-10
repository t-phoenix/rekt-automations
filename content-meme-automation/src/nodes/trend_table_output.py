"""Trend Research Node 4: Format and output the trend report as table."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box


console = Console()


def _momentum_emoji(momentum: str) -> str:
    return {"rising": "📈", "stable": "➡️", "fading": "📉"}.get(momentum, "➡️")


def _score_bar(score: float, width: int = 8) -> str:
    """Convert 0-1 score to a compact bar string."""
    filled = round(score * width)
    return "█" * filled + "░" * (width - filled)


def _build_rich_table(scored_trends: List[Dict]) -> Table:
    """Build a rich console table from scored trends."""
    table = Table(
        title="🔥 Rekt CEO Trend Intelligence Report",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        title_style="bold cyan",
        border_style="bright_black",
        min_width=120,
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Topic", style="bold white", min_width=14)
    table.add_column("Locations", style="dim", min_width=12)
    table.add_column("Today Vol", justify="right", min_width=9)
    table.add_column("7d Trend", justify="center", min_width=9)
    table.add_column("Momentum", justify="center", min_width=10)
    table.add_column("Forecast 7d", justify="center", min_width=12)
    table.add_column("Brand Fit", justify="center", min_width=10)
    table.add_column("Meme 🎭", justify="center", min_width=9)
    table.add_column("⭐ Score", justify="center", min_width=9)

    for i, t in enumerate(scored_trends, 1):
        momentum = t.get("momentum", "stable")
        brand_r = t.get("brand_relevance", 0.5)
        meme_p = t.get("meme_potential", 0.5)
        composite = t.get("composite_score", 0.5)
        forecast_p = t.get("forecast_7d_probability", 0.5)

        # Colour the composite score
        if composite >= 0.80:
            score_style = "bold green"
        elif composite >= 0.60:
            score_style = "bold yellow"
        else:
            score_style = "dim red"

        # Volume formatting
        today_vol = t.get("today_volume", 0)
        vol_str = f"{today_vol / 1000:.1f}K" if today_vol >= 1000 else str(today_vol)

        vol_7d = t.get("volume_7d", 0)
        vol_7d_str = f"{vol_7d / 1000:.1f}K" if vol_7d >= 1000 else (str(vol_7d) if vol_7d else "–")

        locations = t.get("locations", [])
        loc_str = ", ".join(locations[:3]) + ("…" if len(locations) > 3 else "")

        forecast_str = f"{forecast_p:.0%}"
        forecast_style = "green" if forecast_p >= 0.7 else ("yellow" if forecast_p >= 0.4 else "red")

        table.add_row(
            str(i),
            t.get("topic", ""),
            loc_str,
            vol_str,
            vol_7d_str,
            f"{_momentum_emoji(momentum)} {momentum}",
            Text(forecast_str, style=forecast_style),
            _score_bar(brand_r),
            _score_bar(meme_p),
            Text(f"{composite:.2f}", style=score_style),
        )

    return table


def _build_markdown_table(scored_trends: List[Dict], run_id: str) -> str:
    """Build a Markdown table report."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# 🔥 Rekt CEO Trend Intelligence Report",
        f"> Generated: {now} | Run ID: `{run_id}`",
        "",
        "## Trending Topics Analysis",
        "",
        "| # | Topic | Locations | Today Vol | 7d Volume | Momentum | Forecast 7d ↗ | Brand Fit | Meme 🎭 | ⭐ Score |",
        "|---|-------|-----------|-----------|-----------|----------|--------------|-----------|---------|---------|",
    ]

    for i, t in enumerate(scored_trends, 1):
        momentum = t.get("momentum", "stable")
        forecast_p = t.get("forecast_7d_probability", 0.5)
        brand_r = t.get("brand_relevance", 0.5)
        meme_p = t.get("meme_potential", 0.5)
        composite = t.get("composite_score", 0.5)

        today_vol = t.get("today_volume", 0)
        vol_str = f"{today_vol / 1000:.1f}K" if today_vol >= 1000 else str(today_vol)

        vol_7d = t.get("volume_7d", 0)
        vol_7d_str = f"{vol_7d / 1000:.1f}K" if vol_7d >= 1000 else (str(vol_7d) if vol_7d else "–")

        locations = t.get("locations", [])
        loc_str = ", ".join(locations[:3]) + ("…" if len(locations) > 3 else "")

        emoji = _momentum_emoji(momentum)
        lines.append(
            f"| {i} | **{t.get('topic', '')}** | {loc_str} | {vol_str} | "
            f"{vol_7d_str} | {emoji} {momentum} | {forecast_p:.0%} | "
            f"{brand_r:.2f} | {meme_p:.2f} | **{composite:.2f}** |"
        )

    lines += [
        "",
        "---",
        "",
        "## Topic Deep-Dives",
        "",
    ]

    for i, t in enumerate(scored_trends[:10], 1):
        topic = t.get("topic", "")
        lines += [
            f"### {i}. {topic}",
            "",
            f"**7-Day History:** {t.get('history_7d_summary', 'N/A')}",
            "",
            f"**Forecast:** {t.get('forecast_reason', 'N/A')}",
            "",
        ]
        meme_angles = t.get("meme_angles", [])
        if meme_angles:
            lines.append("**Meme Angles:**")
            for angle in meme_angles:
                lines.append(f"- {angle}")
            lines.append("")

        one_liner = t.get("one_liner", "")
        if one_liner:
            lines.append(f"**Rekt CEO One-liner:** _{one_liner}_")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines += [
        "## Score Legend",
        "",
        "| Column | Meaning |",
        "|--------|---------|",
        "| **Brand Fit** | How well the topic fits Rekt CEO's sarcastic, crypto-degen voice (0–1) |",
        "| **Meme 🎭** | How meme-worthy / viral this topic is (0–1) |",
        "| **⭐ Score** | Composite: 40% Brand + 35% Meme + 25% Forecast |",
        "| **Forecast 7d** | Perplexity-estimated probability of trending next week |",
        "| **Momentum** | Rising 📈 / Stable ➡️ / Fading 📉 — based on engagement trend |",
    ]

    return "\n".join(lines)


def trend_table_output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trend Research Node 4: Render final trend report.

    Outputs:
    - Rich console table (printed live)
    - Markdown report  →  output/runs/<run-id>/trends/trend_report.md
    - Structured JSON  →  output/runs/<run-id>/trends/trend_data.json
    """
    print("\n📊 NODE 4: Trend Table Output")
    print("=" * 50)

    scored: List[Dict] = state.get("scored_trends", [])
    run_id: str = state.get("execution_metadata", {}).get("execution_id", "unknown")
    trends_dir: Path = state.get("_trends_dir")

    if not scored:
        print("  ⚠️  No scored trends to display")
        state["trend_report"] = {}
        return state

    # ── Console table ─────────────────────────────────────────────────────
    rich_table = _build_rich_table(scored)
    console.print()
    console.print(rich_table)
    console.print()

    # ── Markdown file ─────────────────────────────────────────────────────
    md_content = _build_markdown_table(scored, run_id)

    if trends_dir:
        md_path = trends_dir / "trend_report.md"
        md_path.write_text(md_content, encoding="utf-8")
        print(f"  📄 Saved Markdown report: {md_path}")

        # ── JSON file ─────────────────────────────────────────────────────
        json_path = trends_dir / "trend_data.json"
        json_path.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "generated_at": datetime.utcnow().isoformat(),
                    "topics": scored,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"  📦 Saved JSON data:     {json_path}")
    else:
        print("  ⚠️  No trends_dir in state — skipping file saves")

    state["trend_report"] = {
        "topic_count": len(scored),
        "top_topic": scored[0]["topic"] if scored else None,
        "top_score": scored[0].get("composite_score", 0) if scored else 0,
        "markdown": md_content,
    }

    print(f"\n  ✅ Report complete — {len(scored)} topics ranked")
    return state
