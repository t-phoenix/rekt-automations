#!/usr/bin/env python3
"""
Main entry point for LangGraph Content & Meme Generation Automation.

Usage:
    # Run all flows (default)
    python main.py
    
    # Run specific flow
    python main.py --flow text
    python main.py --flow meme --run-id run_20260113_070000_a1b2
    python main.py --flow animation --run-id run_20260113_070000_a1b2
    
    # With overrides
    python main.py --flow text --override "platforms=twitter,tone=edgy"
    python main.py --override "skip_animation=true"
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
import click
from rich.console import Console
from rich.panel import Panel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.flows import TextContentFlow, MemeGenerationFlow, AnimationFlow

console = Console()


@click.command()
@click.option(
    '--flow',
    type=click.Choice(['text', 'meme', 'animation', 'all']),
    default='all',
    help='Which flow to run (default: all flows sequentially)'
)
@click.option(
    '--run-id',
    type=str,
    default=None,
    help='Existing run ID to continue (for meme/animation flows)'
)
@click.option(
    '--override',
    type=str,
    default=None,
    help='Configuration overrides (format: key1=value1,key2=value2)'
)
@click.option(
    '--skip-animation',
    is_flag=True,
    default=False,
    help='Skip animation generation'
)
def main(flow, run_id, override, skip_animation):
    """
    🚀 LangGraph Content & Meme Generation Automation
    
    Generate viral memes and platform-specific content automatically.
    """
    # Load environment variables
    load_dotenv()
    
    # Display banner
    console.print(Panel.fit(
        "[bold cyan]LangGraph Content & Meme Generator[/bold cyan]\n"
        "[dim]Automated viral content creation powered by AI[/dim]",
        border_style="cyan"
    ))
    
    # Apply skip_animation to override
    if skip_animation:
        if override:
            override += ",skip_animation=true"
        else:
            override = "skip_animation=true"
    
    try:
        if flow == 'text':
            _run_text_flow(override)
        elif flow == 'meme':
            _run_meme_flow(run_id, override)
        elif flow == 'animation':
            _run_animation_flow(run_id, override)
        else:  # all
            _run_all_flows(override)
            
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Workflow interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]✗ Workflow failed:[/bold red] {e}")
        import traceback
        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


def _run_text_flow(override: str = None):
    """Run text content generation flow."""
    console.print("\n[bold]Running: Text Content Generation Flow[/bold]\n")
    
    flow = TextContentFlow(override_string=override)
    flow.run()
    
    console.print(f"\n[green]✓ Text flow completed[/green] (Run ID: {flow.run_id})")
    console.print(f"[dim]Next: python main.py --flow meme --run-id {flow.run_id}[/dim]\n")


def _run_meme_flow(run_id: str = None, override: str = None):
    """Run meme generation flow."""
    console.print("\n[bold]Running: Meme Generation Flow[/bold]\n")
    
    if not run_id:
        console.print("[yellow]⚠️  No run ID provided - starting new run[/yellow]\n")
    
    flow = MemeGenerationFlow(run_id=run_id, override_string=override)
    flow.run()
    
    console.print(f"\n[green]✓ Meme flow completed[/green]")
    console.print(f"[dim]Next: python main.py --flow animation --run-id {flow.run_id}[/dim]\n")


def _run_animation_flow(run_id: str = None, override: str = None):
    """Run animation flow."""
    if not run_id:
        console.print("\n[bold red]✗ Error:[/bold red] --run-id required for animation flow")
        console.print("[dim]Run meme flow first to generate a meme to animate[/dim]\n")
        sys.exit(1)
    
    console.print("\n[bold]Running: Animation Flow[/bold]\n")
    
    flow = AnimationFlow(run_id=run_id, override_string=override)
    output = flow.run()
    
    if not output.get("skipped"):
        console.print(f"\n[green]✓ Animation flow completed[/green]\n")
    else:
        console.print(f"\n[yellow]⚠️  Animation skipped[/yellow]\n")


def _run_all_flows(override: str = None):
    """Run all flows sequentially."""
    console.print("\n[bold]Running: ALL FLOWS (Text → Meme → Animation)[/bold]\n")
    console.print("=" * 60)
    
    # Flow 1: Text
    console.print("\n[bold]Step 1/3: Text Content Generation[/bold]")
    text_flow = TextContentFlow(override_string=override)
    text_flow.run()
    run_id = text_flow.run_id
    console.print(f"\n[green]✓ Text flow completed[/green]")
    
    # Flow 2: Meme
    console.print("\n[bold]Step 2/3: Meme Generation[/bold]")
    meme_flow = MemeGenerationFlow(run_id=run_id, override_string=override)
    meme_flow.run()
    console.print(f"\n[green]✓ Meme flow completed[/green]")
    
    # Flow 3: Animation
    skip_animation = override and "skip_animation=true" in override
    if not skip_animation:
        console.print("\n[bold]Step 3/3: Animation[/bold]")
        animation_flow = AnimationFlow(run_id=run_id, override_string=override)
        animation_output = animation_flow.run()
        
        if not animation_output.get("skipped"):
            console.print(f"\n[green]✓ Animation flow completed[/green]")
    else:
        console.print("\n[yellow]⚠️  Skipping animation[/yellow]")
    
    # Success
    console.print("\n" + "=" * 60)
    console.print("[bold green]🎉 ALL FLOWS COMPLETED![/bold green]")
    console.print("=" * 60)
    console.print(f"\n[bold]Run ID:[/bold] [cyan]{run_id}[/cyan]")
    console.print(f"[bold]Outputs:[/bold] [cyan]output/runs/{run_id}/[/cyan]\n")


if __name__ == "__main__":
    main()
