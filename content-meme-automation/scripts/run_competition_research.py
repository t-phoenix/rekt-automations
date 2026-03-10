#!/usr/bin/env python3
"""
Runner script for Competition Research Flow (Flow 6).

Usage:
    python run_competition_research.py
    python run_competition_research.py --override "lookback_hours=12"
"""
import sys
import click
from pathlib import Path
from rich.console import Console

# Add project root to path (parent of src/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.flows import CompetitionResearchFlow

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
    help='Use mock data instead of real API calls'
)
def main(override, dry_run):
    """🕵️ Run Competition Research Flow."""
    console.print("\n[bold cyan]Competition Research Flow[/bold cyan]")
    console.print("[dim]Scraping competitor posts and extracting successful Rekt CEO strategies using RAG[/dim]\n")

    if dry_run:
        override = ((override or '') + ',dry_run=true').lstrip(',')

    try:
        flow = CompetitionResearchFlow(override_string=override)
        output = flow.run()

        console.print(f"\n[bold green]✓ Competition Research Flow completed successfully![/bold green]")
        console.print(f"[bold]Run ID:[/bold] [cyan]{flow.run_id}[/cyan]")
        console.print(f"\n[dim]Outputs saved to: output/runs/{flow.run_id}/competition_research/[/dim]")
        console.print(f"  📄 competition_report.md  — full Markdown table & strategies")
        console.print(f"  📦 competition_data.json  — structured JSON\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Flow failed:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
