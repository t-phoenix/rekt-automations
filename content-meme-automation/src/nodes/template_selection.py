"""Node 5: Meme Template Selection."""
import os
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image

from ..graph.state import GraphState, TemplateSelection


def find_all_templates(templates_path: str) -> Dict[str, List[str]]:
    """
    Recursively find all template images organized by category.
    
    Args:
        templates_path: Path to rekt_meme_templates directory
        
    Returns:
        Dict mapping category names to lists of image paths
    """
    templates_dir = Path(templates_path)
    
    if not templates_dir.exists():
        raise FileNotFoundError(f"Templates directory not found: {templates_path}")
    
    templates_by_category = {}
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    
    # Find all subdirectories (categories)
    for category_dir in templates_dir.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            templates = []
            
            # Find all images in this category
            for img_file in category_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                    templates.append(str(img_file))
            
            if templates:
                templates_by_category[category_name] = templates
    
    return templates_by_category


def get_image_metadata(image_path: str) -> Dict[str, Any]:
    """
    Get metadata from image file.
    
    Args:
        image_path: Path to image
        
    Returns:
        Dict with dimensions and text zones
    """
    img = Image.open(image_path)
    width, height = img.size
    
    # Define standard text zones for memes
    # Top text: centered at top 15% of image
    # Bottom text: centered at bottom 15% of image
    text_zones = {
        "top": {
            "x": width // 2,
            "y": int(height * 0.1),
            "width": int(width * 0.9),
            "height": int(height * 0.15)
        },
        "bottom": {
            "x": width // 2,
            "y": int(height * 0.85),
            "width": int(width * 0.9),
            "height": int(height * 0.15)
        }
    }
    
    return {
        "dimensions": {"width": width, "height": height},
        "text_zones": text_zones
    }


def select_template_contextual(
    templates_by_category: Dict[str, List[str]],
    suggested_categories: List[str]
) -> Tuple[str, str]:
    """
    Select template based on suggested categories.
    
    Args:
        templates_by_category: Templates organized by category
        suggested_categories: Suggested categories from sentiment analysis
        
    Returns:
        (template_path, category_name) tuple
    """
    # Try suggested categories first
    for category in suggested_categories:
        if category in templates_by_category:
            templates = templates_by_category[category]
            selected = random.choice(templates)
            return selected, category
    
    # Fallback: random category
    category = random.choice(list(templates_by_category.keys()))
    selected = random.choice(templates_by_category[category])
    return selected, category


def template_selection_node(state: GraphState) -> GraphState:
    """
    Node 5: Select optimal meme template from repository.
    
    This node:
    - Scans meme_templates directory for all images
    - Filters by suggested categories from sentiment analysis
    - Selects template (contextual or random)
    - Extracts template metadata (dimensions, text zones)
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with template_selection populated
    """
    print("\n🖼️ NODE 5: Meme Template Selection")
    print("=" * 50)
    
    templates_path = state["config"].get(
        "meme_templates_path",
        os.getenv("MEME_TEMPLATES_PATH", "./rekt_meme_templates")
    )
    
    content_analysis = state.get("content_analysis", {})
    suggested_categories = content_analysis.get("suggested_template_categories", [])
    
    print(f"📁 Scanning templates from: {templates_path}")
    templates_by_category = find_all_templates(templates_path)
    
    total_templates = sum(len(templates) for templates in templates_by_category.values())
    print(f"✓ Found {total_templates} templates in {len(templates_by_category)} categories")
    print(f"  Categories: {', '.join(templates_by_category.keys())}")
    
    print(f"🎯 Suggested categories: {', '.join(suggested_categories)}")
    
    # Select template
    template_path, category = select_template_contextual(
        templates_by_category,
        suggested_categories
    )
    
    print(f"✓ Selected: {Path(template_path).name}")
    print(f"  Category: {category}")
    
    # Get metadata
    metadata = get_image_metadata(template_path)
    filename = Path(template_path).name
    
    template_selection = TemplateSelection(
        template_image_path=template_path,
        template_metadata={
            "category": category,
            "filename": filename,
            **metadata
        }
    )
    
    state["template_selection"] = template_selection
    return state
