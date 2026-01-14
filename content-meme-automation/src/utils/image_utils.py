"""Image processing utilities."""
import os
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import colorsys


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return '#%02x%02x%02x' % rgb


def adjust_color_toward_target(
    source_color: Tuple[int, int, int],
    target_color: Tuple[int, int, int],
    intensity: float = 0.2
) -> Tuple[int, int, int]:
    """
    Adjust source color toward target color by intensity factor.
    
    Args:
        source_color: RGB tuple of source color
        target_color: RGB tuple of target color
        intensity: How much to shift (0.0 = no change, 1.0 = full target)
        
    Returns:
        Adjusted RGB tuple
    """
    adjusted = tuple(
        int(source_color[i] + (target_color[i] - source_color[i]) * intensity)
        for i in range(3)
    )
    return adjusted


def get_text_size(
    text: str,
    font: ImageFont.FreeTypeFont
) -> Tuple[int, int]:
    """
    Get text bounding box size.
    
    Args:
        text: Text to measure
        font: Font to use
        
    Returns:
        (width, height) tuple
    """
    # Create temporary image for measurement
    dummy_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


def get_optimal_font_size(
    text: str,
    font_path: str,
    max_width: int,
    max_height: int,
    min_size: int = 20,
    max_size: int = 100
) -> int:
    """
    Find optimal font size to fit text within bounds.
    
    Args:
        text: Text to fit
        font_path: Path to font file
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        min_size: Minimum font size
        max_size: Maximum font size
        
    Returns:
        Optimal font size
    """
    for size in range(max_size, min_size - 1, -1):
        try:
            font = ImageFont.truetype(font_path, size)
            width, height = get_text_size(text, font)
            
            if width <= max_width and height <= max_height:
                return size
        except:
            continue
            
    return min_size


def draw_outlined_text(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_color: Tuple[int, int, int],
    outline_color: Tuple[int, int, int],
    outline_width: int = 2
) -> None:
    """
    Draw text with outline/stroke.
    
    Args:
        draw: ImageDraw instance
        position: (x, y) position
        text: Text to draw
        font: Font to use
        fill_color: RGB tuple for text fill
        outline_color: RGB tuple for outline
        outline_width: Width of outline in pixels
    """
    x, y = position
    
    # Draw outline by drawing text multiple times with offset
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text(
                    (x + offset_x, y + offset_y),
                    text,
                    font=font,
                    fill=outline_color
                )
    
    # Draw main text on top
    draw.text(position, text, font=font, fill=fill_color)


def resize_image_maintain_aspect(
    image: Image.Image,
    target_width: Optional[int] = None,
    target_height: Optional[int] = None
) -> Image.Image:
    """
    Resize image while maintaining aspect ratio.
    
    Args:
        image: PIL Image
        target_width: Target width (provide one of width or height)
        target_height: Target height
        
    Returns:
        Resized image
    """
    original_width, original_height = image.size
    
    if target_width:
        ratio = target_width / original_width
        new_height = int(original_height * ratio)
        return image.resize((target_width, new_height), Image.Resampling.LANCZOS)
    elif target_height:
        ratio = target_height / original_height
        new_width = int(original_width * ratio)
        return image.resize((new_width, target_height), Image.Resampling.LANCZOS)
    else:
        return image
