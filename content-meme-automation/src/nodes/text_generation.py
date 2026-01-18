"""Node 7: Meme Text Generation (Image-Aware)."""
import json
import random
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate

from ..utils import get_llm
from ..graph.state import GraphState, MemeText


def generate_meme_text(
    content_analysis: Dict,
    platform_content: Dict,
    business_context: Dict,
    image_analysis: Dict,
    previous_angles: list = None
) -> MemeText:
    """
    Generate viral meme text (top and bottom) - IMAGE-AWARE VERSION.
    
    Args:
        content_analysis: Sentiment and humor analysis
        platform_content: Generated platform content
        business_context: Business context (enhanced nested structure)
        image_analysis: NEW - Visual analysis from Node 5.5
        previous_angles: Previously used angles to avoid repetition
        
    Returns:
        MemeText with top_text, bottom_text, and metadata
    """
    llm = get_llm("content_generation")
    
    # Extract brand context from nested structure
    communication_style = business_context.get("communication_style", {})
    variation_seeds = business_context.get("content_variation_seeds", {})
    
    # Select random humor pattern for variation
    humor_patterns = [
        "wordplay",
        "subversion_of_expectations",
        "cultural_references",
        "absurdist",
        "self_deprecating",
        "hyperbole",
        "callback_humor"
    ]
    selected_humor_pattern = random.choice(humor_patterns)
    
    # Select random perspective for variation
    perspectives = variation_seeds.get("perspectives", ["community cheerleader"])
    selected_perspective = random.choice(perspectives) if perspectives else "community cheerleader"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a VIRAL meme creator with deep understanding of Web3 culture and human humor.

## YOUR MISSION
Create meme text that:
1. **FITS THE IMAGE PERFECTLY** - The text must make sense with the visual
2. **USES HUMAN HUMOR** - Apply the specified humor pattern naturally
3. **STAYS ON BRAND** - Match the brand voice but with fresh perspective
4. **AVOIDS REPETITION** - Don't reuse these angles: {previous_angles}

## IMAGE CONTEXT (CRITICAL - READ CAREFULLY)
Image Description: {image_description}
Visual Elements: {visual_elements}
Emotional Context: {emotional_context}
Meme Format: {meme_format}
Narrative Structure: {narrative_structure}
Humor Opportunities: {humor_opportunities}

## HUMOR PATTERN TO USE: {humor_pattern}

**Humor Pattern Guidelines:**
- **wordplay**: Use puns, double meanings, clever word twists related to crypto/Web3
- **subversion_of_expectations**: Set up one expectation, deliver surprising twist
- **cultural_references**: Reference popular culture, internet memes, or Web3 inside jokes
- **absurdist**: Embrace the ridiculous, exaggerate to comedic effect
- **self_deprecating**: Poke fun at ourselves/community in relatable way
- **hyperbole**: Extreme exaggeration for comedic effect
- **callback_humor**: Reference known patterns in crypto/meme culture

## BRAND VOICE
Tone: {tone}
Humor Style: {humor_style}
Example Phrases: {example_phrases}

## CONTENT CONTEXT
Trending Topic: {topic}
Topic Domain: {topic_domain}
Meme Angle: {meme_angle}
Platform Content Sample: {content_sample}

## PERSPECTIVE: {perspective}
Approach this from the "{perspective}" angle

## TEXT GENERATION RULES
1. TOP TEXT: Setup that matches the image's visual context
2. BOTTOM TEXT: Punchline that complements the setup AND the image
3. Each line UNDER 40 characters
4. Use the image's natural emotion and narrative structure
5. Don't just describe the image - USE it for the joke
6. Make it Web3-relevant and culturally current
7. ALL CAPS or Mixed Case (your choice based on impact)
8. Platform-safe (no offensive content)

## OUTPUT FORMAT
Return ONLY a valid JSON object with:
{{
  "top_text": "string",
  "bottom_text": "string",
  "text_metadata": {{
    "character_counts": {{"top": int, "bottom": int}},
    "virality_score": float (0-1),
    "humor_pattern_used": "string",
    "perspective_used": "string",
    "image_coherence_score": float (0-1 - how well text matches image),
    "alternatives": [
      {{"top": "string", "bottom": "string"}},
      {{"top": "string", "bottom": "string"}}
    ]
  }}
}}

Make it VIRAL! 🔥 But most importantly, make it COHERENT with the IMAGE!"""),
        ("user", """Generate image-aware meme text as JSON.""")
    ])
    
    # Get sample content
    content_sample = ""
    if "twitter" in platform_content:
        content_sample = platform_content["twitter"].get("post", "")[:150]
    
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
        
        # Brand voice
        "tone": ", ".join(communication_style.get("tone_descriptors", [])),
        "humor_style": communication_style.get("humor_style", ""),
        "example_phrases": ", ".join(communication_style.get("example_phrases", [])[:3]),
        
        # Content context
        "topic": content_analysis.get("visual_vibe", ""),
        "topic_domain": content_analysis.get("narrative_intent", ""),
        "meme_angle": content_analysis.get("meme_angle", ""),
        "content_sample": content_sample,
        
        # Variation mechanisms
        "humor_pattern": selected_humor_pattern,
        "perspective": selected_perspective,
        "previous_angles": prev_angles_str
    })
    
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    meme_data = json.loads(content)
    
    return MemeText(**meme_data)


def text_generation_node(state: GraphState) -> GraphState:
    """
    Node 7: Generate viral meme text.
    
    This node:
    - Generates TOP TEXT and BOTTOM TEXT
    - Ensures text is concise and quotable
    - Matches brand tone and humor style
    - Provides alternatives for selection
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with meme_text populated
    """
    print("\n💬 NODE 7: Meme Text Generation")
    print("=" * 50)
    
    content_analysis = state.get("content_analysis", {})
    platform_content = state.get("platform_content", {})
    business_context = state.get("business_context", {})
    image_analysis = state.get("image_analysis", {})
    previous_angles = state.get("previous_meme_angles", [])
    
    if not image_analysis:
        raise ValueError("No image analysis found - Node 5.5 must run before Node 7")
    
    print(f"🎨 Image Format: {image_analysis.get('meme_format', 'Unknown')}")
    print("✍️ Generating meme text...")
    meme_text = generate_meme_text(content_analysis, platform_content, business_context, image_analysis, previous_angles)
    
    print(f"✓ Generated meme text:")
    print(f"  TOP: {meme_text['top_text']}")
    print(f"  BOTTOM: {meme_text['bottom_text']}")
    print(f"  Virality: {meme_text['text_metadata']['virality_score']:.2f}")
    print(f"  Image Coherence: {meme_text['text_metadata'].get('image_coherence_score', 0):.2f}")
    print(f"  Humor Pattern: {meme_text['text_metadata'].get('humor_pattern_used', 'N/A')}")
    
    # Track the angle used to prevent repetition
    current_angle = f"{meme_text['top_text'][:20]}..."
    if previous_angles is None:
        previous_angles = []
    previous_angles.append(current_angle)
    
    state["meme_text"] = meme_text
    state["previous_meme_angles"] = previous_angles
    return state
