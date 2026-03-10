#!/usr/bin/env python3
"""
Runner script for KOL Research Flow (Flow 7).

Usage:
    python run_kol_research.py
    python run_kol_research.py --override "follower_range=[50000, 100000]"
"""
import sys
import click
from pathlib import Path
from rich.console import Console

# Add project root to path (parent of src/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.flows import KOLResearchFlow

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
    """🎯 Run KOL Research Flow."""
    console.print("\n[bold cyan]KOL Research Flow[/bold cyan]")
    console.print("[dim]Discovering target KOLs, scoring alignment using RAG, and brainstorming custom engagement strategies[/dim]\n")

    if dry_run:
        override = ((override or '') + ',dry_run=true').lstrip(',')

    try:
        flow = KOLResearchFlow(override_string=override)
        output = flow.run()

        console.print(f"\n[bold green]✓ KOL Research Flow completed successfully![/bold green]")
        console.print(f"[bold]Run ID:[/bold] [cyan]{flow.run_id}[/cyan]")
        console.print(f"\n[dim]Outputs saved to: output/runs/{flow.run_id}/kol_research/[/dim]")
        console.print(f"  📄 kol_report.md  — top targets and exact engagement scripts")
        console.print(f"  📦 kol_data.json  — structured JSON\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Flow failed:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
