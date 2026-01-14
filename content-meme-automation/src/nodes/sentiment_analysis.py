"""Node 4: Content Context & Sentiment Analysis."""
import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate

from ..utils import get_llm
from ..graph.state import GraphState, ContentAnalysis


def analyze_content_sentiment(platform_content: Dict, trending_topic: Dict) -> ContentAnalysis:
    """
    Analyze content for emotion, humor, and meme-worthiness.
    
    Args:
        platform_content: Generated platform content
        trending_topic: Selected trending topic
        
    Returns:
        ContentAnalysis with emotion, humor type, visual vibe, etc.
    """
    llm = get_llm("analysis")
    
    # Combine all platform content for analysis
    all_content = []
    if "twitter" in platform_content:
        all_content.append(f"Twitter: {platform_content['twitter'].get('post', '')}")
    if "instagram" in platform_content:
        all_content.append(f"Instagram: {platform_content['instagram'].get('caption', '')}")
    if "linkedin" in platform_content:
        all_content.append(f"LinkedIn: {platform_content['linkedin'].get('post', '')}")
    
    combined_content = "\n\n".join(all_content)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a content analyst specializing in meme psychology and viral content.

Analyze the provided content and return a JSON object with:
- dominant_emotion: One of: "joy", "surprise", "anger", "confidence", "confusion", "triumph"
- humor_type: One of: "satire", "irony", "absurd", "witty", "wholesome", "none"
- meme_worthiness_score: 0-1 score of how meme-able this content is
- meme_angle: Brief description of the meme angle (e.g., "celebrate community win")
- visual_vibe: Visual style suggestion (e.g., "confident_success", "shocked_reaction")
- narrative_intent: One of: "educational", "promotional", "community", "reactive"
- suggested_template_categories: Array of 2-3 template categories (e.g., ["success_failure", "reaction_memes"])

Return ONLY valid JSON."""),
        ("user", """Content:
{content}

Trending Topic: {topic}
Sentiment: {sentiment}

Analyze and return JSON:""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "content": combined_content,
        "topic": trending_topic.get("topic", ""),
        "sentiment": trending_topic.get("sentiment", "neutral")
    })
    
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    analysis_dict = json.loads(content)
    
    return ContentAnalysis(**analysis_dict)


def sentiment_analysis_node(state: GraphState) -> GraphState:
    """
    Node 4: Analyze content for emotion, humor, and meme potential.
    
    This node:
    - Analyzes combined platform content
    - Detects dominant emotion
    - Classifies humor type
    - Scores meme-worthiness
    - Suggests visual vibe for template selection
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with content_analysis populated
    """
    print("\n🎭 NODE 4: Content Context & Sentiment Analysis")
    print("=" * 50)
    
    platform_content = state.get("platform_content", {})
    trending_topic = state.get("trend_intelligence", {}).get("selected_topic", {})
    
    print("🔍 Analyzing content sentiment...")
    analysis = analyze_content_sentiment(platform_content, trending_topic)
    
    print(f"✓ Dominant Emotion: {analysis['dominant_emotion']}")
    print(f"✓ Humor Type: {analysis['humor_type']}")
    print(f"✓ Meme Worthiness: {analysis['meme_worthiness_score']:.2f}")
    print(f"✓ Visual Vibe: {analysis['visual_vibe']}")
    print(f"✓ Suggested Templates: {', '.join(analysis['suggested_template_categories'])}")
    
    state["content_analysis"] = analysis
    return state
