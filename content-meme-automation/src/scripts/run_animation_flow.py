#!/usr/bin/env python3
"""
Simple runner script for Animation Flow.

Usage:
    python run_animation_flow.py --run-id run_20260113_070000_a1b2
    python run_animation_flow.py --run-id run_20260113_070000_a1b2 --override "animation_style=bounce"
"""
import sys
import click
from pathlib import Path
from rich.console import Console

# Add project root to path (parent of src/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.flows import AnimationFlow
from src.config import FlowConfig

console = Console()


@click.command()
@click.option(
    '--run-id',
    type=str,
    required=True,
    help='Run ID from previous meme flow (required)'
)
@click.option(
    '--override',
    type=str,
    default=None,
    help='Configuration overrides (format: key1=value1,key2=value2)'
)
def main(run_id, override):
    """🚀 Run Animation Flow."""
    
    # Display banner
    console.print("\n[bold cyan]Animation Flow[/bold cyan]")
    console.print("[dim]Generate animated videos from memes[/dim]\n")
    
    console.print(f"[bold]Continuing from run:[/bold] [cyan]{run_id}[/cyan]\n")
    
    try:
        # Create and run flow
        flow = AnimationFlow(run_id=run_id, override_string=override)
        output = flow.run()
        
        if output.get("skipped"):
            console.print("\n[yellow]⚠️  Animation skipped (disabled in config)[/yellow]")
            return
        
        # Success
        console.print(f"\n[bold green]✓ Flow completed successfully![/bold green]")
        console.print(f"[bold]Run ID:[/bold] [cyan]{flow.run_id}[/cyan]")
        console.print(f"\n[dim]Outputs saved to: output/runs/{flow.run_id}/[/dim]")
        
        # Summary
        console.print("\n[bold]All Done! 🎉[/bold]")
        console.print(f"  View animated video in [cyan]output/runs/{flow.run_id}/video/[/cyan]")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Flow failed:[/bold red] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
