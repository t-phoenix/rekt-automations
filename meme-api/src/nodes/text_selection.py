"""Node 4: Text Selection (NEW)."""
import json
from typing import Dict, Any, List
from ..graph.state import GraphState, MemeTextOption


def calculate_text_input_alignment(
    option: Dict,
    content_analysis: Dict
) -> float:
    """
    Calculate how well the text option aligns with user's input sentiment.
    
    Args:
        option: A single meme text option
        content_analysis: Sentiment analysis from Node 1
        
    Returns:
        Alignment score (0-1)
    """
    # Base score from virality (reflects overall quality)
    alignment_score = option.get("virality_score", 0.5)
    
    # Bonus for matching emotion through humor pattern
    humor_pattern = option.get("humor_pattern_used", "")
    input_emotion = content_analysis.get("dominant_emotion", "")
    input_humor = content_analysis.get("humor_type", "")
    
    # Emotion-humor pattern alignment bonuses
    emotion_humor_map = {
        "joy": ["triumphant_flex", "hyperbole", "relatable_struggle"],
        "surprise": ["subversion_of_expectations", "absurdist"],
        "confidence": ["triumphant_flex", "hyperbole", "wordplay"],
        "triumph": ["triumphant_flex", "callback_humor"],
        "confusion": ["absurdist", "ironic_contrast", "relatable_struggle"],
        "anger": ["ironic_contrast", "self_deprecating", "sarcastic"]
    }
    
    if input_emotion in emotion_humor_map and humor_pattern in emotion_humor_map[input_emotion]:
        alignment_score += 0.15
    
    # Cap at 1.0
    return min(alignment_score, 1.0)


def rank_text_options(
    options: List[Dict],
    content_analysis: Dict,
    image_analysis: Dict
) -> List[Dict]:
    """
    Rank all text options using 60/40 weighting.
    
    60% Text Input Alignment (user's sentiment/topic)
    40% Image Coherence (how well text fits image)
    
    Args:
        options: List of 10 meme text options from Node 3
        content_analysis: Sentiment analysis from Node 1
        image_analysis: Image analysis from Node 2
        
    Returns:
        List of options sorted by ranking_score (highest first)
    """
    ranked_options = []
    used_humor_patterns = set()
    
    for option in options:
        # Calculate text input alignment (60% weight)
        text_alignment = calculate_text_input_alignment(option, content_analysis)
        
        # Get image coherence score (40% weight)
        image_coherence = option.get("image_coherence_score", 0.5)
        
        # Calculate weighted score
        ranking_score = (0.6 * text_alignment) + (0.4 * image_coherence)
        
        # Diversity bonus: slightly boost if using a new humor pattern
        humor_pattern = option.get("humor_pattern_used", "")
        if humor_pattern not in used_humor_patterns:
            ranking_score += 0.05
            used_humor_patterns.add(humor_pattern)
        
        # Add ranking score to option
        option_with_rank = option.copy()
        option_with_rank["ranking_score"] = min(ranking_score, 1.0)
        option_with_rank["text_alignment_score"] = text_alignment
        
        ranked_options.append(option_with_rank)
    
    # Sort by ranking_score (descending)
    ranked_options.sort(key=lambda x: x["ranking_score"], reverse=True)
    
    return ranked_options


def text_selection_node(state: GraphState) -> GraphState:
    """
    Node 4: Select top 3 meme text options from the 10 generated.
    
    This NEW node:
    - Receives 10 text options from Node 3
    - Uses content analysis from Node 1 and image analysis from Node 2
    - Ranks using 60/40 weighting (text input vs image coherence)
    - Returns top 3 best options
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with text_selection populated (top 3 options)
    """
    print("\n🏆 NODE 4: Text Selection (Top 3)")
    print("=" * 50)
    
    meme_text = state.get("meme_text", {})
    content_analysis = state.get("content_analysis", {})
    image_analysis = state.get("image_analysis", {})
    
    options = meme_text.get("options", [])
    
    if not options:
        raise ValueError("No meme text options found - Node 3 must run before Node 4")
    
    print(f"📊 Ranking {len(options)} options...")
    print(f"   60% weight on text input alignment")
    print(f"   40% weight on image coherence")
    
    # Rank all options
    ranked_options = rank_text_options(options, content_analysis, image_analysis)
    
    # Select top 3
    top_3 = ranked_options[:3]
    
    print(f"\n✓ Top 3 Selected:")
    for i, option in enumerate(top_3, 1):
        print(f"  #{i} (Score: {option['ranking_score']:.3f})")
        print(f"     TOP: {option['top_text']}")
        print(f"     BOTTOM: {option['bottom_text']}")
        print(f"     Text Alignment: {option['text_alignment_score']:.2f} | Image Coherence: {option['image_coherence_score']:.2f}")
        print(f"     Humor: {option['humor_pattern_used']}")
    
    # Store in state
    state["text_selection"] = {
        "top_3_options": top_3,
        "selection_metadata": {
            "total_options_considered": len(options),
            "weighting": "60% text input, 40% image coherence",
            "diversity_bonus_applied": True
        }
    }
    
    return state
