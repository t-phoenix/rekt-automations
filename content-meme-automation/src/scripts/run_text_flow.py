#!/usr/bin/env python3
"""
Simple runner script for Text Content Generation Flow.

Usage:
    python run_text_flow.py
    python run_text_flow.py --override "platforms=twitter"
    python run_text_flow.py --override "tone=edgy,platforms=twitter,instagram"
"""
import sys
import click
from pathlib import Path
from rich.console import Console

# Add project root to path (parent of src/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.flows import TextContentFlow
from src.config import FlowConfig

console = Console()


@click.command()
@click.option(
    '--override',
    type=str,
    default=None,
    help='Configuration overrides (format: key1=value1,key2=value2)'
)
def main(override):
    """🚀 Run Text Content Generation Flow."""
    
    # Display banner
    console.print("\n[bold cyan]Text Content Generation Flow[/bold cyan]")
    console.print("[dim]Generate platform-specific content from trends[/dim]\n")
    
    try:
        # Create and run flow
        flow = TextContentFlow(override_string=override)
        output = flow.run()
        
        # Success
        console.print(f"\n[bold green]✓ Flow completed successfully![/bold green]")
        console.print(f"[bold]Run ID:[/bold] [cyan]{flow.run_id}[/cyan]")
        console.print(f"\n[dim]Outputs saved to: output/runs/{flow.run_id}/[/dim]")
        
        # Next steps
        console.print("\n[bold]Next Steps:[/bold]")
        console.print(f"  1. Review generated content in [cyan]output/runs/{flow.run_id}/content/[/cyan]")
        console.print(f"  2. Run meme generation: [cyan]python run_meme_flow.py --run-id {flow.run_id}[/cyan]")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Flow failed:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
