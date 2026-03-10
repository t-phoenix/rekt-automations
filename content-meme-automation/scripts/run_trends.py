#!/usr/bin/env python3
"""
Runner script for Trend Research Flow (Flow 4).

Usage:
    python run_trends_flow.py
    python run_trends_flow.py --override "dry_run=true"
    python run_trends_flow.py --override "dry_run=true" --dry-run
"""
import sys
import click
from pathlib import Path
from rich.console import Console

# Add project root to path (parent of src/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.flows import TrendResearchFlow

console = Console()


@click.command()
@click.option(
    '--override',
    type=str,
    default=None,
    help='Configuration overrides (format: key1=value1,key2=value2)'
)
@click.option(
    '--dry-run',
    is_flag=True,
    default=False,
    help='Use fixture data instead of real API calls (no keys needed)'
)
def main(override, dry_run):
    """🔥 Run Trend Research Flow — Twitter trends + Perplexity research + Rekt scoring."""

    console.print("\n[bold cyan]Trend Research Flow[/bold cyan]")
    console.print("[dim]Real-time crypto Twitter trend intelligence for Rekt CEO[/dim]\n")

    # Apply dry_run flag to override string
    if dry_run:
        override = ((override or '') + ',dry_run=true').lstrip(',')

    try:
        flow = TrendResearchFlow(override_string=override)
        output = flow.run()

        report = output.get("trend_report", {})

        console.print(f"\n[bold green]✓ Flow completed successfully![/bold green]")
        console.print(f"[bold]Run ID:[/bold] [cyan]{flow.run_id}[/cyan]")
        console.print(f"\n[bold]Top Topic:[/bold] [white]{report.get('top_topic', 'N/A')}[/white] "
                      f"(score: {report.get('top_score', 0):.2f})")
        console.print(f"\n[dim]Outputs saved to: output/runs/{flow.run_id}/trends/[/dim]")
        console.print(f"  📄 trend_report.md  — full Markdown table + deep-dives")
        console.print(f"  📦 trend_data.json  — structured JSON\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Flow failed:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
