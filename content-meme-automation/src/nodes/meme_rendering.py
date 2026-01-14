"""Node 8: Final Meme Rendering."""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont

from ..utils import hex_to_rgb, get_optimal_font_size, draw_outlined_text, get_text_size
from ..graph.state import GraphState, FinalMeme


def load_brand_config(brand_identity_path: str) -> Dict[str, Any]:
    """Load brand configuration."""
    config_path = Path(brand_identity_path) / "brand_config.json"
    return json.loads(config_path.read_text())


def get_font_path(font_family: str) -> str:
    """
    Get font file path. Falls back to system Impact font.
    
    Args:
        font_family: Font family name
        
    Returns:
        Path to font file
    """
    # Try common system font paths
    font_paths = [
        f"/System/Library/Fonts/Supplemental/{font_family}.ttc",
        f"/Library/Fonts/{font_family}.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Impact.ttf",
    ]
    
    for path in font_paths:
        if Path(path).exists():
            return path
    
    # Final fallback: use default
    try:
        return ImageFont.truetype("Impact", 40).path
    except:
        # Use default PIL font
        return None


def render_meme_with_text(
    image_path: str,
    top_text: str,
    bottom_text: str,
    brand_config: Dict[str, Any],
    template_metadata: Dict[str, Any]
) -> Image.Image:
    """
    Render final meme with text overlay.
    
    Args:
        image_path: Path to branded template
        top_text: Top meme text
        bottom_text: Bottom meme text
        brand_config: Brand configuration
        template_metadata: Template metadata with text zones
        
    Returns:
        Final meme image
    """
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    width, height = image.size
    text_zones = template_metadata.get("text_zones", {})
    
    # Get font
    font_family = brand_config.get("font_family", "Impact")
    font_path = get_font_path(font_family)
    
    # Text style rules
    text_rules = brand_config.get("text_style_rules", {})
    stroke_color = text_rules.get("stroke_color", "#000000")
    stroke_width = text_rules.get("stroke_width", 2)
    
    # Process text (uppercase if configured)
    if text_rules.get("uppercase", True):
        top_text = top_text.upper()
        bottom_text = bottom_text.upper()
    
    # Calculate optimal font sizes
    top_zone = text_zones.get("top", {})
    bottom_zone = text_zones.get("bottom", {})
    
    max_width = int(width * 0.9)
    max_height = int(height * 0.12)
    
    if font_path:
        top_font_size = get_optimal_font_size(
            top_text, font_path, max_width, max_height,
            min_size=30, max_size=80
        )
        bottom_font_size = get_optimal_font_size(
            bottom_text, font_path, max_width, max_height,
            min_size=30, max_size=80
        )
        
        top_font = ImageFont.truetype(font_path, top_font_size)
        bottom_font = ImageFont.truetype(font_path, bottom_font_size)
    else:
        # Fallback to default font
        top_font = ImageFont.load_default()
        bottom_font = ImageFont.load_default()
    
    # Draw TOP TEXT
    top_text_width, top_text_height = get_text_size(top_text, top_font)
    top_x = (width - top_text_width) // 2
    top_y = int(height * 0.05)
    
    draw_outlined_text(
        draw,
        (top_x, top_y),
        top_text,
        top_font,
        fill_color=(255, 255, 255),
        outline_color=hex_to_rgb(stroke_color),
        outline_width=stroke_width
    )
    
    # Draw BOTTOM TEXT
    bottom_text_width, bottom_text_height = get_text_size(bottom_text, bottom_font)
    bottom_x = (width - bottom_text_width) // 2
    bottom_y = height - bottom_text_height - int(height * 0.05)
    
    draw_outlined_text(
        draw,
        (bottom_x, bottom_y),
        bottom_text,
        bottom_font,
        fill_color=(255, 255, 255),
        outline_color=hex_to_rgb(stroke_color),
        outline_width=stroke_width
    )
    
    return image


def meme_rendering_node(state: GraphState) -> GraphState:
    """
    Node 8: Render final meme with text overlay.
    
    This node:
    - Loads branded template
    - Applies brand font rules
    - Renders top and bottom text with proper sizing
    - Adds text outline/stroke
    - Saves final meme image
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with final_meme populated
    """
    print("\n🎬 NODE 8: Final Meme Rendering")
    print("=" * 50)
    
    brand_identity_path = state["config"].get(
        "brand_identity_path",
        os.getenv("BRAND_IDENTITY_PATH", "./brand_identity")
    )
    
    branded_template_path = state.get("branded_template", {}).get("branded_template_image_path")
    meme_text = state.get("meme_text", {})
    template_metadata = state.get("template_selection", {}).get("template_metadata", {})
    
    if not branded_template_path:
        raise ValueError("No branded template found")
    
    print("🎨 Loading brand config...")
    brand_config = load_brand_config(brand_identity_path)
    
    top_text = meme_text.get("top_text", "")
    bottom_text = meme_text.get("bottom_text", "")
    
    print(f"📝 Rendering text:")
    print(f"   TOP: {top_text}")
    print(f"   BOTTOM: {bottom_text}")
    
    # Render meme
    final_image = render_meme_with_text(
        branded_template_path,
        top_text,
        bottom_text,
        brand_config,
        template_metadata
    )
    
    # Save final meme
    output_dir = Path(state["config"].get("output_path", "./output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = output_dir / f"final_meme_{timestamp}.png"
    final_image.save(final_path, quality=95)
    
    print(f"✓ Saved final meme: {final_path.name}")
    print(f"  Size: {final_image.size}")
    
    final_meme = FinalMeme(
        final_meme_image_path=str(final_path),
        rendering_metadata={
            "font_used": brand_config.get("font_family", "Impact"),
            "text_positions": {"top": "center_top", "bottom": "center_bottom"},
            "image_size": {"width": final_image.size[0], "height": final_image.size[1]}
        }
    )
    
    state["final_meme"] = final_meme
    return state
