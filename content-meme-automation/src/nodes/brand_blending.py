"""Node 6: Brand Identity Blending."""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageEnhance
# from rembg import remove  # Disabled due to Python 3.14 compatibility issues

from ..utils import hex_to_rgb, adjust_color_toward_target, resize_image_maintain_aspect
from ..graph.state import GraphState, BrandedTemplate


def load_brand_config(brand_identity_path: str) -> Dict[str, Any]:
    """Load brand configuration from JSON file."""
    config_path = Path(brand_identity_path) / "brand_config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Brand config not found: {config_path}")
    
    return json.loads(config_path.read_text())


def apply_color_adjustment(
    image: Image.Image,
    primary_color: str,
    secondary_color: str,
    intensity: float = 0.15
) -> Image.Image:
    """
    Subtly adjust image colors toward brand colors.
    
    Args:
        image: PIL Image
        primary_color: Primary brand color hex
        secondary_color: Secondary brand color hex
        intensity: How much to shift colors (0.0-1.0)
        
    Returns:
        Color-adjusted image
    """
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    pixels = image.load()
    width, height = image.size
    
    primary_rgb = hex_to_rgb(primary_color)
    
    # Adjust pixels (sample every 2nd pixel for performance)
    for x in range(0, width, 2):
        for y in range(0, height, 2):
            original = pixels[x, y]
            adjusted = adjust_color_toward_target(original, primary_rgb, intensity)
            pixels[x, y] = adjusted
            
            # Fill neighbor pixels
            if x + 1 < width:
                pixels[x + 1, y] = adjusted
            if y + 1 < height:
                pixels[x, y + 1] = adjusted
    
    return image


def add_logo_watermark(
    image: Image.Image,
    logo_path: str,
    position: str = "bottom_right",
    opacity: float = 0.7
) -> Image.Image:
    """
    Add subtle logo watermark to image.
    
    Args:
        image: Base image
        logo_path: Path to logo file
        position: "bottom_right" or "top_left"
        opacity: Logo opacity (0.0-1.0)
        
    Returns:
        Image with logo
    """
    if not Path(logo_path).exists():
        print(f"⚠ Logo not found: {logo_path}")
        return image
    
    logo = Image.open(logo_path).convert("RGBA")
    
    # Resize logo to 8-10% of image width
    target_width = int(image.width * 0.08)
    logo = resize_image_maintain_aspect(logo, target_width=target_width)
    
    # Adjust opacity
    logo_with_opacity = logo.copy()
    alpha = logo_with_opacity.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    logo_with_opacity.putalpha(alpha)
    
    # Calculate position
    margin = 20
    if position == "bottom_right":
        x = image.width - logo.width - margin
        y = image.height - logo.height - margin
    else:  # top_left
        x = margin
        y = margin
    
    # Paste logo
    image.paste(logo_with_opacity, (x, y), logo_with_opacity)
    
    return image


def add_colored_border(
    image: Image.Image,
    color: str,
    width: int = 3
) -> Image.Image:
    """
    Add subtle colored border.
    
    Args:
        image: Base image
        color: Border color hex
        width: Border width in pixels
        
    Returns:
        Image with border
    """
    draw = ImageDraw.Draw(image)
    rgb_color = hex_to_rgb(color)
    
    # Draw rectangle border
    draw.rectangle(
        [(0, 0), (image.width - 1, image.height - 1)],
        outline=rgb_color,
        width=width
    )
    
    return image


def brand_blending_node(state: GraphState) -> GraphState:
    """
    Node 6: Apply subtle brand customization to template.
    
    This node:
    - Loads brand configuration
    - Applies subtle color adjustments
    - Adds logo watermark (if configured)
    - Adds colored border
    - Preserves meme template feel (80% original, 20% brand)
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with branded_template populated
    """
    print("\n🎨 NODE 6: Brand Identity Blending")
    print("=" * 50)
    
    brand_identity_path = state["config"].get(
        "brand_identity_path",
        os.getenv("BRAND_IDENTITY_PATH", "./brand_identity")
    )
    
    template_path = state.get("template_selection", {}).get("template_image_path")
    
    if not template_path:
        raise ValueError("No template selected")
    
    print(f"🎨 Loading brand config from: {brand_identity_path}")
    brand_config = load_brand_config(brand_identity_path)
    
    print(f"✓ Brand: {brand_config['brand_name']}")
    print(f"✓ Primary Color: {brand_config['primary_color']}")
    print(f"✓ Visual Tone: {brand_config['visual_tone']}")
    
    # Load template image
    image = Image.open(template_path).convert("RGB")
    print(f"📐 Template size: {image.size}")
    
    modifications_applied = {}
    
    # Apply color adjustment (minimal intensity to preserve template)
    print("🌈 Applying color adjustment...")
    image = apply_color_adjustment(
        image,
        brand_config["primary_color"],
        brand_config["secondary_color"],
        intensity=0.1  # Very subtle
    )
    modifications_applied["color_adjustment"] = True
    
    # Add logo if configured
    logo_path_relative = brand_config.get("logo_path")
    if logo_path_relative:
        logo_path_full = Path(brand_identity_path) / logo_path_relative
        if logo_path_full.exists():
            print("🏷️ Adding logo watermark...")
            image = add_logo_watermark(image, str(logo_path_full), opacity=0.6)
            modifications_applied["logo_added"] = True
        else:
            modifications_applied["logo_added"] = False
    else:
        modifications_applied["logo_added"] = False
    
    # Add border
    print("🖼️ Adding brand border...")
    image = add_colored_border(image, brand_config["primary_color"], width=3)
    modifications_applied["border_added"] = True
    
    # Save branded template
    output_dir = Path(state["config"].get("output_path", "./output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    branded_path = output_dir / f"branded_template_{timestamp}.png"
    image.save(branded_path)
    
    print(f"✓ Saved branded template: {branded_path.name}")
    
    branded_template = BrandedTemplate(
        branded_template_image_path=str(branded_path),
        modifications_applied=modifications_applied,
        preview_metadata={
            "original_path": template_path,
            "changes_summary": f"Color adjustment, border, {'logo' if modifications_applied['logo_added'] else 'no logo'}"
        }
    )
    
    state["branded_template"] = branded_template
    return state
