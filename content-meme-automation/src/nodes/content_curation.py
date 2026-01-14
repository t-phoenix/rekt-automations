"""Node 3: Platform Content Curation."""
import os
import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate

from ..utils import get_llm
from ..graph.state import GraphState, PlatformContent


def generate_twitter_content(business_context: Dict, trending_topic: Dict) -> Dict[str, Any]:
    """Generate Twitter-optimized content."""
    llm = get_llm("content_generation")
    
    account_type = os.getenv("TWITTER_ACCOUNT_TYPE", "standard")
    max_chars = 4000 if account_type == "premium" else 280
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a viral Twitter content creator. Create an engaging tweet that:
- Matches the brand tone: {{tone}}
- Addresses the trending topic
- Is emoji-rich for better engagement
- Stays under {max_chars} characters
- Includes 2-4 relevant hashtags

Return ONLY a JSON object with: post, hashtags (array), character_count, account_type, emoji_count"""),
        ("user", """Brand Context:
{brand_summary}
Tone: {tone}
Key Messages: {key_messages}

Trending Topic: {topic}
{topic_description}

Generate Twitter content as JSON:""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "brand_summary": business_context.get("brand_summary", ""),
        "tone": business_context.get("tone", ""),
        "key_messages": ", ".join(business_context.get("key_messages", [])),
        "topic": trending_topic.get("topic", ""),
        "topic_description": trending_topic.get("description", "")
    })
    
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    return json.loads(content)


def generate_instagram_content(business_context: Dict, trending_topic: Dict) -> Dict[str, Any]:
    """Generate Instagram-optimized content."""
    llm = get_llm("content_generation")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an Instagram content strategist. Create an engaging caption that:
- Matches the brand tone: {tone}
- Is 125-150 words
- Is emoji-rich and visually engaging
- Includes 5-10 relevant hashtags
- Tells a story or creates engagement

Return ONLY a JSON object with: caption, hashtags (array), emoji_count"""),
        ("user", """Brand Context:
{brand_summary}
Tone: {tone}
Key Messages: {key_messages}

Trending Topic: {topic}
{topic_description}

Generate Instagram content as JSON:""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "brand_summary": business_context.get("brand_summary", ""),
        "tone": business_context.get("tone", ""),
        "key_messages": ", ".join(business_context.get("key_messages", [])),
        "topic": trending_topic.get("topic", ""),
        "topic_description": trending_topic.get("description", "")
    })
    
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    return json.loads(content)


def generate_linkedin_content(business_context: Dict, trending_topic: Dict) -> Dict[str, Any]:
    """Generate LinkedIn-optimized content."""
    llm = get_llm("content_generation")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a LinkedIn thought leader. Create a professional post that:
- Maintains professional yet engaging tone
- Is 150-200 words
- Provides insight or value
- Includes 2-3 professional hashtags
- Balances brand voice with LinkedIn professionalism

Return ONLY a JSON object with: post, hashtags (array), professional_tone_score (0-1)"""),
        ("user", """Brand Context:
{brand_summary}
Tone: {tone}
Key Messages: {key_messages}

Trending Topic: {topic}
{topic_description}

Generate LinkedIn content as JSON:""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "brand_summary": business_context.get("brand_summary", ""),
        "tone": business_context.get("tone", ""),
        "key_messages": ", ".join(business_context.get("key_messages", [])),
        "topic": trending_topic.get("topic", ""),
        "topic_description": trending_topic.get("description", "")
    })
    
    content = response.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    return json.loads(content)


def content_curation_node(state: GraphState) -> GraphState:
    """
    Node 3: Generate platform-optimized content.
    
    This node:
    - Generates content for Twitter, Instagram, LinkedIn
    - Adapts tone and format for each platform
    - Respects character limits (Twitter Premium support)
    - Creates emoji-rich, engaging content
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with platform_content populated
    """
    print("\n✍️ NODE 3: Platform Content Curation")
    print("=" * 50)
    
    business_context = state.get("business_context", {})
    trending_topic = state.get("trend_intelligence", {}).get("selected_topic", {})
    
    platforms = state["config"].get("platforms", ["twitter", "instagram", "linkedin"])
    
    platform_content = PlatformContent()
    
    if "twitter" in platforms:
        print("🐦 Generating Twitter content...")
        platform_content["twitter"] = generate_twitter_content(business_context, trending_topic)
        print(f"  ✓ {platform_content['twitter']['character_count']} chars, "
              f"{len(platform_content['twitter']['hashtags'])} hashtags")
    
    if "instagram" in platforms:
        print("📸 Generating Instagram content...")
        platform_content["instagram"] = generate_instagram_content(business_context, trending_topic)
        print(f"  ✓ {platform_content['instagram']['emoji_count']} emojis, "
              f"{len(platform_content['instagram']['hashtags'])} hashtags")
    
    if "linkedin" in platforms:
        print("💼 Generating LinkedIn content...")
        platform_content["linkedin"] = generate_linkedin_content(business_context, trending_topic)
        print(f"  ✓ Professional tone: {platform_content['linkedin']['professional_tone_score']:.2f}")
    
    state["platform_content"] = platform_content
    return state
