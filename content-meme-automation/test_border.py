import sys
from pathlib import Path
sys.path.append("/Users/abhinilagarwal/Desktop/rekt-automations/content-meme-automation")

from PIL import Image
from src.nodes.meme_rendering import apply_rekt_border

# Create a dummy image
img = Image.new('RGB', (400, 300), color=(100, 100, 200))

# Mock brand config
brand_config = {
    "primary_color": "#ff0033",
    "font_family": "Impact"
}

try:
    bordered_img = apply_rekt_border(img, brand_config)
    bordered_img.save("test_bordered.png")
    print("Successfully applied border. Image saved to test_bordered.png")
    print(f"Original size: {img.size}")
    print(f"Bordered size: {bordered_img.size}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error applying border: {e}")
