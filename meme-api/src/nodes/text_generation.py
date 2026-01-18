"""Node 7: Meme Text Generation (Image-Aware)."""
import json
import random
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate

from ..utils import get_llm
from ..graph.state import GraphState, MemeText


def generate_meme_text(
    content_analysis: Dict,
    image_analysis: Dict,
    previous_angles: list = None
) -> Dict:
    """
    Generate 10 diverse meme text options (top and bottom) - IMAGE-AWARE VERSION.
    
    Args:
        content_analysis: Sentiment and humor analysis from raw input
        image_analysis: Visual analysis from Node 2
        previous_angles: Previously used angles to avoid repetition
        
    Returns:
        Dict with list of 10 MemeTextOption objects
    """
    llm = get_llm("content_generation")
    
    # Select 10 different humor patterns for maximum diversity
    humor_patterns = [
        "wordplay",
        "subversion_of_expectations",
        "cultural_references",
        "absurdist",
        "self_deprecating",
        "hyperbole",
        "callback_humor",
        "ironic_contrast",
        "relatable_struggle",
        "triumphant_flex"
    ]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a VIRAL meme creator with deep understanding of internet culture and human humor.

## YOUR MISSION
Generate 10 DIVERSE meme text options that:
1. **FIT THE IMAGE PERFECTLY** - The text must make sense with the visual
2. **MATCH USER INPUT** - Align with the user's topic/sentiment
3. **USE DIVERSE HUMOR** - Each option should use a different humor approach
4. **AVOID REPETITION** - Don't reuse these angles: {previous_angles}

## IMAGE CONTEXT (CRITICAL - READ CAREFULLY)
Image Description: {image_description}
Visual Elements: {visual_elements}
Emotional Context: {emotional_context}
Meme Format: {meme_format}
Narrative Structure: {narrative_structure}
Humor Opportunities: {humor_opportunities}

## USER INPUT CONTEXT
User's Topic/Content: {user_content}
Meme Angle: {meme_angle}
Dominant Emotion: {dominant_emotion}
Humor Type: {humor_type}

## TEXT GENERATION RULES
1. Generate EXACTLY 10 different options
2. Each option uses a DIFFERENT humor pattern from: {humor_patterns}
3. TOP TEXT: Setup that matches the image's visual context
4. BOTTOM TEXT: Punchline that complements the setup AND the image
5. Each line UNDER 40 characters
6. Use the image's natural emotion and narrative structure
7. Don't just describe the image - USE it for the joke
8. Make it culturally current and relatable
9. ALL CAPS or Mixed Case (your choice based on impact)
10. Platform-safe (no offensive content)

## OUTPUT FORMAT
Return ONLY a valid JSON object with:
{{
  "options": [
    {{
      "top_text": "string",
      "bottom_text": "string",
      "virality_score": float (0-1),
      "image_coherence_score": float (0-1 - how well text matches image),
      "humor_pattern_used": "string",
      "character_counts": {{"top": int, "bottom": int}}
    }},
    ... (10 total options)
  ]
}}

Make each option UNIQUE and VIRAL! 🔥"""),
        ("user", """Generate 10 diverse meme text options as JSON.""")
    ])
    
    # Prepare previous angles string
    prev_angles_str = ", ".join(previous_angles[-5:]) if previous_angles else "None yet"
    
    chain = prompt | llm
    response = chain.invoke({
        # Image context
        "image_description": image_analysis.get("image_description", ""),
        "visual_elements": ", ".join(image_analysis.get("visual_elements", [])),
        "emotional_context": image_analysis.get("emotional_context", ""),
        "meme_format": image_analysis.get("meme_format", ""),
        "narrative_structure": image_analysis.get("suggested_narrative_structure", ""),
        "humor_opportunities": ", ".join(image_analysis.get("humor_opportunities", [])),
        
        # User input context (NO BRAND CONTEXT)
        "user_content": content_analysis.get("meme_angle", ""),
        "meme_angle": content_analysis.get("meme_angle", ""),
        "dominant_emotion": content_analysis.get("dominant_emotion", ""),
        "humor_type": content_analysis.get("humor_type", ""),
        
        # Variation mechanisms
        "humor_patterns": ", ".join(humor_patterns),
        "previous_angles": prev_angles_str
    })
    
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    meme_data = json.loads(content)
    
    return meme_data


def text_generation_node(state: GraphState) -> GraphState:
    """
    Node 3: Generate 10 diverse viral meme text options.
    
    This node:
    - Generates 10 different TOP/BOTTOM TEXT options
    - Uses diverse humor patterns for variety
    - Focuses purely on user input + image analysis (NO brand context)
    - Each option scored for virality and image coherence
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with meme_text populated (containing 10 options)
    """
    print("\n💬 NODE 3: Meme Text Generation (10 Options)")
    print("=" * 50)
    
    content_analysis = state.get("content_analysis", {})
    image_analysis = state.get("image_analysis", {})
    previous_angles = state.get("previous_meme_angles", [])
    
    if not image_analysis:
        raise ValueError("No image analysis found - Node 2 must run before Node 3")
    
    print(f"🎨 Image Format: {image_analysis.get('meme_format', 'Unknown')}")
    print("✍️  Generating 10 diverse meme text options...")
    meme_text_data = generate_meme_text(content_analysis, image_analysis, previous_angles)
    
    options = meme_text_data.get("options", [])
    print(f"✓ Generated {len(options)} meme text options:")
    
    for i, option in enumerate(options[:3], 1):  # Show first 3 as preview
        print(f"  Option {i}:")
        print(f"    TOP: {option['top_text']}")
        print(f"    BOTTOM: {option['bottom_text']}")
        print(f"    Virality: {option['virality_score']:.2f} | Image Coherence: {option['image_coherence_score']:.2f}")
        print(f"    Humor: {option['humor_pattern_used']}")
    
    if len(options) > 3:
        print(f"  ... and {len(options) - 3} more options")
    
    # Track angles used to prevent repetition
    if previous_angles is None:
        previous_angles = []
    for option in options:
        current_angle = f"{option['top_text'][:20]}..."
        previous_angles.append(current_angle)
    
    state["meme_text"] = meme_text_data
    state["previous_meme_angles"] = previous_angles
    return state
