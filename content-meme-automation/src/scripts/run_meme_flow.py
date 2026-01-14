#!/usr/bin/env python3
"""
Simple runner script for Meme Generation Flow.

Usage:
    python run_meme_flow.py --run-id run_20260113_070000_a1b2
    python run_meme_flow.py --run-id run_20260113_070000_a1b2 --override "style=bold"
    python run_meme_flow.py (creates new run without text flow data)
"""
import sys
import click
from pathlib import Path
from rich.console import Console

# Add project root to path (parent of src/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.flows import MemeGenerationFlow
from src.config import FlowConfig

console = Console()


@click.command()
@click.option(
    '--run-id',
    type=str,
    default=None,
    help='Run ID from previous text flow (optional)'
)
@click.option(
    '--override',
    type=str,
    default=None,
    help='Configuration overrides (format: key1=value1,key2=value2)'
)
def main(run_id, override):
    """🚀 Run Meme Generation Flow."""
    
    # Display banner
    console.print("\n[bold cyan]Meme Generation Flow[/bold cyan]")
    console.print("[dim]Generate branded memes from content[/dim]\n")
    
    if run_id:
        console.print(f"[bold]Continuing from run:[/bold] [cyan]{run_id}[/cyan]\n")
    else:
        console.print("[yellow]⚠️  No run ID provided - starting new run without text flow data[/yellow]\n")
    
    try:
        # Create and run flow
        flow = MemeGenerationFlow(run_id=run_id, override_string=override)
        output = flow.run()
        
        # Success
        console.print(f"\n[bold green]✓ Flow completed successfully![/bold green]")
        console.print(f"[bold]Run ID:[/bold] [cyan]{flow.run_id}[/cyan]")
        console.print(f"\n[dim]Outputs saved to: output/runs/{flow.run_id}/[/dim]")
        
        # Next steps
        console.print("\n[bold]Next Steps:[/bold]")
        console.print(f"  1. View generated meme in [cyan]output/runs/{flow.run_id}/memes/[/cyan]")
        console.print(f"  2. Run animation: [cyan]python run_animation_flow.py --run-id {flow.run_id}[/cyan]")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Flow failed:[/bold red] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
