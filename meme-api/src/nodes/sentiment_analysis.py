"""Node 1: Topic Sentiment Analysis."""
import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate

from ..utils import get_llm
from ..graph.state import GraphState, ContentAnalysis


def analyze_topic_sentiment(input_text: str, is_twitter_post: bool) -> ContentAnalysis:
    """
    Analyze topic or Twitter post for emotion, humor, and meme-worthiness.
    
    Args:
        input_text: Raw input text (either short topic or full Twitter post)
        is_twitter_post: True if input is a full Twitter post, False if short topic
        
    Returns:
        ContentAnalysis with emotion, humor type, visual vibe, etc.
    """
    llm = get_llm("analysis")
    
    # Different prompts based on input type
    if is_twitter_post:
        system_prompt = """You are a content analyst specializing in meme psychology and viral content.

Analyze the provided TWITTER POST and return a JSON object with:
- dominant_emotion: One of: "joy", "surprise", "anger", "confidence", "confusion", "triumph"
- humor_type: One of: "satire", "irony", "absurd", "witty", "wholesome", "none"
- meme_worthiness_score: 0-1 score of how meme-able this content is
- meme_angle: Brief description of the meme angle (e.g., "celebrate community win", "relatable dev frustrations")
- visual_vibe: Visual style suggestion (e.g., "confident_success", "shocked_reaction", "facepalm_moment")
- narrative_intent: One of: "educational", "promotional", "community", "reactive"
- suggested_template_categories: Array of 2-3 template categories (e.g., ["success_failure", "reaction_memes"])

Analyze the tweet's sentiment, tone, and underlying message to determine the best meme approach.

Return ONLY valid JSON."""
    else:
        system_prompt = """You are a content analyst specializing in meme psychology and viral content.

Analyze the provided SHORT TOPIC and infer what kind of meme the user wants to create.

Based on SOLELY the given topic, return a JSON object with:
- dominant_emotion: One of: "joy", "surprise", "anger", "confidence", "confusion", "triumph" (infer from topic)
- humor_type: One of: "satire", "irony", "absurd", "witty", "wholesome", "none" (suggest based on topic)
- meme_worthiness_score: 0-1 score of how meme-able this topic is
- meme_angle: Brief description of the meme angle to take (e.g., "celebrate success", "poke fun at complexity")
- visual_vibe: Visual style suggestion (e.g., "confident_success", "confused_learning", "triumphant_moment")
- narrative_intent: One of: "educational", "promotional", "community", "reactive"
- suggested_template_categories: Array of 2-3 template categories that would work well

You must INFER the user's intent from just the topic text. Think about what emotion, humor, and visual style would best capture this topic as a meme.

Return ONLY valid JSON."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", """Input:
{input_text}

Analyze and return JSON:""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "input_text": input_text
    })
    
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    analysis_dict = json.loads(content)
    
    return ContentAnalysis(**analysis_dict)


def sentiment_analysis_node(state: GraphState) -> GraphState:
    """
    Node 1: Analyze topic or Twitter post for emotion, humor, and meme potential.
    
    This node:
    - Analyzes either short topic or full Twitter post based on input_type
    - Detects dominant emotion from raw input
    - Classifies humor type
    - Scores meme-worthiness
    - Suggests visual vibe for meme creation
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with content_analysis populated
    """
    print("\n🎭 NODE 1: Topic Sentiment Analysis")
    print("=" * 50)
    
    input_text = state.get("input_text", "")
    input_type = state.get("input_type", "topic")
    is_twitter_post = (input_type == "twitter_post")
    
    input_label = "Twitter Post" if is_twitter_post else "Topic"
    print(f"📝 Input Type: {input_label}")
    print(f"📄 Input: {input_text[:100]}{'...' if len(input_text) > 100 else ''}")
    print("🔍 Analyzing sentiment...")
    
    analysis = analyze_topic_sentiment(input_text, is_twitter_post)
    
    print(f"✓ Dominant Emotion: {analysis['dominant_emotion']}")
    print(f"✓ Humor Type: {analysis['humor_type']}")
    print(f"✓ Meme Worthiness: {analysis['meme_worthiness_score']:.2f}")
    print(f"✓ Meme Angle: {analysis['meme_angle']}")
    print(f"✓ Visual Vibe: {analysis['visual_vibe']}")
    print(f"✓ Suggested Templates: {', '.join(analysis['suggested_template_categories'])}")
    
    state["content_analysis"] = analysis
    return state
