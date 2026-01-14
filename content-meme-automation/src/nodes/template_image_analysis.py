"""Node 5.5: Template Image Analysis (NEW)."""
import json
import base64
from pathlib import Path
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from ..utils import get_llm
from ..graph.state import GraphState, ImageAnalysis


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode image to base64 for multimodal LLM.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Base64 encoded image string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_template_image(template_path: str) -> ImageAnalysis:
    """
    Analyze meme template image to understand visual context.
    
    Args:
        template_path: Path to selected template image
        
    Returns:
        ImageAnalysis with visual understanding
    """
    llm = get_llm("analysis")  # Will use Gemini vision model
    
    # Encode image
    base64_image = encode_image_to_base64(template_path)
    image_url = f"data:image/png;base64,{base64_image}"
    
    # Create vision prompt
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": """You are a meme expert analyzing this template image for text generation.

Analyze this meme template and provide:

1. **image_description**: Detailed 2-3 sentence description of what's in the image (people, objects, expressions, setting)

2. **visual_elements**: Array of key visual elements (e.g., ["person pointing", "expression: excited", "background: office", "gesture: thumbs up"])

3. **emotional_context**: The primary emotion this image naturally conveys (e.g., "triumph", "confusion", "disappointment", "excitement", "suspicion", "pride")

4. **meme_format**: The recognized meme format if known (e.g., "success_kid", "drake_reaction", "distracted_boyfriend", "expanding_brain", "two_buttons", "running_away", "generic_reaction") or "custom" if not recognized

5. **text_placement_suitability**: Object with:
   - top: "good" | "moderate" | "poor" (is top area good for text?)
   - bottom: "good" | "moderate" | "poor" (is bottom area good for text?)

6. **suggested_narrative_structure**: How to structure meme text (e.g., "setup/punchline", "before/after", "comparison", "reaction", "escalation", "ironic_contrast")

7. **cultural_references**: Array of cultural/meme references this image evokes (e.g., ["success culture", "crypto wins", "office work"])

8. **humor_opportunities**: Array of 3-5 specific humor angles this image enables (e.g., ["contrast between effort and reward", "unexpected success", "overcoming obstacles"])

Return ONLY a valid JSON object with these exact keys. No markdown, no explanation."""
            },
            {
                "type": "image_url",
                "image_url": {"url": image_url}
            }
        ]
    )
    
    response = llm.invoke([message])
    
    # Parse JSON response
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    analysis_dict = json.loads(content)
    
    return ImageAnalysis(**analysis_dict)


def template_image_analysis_node(state: GraphState) -> GraphState:
    """
    Node 5.5: Analyze selected template image before text generation.
    
    This NEW node:
    - Receives selected template from Node 5
    - Uses multimodal LLM (Gemini Vision) to understand image
    - Extracts visual context, emotion, meme format
    - Identifies humor opportunities
    - Provides analysis to Node 7 for image-aware text generation
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with image_analysis populated
    """
    print("\n🔍 NODE 5.5: Template Image Analysis")
    print("=" * 50)
    
    template_path = state.get("template_selection", {}).get("template_image_path")
    
    if not template_path:
        raise ValueError("No template selected for analysis")
    
    print(f"📸 Analyzing image: {Path(template_path).name}")
    
    # Analyze image
    analysis = analyze_template_image(template_path)
    
    print(f"✓ Image Analysis Complete:")
    print(f"  - Format: {analysis['meme_format']}")
    print(f"  - Emotion: {analysis['emotional_context']}")
    print(f"  - Narrative: {analysis['suggested_narrative_structure']}")
    print(f"  - Humor Opportunities: {len(analysis['humor_opportunities'])}")
    
    state["image_analysis"] = analysis
    return state
