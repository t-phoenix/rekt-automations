#!/usr/bin/env python3
"""
Runner script for Twitter Engagement Flow (Flow 5).

Usage:
    python run_twitter_engagement.py
    python run_twitter_engagement.py --override "dry_run=true"
    python run_twitter_engagement.py --dry-run
"""
import sys
import click
from pathlib import Path
from rich.console import Console

# Add project root to path (parent of src/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.flows import TwitterEngagementFlow

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
    """🔥 Run Twitter Engagement Flow — Fetch top tweets, score them, and generate savage replies."""

    console.print("\n[bold cyan]Twitter Engagement Flow[/bold cyan]")
    console.print("[dim]Trend-surfing and engagement farming for Rekt CEO[/dim]\n")

    # Apply dry_run flag to override string
    if dry_run:
        override = ((override or '') + ',dry_run=true').lstrip(',')

    try:
        flow = TwitterEngagementFlow(override_string=override)
        output = flow.run()

        replies = output.get("suggested_replies", [])

        console.print(f"\n[bold green]✓ Flow completed successfully![/bold green]")
        console.print(f"[bold]Run ID:[/bold] [cyan]{flow.run_id}[/cyan]")
        
        if replies:
            console.print(f"\n[bold]Targets Drafted:[/bold] [white]{len(replies)}[/white]")
        
        console.print(f"\n[dim]Outputs saved to: output/runs/{flow.run_id}/twitter_engagement/[/dim]")
        console.print(f"  📄 engagement_report.md  — full Markdown table of tweets & replies")
        console.print(f"  📦 engagement_data.json  — structured JSON\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Flow failed:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
