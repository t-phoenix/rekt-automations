#!/usr/bin/env python3
"""
Simple runner script to run ALL flows sequentially.

Usage:
    python run_all_flows.py
    python run_all_flows.py --override "platforms=twitter,tone=edgy"
    python run_all_flows.py --skip-animation
"""
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add project root to path (parent of src/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.flows import TextContentFlow, MemeGenerationFlow, AnimationFlow
from src.config import FlowConfig

console = Console()


@click.command()
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
def main(override, skip_animation):
    """🚀 Run ALL flows sequentially (Text → Meme → Animation)."""
    
    # Display banner
    console.print(Panel.fit(
        "[bold cyan]Complete Automation Flow[/bold cyan]\n"
        "[dim]Text Generation → Meme Generation → Animation[/dim]",
        border_style="cyan"
    ))
    
    # Apply skip_animation to override if needed
    if skip_animation:
        if override:
            override += ",skip_animation=true"
        else:
            override = "skip_animation=true"
    
    run_id = None
    
    try:
        # === FLOW 1: Text Content Generation ===
        console.print("\n[bold]Step 1/3: Text Content Generation[/bold]")
        console.print("-" * 60)
        
        text_flow = TextContentFlow(override_string=override)
        text_flow.run()
        run_id = text_flow.run_id
        
        console.print(f"\n[green]✓ Text flow completed[/green] (Run ID: {run_id})")
        
        # === FLOW 2: Meme Generation ===
        console.print("\n[bold]Step 2/3: Meme Generation[/bold]")
        console.print("-" * 60)
        
        meme_flow = MemeGenerationFlow(run_id=run_id, override_string=override)
        meme_flow.run()
        
        console.print(f"\n[green]✓ Meme flow completed[/green]")
        
        # === FLOW 3: Animation ===
        if not skip_animation:
            console.print("\n[bold]Step 3/3: Animation[/bold]")
            console.print("-" * 60)
            
            animation_flow = AnimationFlow(run_id=run_id, override_string=override)
            animation_output = animation_flow.run()
            
            if not animation_output.get("skipped"):
                console.print(f"\n[green]✓ Animation flow completed[/green]")
            else:
                console.print(f"\n[yellow]⚠️  Animation skipped[/yellow]")
        else:
            console.print("\n[yellow]⚠️  Skipping animation (--skip-animation flag)[/yellow]")
        
        # === SUCCESS ===
        console.print("\n" + "=" * 60)
        console.print("[bold green]🎉 ALL FLOWS COMPLETED SUCCESSFULLY![/bold green]")
        console.print("=" * 60)
        
        console.print(f"\n[bold]Run ID:[/bold] [cyan]{run_id}[/cyan]")
        console.print(f"\n[bold]Generated Assets:[/bold]")
        console.print(f"  📄 Content: [cyan]output/runs/{run_id}/content/[/cyan]")
        console.print(f"  🖼️  Meme: [cyan]output/runs/{run_id}/memes/[/cyan]")
        if not skip_animation:
            console.print(f"  🎬 Video: [cyan]output/runs/{run_id}/video/[/cyan]")
        
        console.print(f"\n[dim]All outputs saved to: output/runs/{run_id}/[/dim]\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Flow interrupted by user[/yellow]")
        if run_id:
            console.print(f"[dim]Partial outputs saved to: output/runs/{run_id}/[/dim]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]✗ Flow failed:[/bold red] {e}")
        if run_id:
            console.print(f"[dim]Partial outputs saved to: output/runs/{run_id}/[/dim]")
        import traceback
        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
