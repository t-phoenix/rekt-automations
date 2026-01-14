"""LangGraph workflow definition."""
import os
from typing import Dict, Any
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END

from .state import GraphState
from ..nodes import (
    business_context_node,
    trend_intelligence_node,
    content_curation_node,
    sentiment_analysis_node,
    template_selection_node,
    brand_blending_node,
    text_generation_node,
    meme_rendering_node,
    meme_animation_node,
)


def should_animate(state: GraphState) -> str:
    """
    Decide whether to animate based on config.
    
    Args:
        state: Current graph state
        
    Returns:
        Edge name: "animate" or "skip"
    """
    skip_animation = state["config"].get("skip_animation", False)
    
    if skip_animation:
        return "skip"
    
    # Also check meme worthiness
    content_analysis = state.get("content_analysis", {})
    meme_score = content_analysis.get("meme_worthiness_score", 1.0)
    
    if meme_score < 0.5:
        print("⚠️ Low meme worthiness score, skipping animation")
        return "skip"
    
    return "animate"


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow.
    
    Returns:
        Compiled StateGraph
    """
    # Initialize graph
    workflow = StateGraph(GraphState)
    
    # Add all nodes
    workflow.add_node("business_context", business_context_node)
    workflow.add_node("trend_intelligence", trend_intelligence_node)
    workflow.add_node("content_curation", content_curation_node)
    workflow.add_node("sentiment_analysis", sentiment_analysis_node)
    workflow.add_node("template_selection", template_selection_node)
    workflow.add_node("brand_blending", brand_blending_node)
    workflow.add_node("text_generation", text_generation_node)
    workflow.add_node("meme_rendering", meme_rendering_node)
    workflow.add_node("meme_animation", meme_animation_node)
    
    # Set entry point
    workflow.set_entry_point("business_context")
    
    # Define edges
    # Business context → trend intelligence
    workflow.add_edge("business_context", "trend_intelligence")
    
    # Trend intelligence → content curation
    workflow.add_edge("trend_intelligence", "content_curation")
    
    # Content curation → sentiment analysis
    workflow.add_edge("content_curation", "sentiment_analysis")
    
    # Sentiment analysis → template selection
    workflow.add_edge("sentiment_analysis", "template_selection")
    
    # Template selection → brand blending
    workflow.add_edge("template_selection", "brand_blending")
    
    # Brand blending → text generation
    # (text generation also needs sentiment analysis output)
    workflow.add_edge("brand_blending", "text_generation")
    
    # Text generation → meme rendering
    workflow.add_edge("text_generation", "meme_rendering")
    
    # Conditional: meme rendering → animation or END
    workflow.add_conditional_edges(
        "meme_rendering",
        should_animate,
        {
            "animate": "meme_animation",
            "skip": END
        }
    )
    
    # Animation → END
    workflow.add_edge("meme_animation", END)
    
    # Compile
    return workflow.compile()


def run_workflow(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete content generation workflow.
    
    Args:
        config: Configuration dictionary with paths and settings
        
    Returns:
        Final state with all outputs
    """
    print("\n" + "=" * 60)
    print("🚀 LANGGRAPH CONTENT & MEME GENERATION AUTOMATION")
    print("=" * 60)
    
    # Create workflow app
    app = create_workflow()
    
    # Initialize state
    execution_id = str(uuid.uuid4())[:8]
    initial_state = GraphState(
        config=config,
        execution_metadata={
            "execution_id": execution_id,
            "started_at": datetime.now().isoformat(),
            "errors": []
        }
    )
    
    print(f"\n📋 Execution ID: {execution_id}")
    print(f"⏰ Started at: {initial_state['execution_metadata']['started_at']}")
    
    # Run workflow
    try:
        final_state = app.invoke(initial_state)
        
        # Update completion time
        final_state["execution_metadata"]["completed_at"] = datetime.now().isoformat()
        
        # Save platform content to files
        save_platform_content(final_state, config.get("output_dir", "./output"))
        
        print("\n" + "=" * 60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        # Print summary
        print_workflow_summary(final_state)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        raise


def save_platform_content(state: GraphState, output_dir: str) -> None:
    """
    Save platform-specific content to text files.
    
    Args:
        state: Final workflow state
        output_dir: Directory to save content files
    """
    if "platform_content" not in state:
        return
    
    import json
    
    # Create content subdirectory
    content_dir = os.path.join(output_dir, "content")
    os.makedirs(content_dir, exist_ok=True)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    execution_id = state.get("execution_metadata", {}).get("execution_id", "unknown")
    
    platform_content = state["platform_content"]
    
    # Save each platform's content
    for platform, content in platform_content.items():
        if not content:
            continue
        
        # Save as text file
        txt_filename = f"{platform}_content_{timestamp}.txt"
        txt_path = os.path.join(content_dir, txt_filename)
        
        # Extract content based on platform
        text = content.get("post") or content.get("caption") or content.get("article") or content.get("content", "")
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Platform: {platform.upper()}\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Execution ID: {execution_id}\n")
            f.write("=" * 60 + "\n\n")
            f.write(text)
            f.write("\n\n" + "=" * 60 + "\n")
            
            # Add metadata
            if "metadata" in content:
                f.write("\nMetadata:\n")
                for key, value in content["metadata"].items():
                    f.write(f"  {key}: {value}\n")
        
        # Save as JSON with full details
        json_filename = f"{platform}_content_{timestamp}.json"
        json_path = os.path.join(content_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "platform": platform,
                "timestamp": timestamp,
                "execution_id": execution_id,
                **content
            }, f, indent=2, ensure_ascii=False)
        
        print(f"  📄 Saved {platform.capitalize()}: {txt_path}")



def print_workflow_summary(state: GraphState) -> None:
    """Print a summary of the workflow results."""
    print("\n📊 WORKFLOW SUMMARY:")
    print("-" * 60)
    
    # Business Context
    if "business_context" in state:
        print(f"\n✓ Business Context:")
        print(f"  Tone: {state['business_context'].get('tone', 'N/A')}")
        print(f"  Messages: {len(state['business_context'].get('key_messages', []))}")
    
    # Trends
    if "trend_intelligence" in state:
        topic = state['trend_intelligence'].get('selected_topic', {})
        print(f"\n✓ Trending Topic:")
        print(f"  {topic.get('topic', 'N/A')}")
        print(f"  Relevance: {topic.get('relevance_score', 0):.2f}")
    
    # Platform Content
    if "platform_content" in state:
        print(f"\n✓ Platform Content Generated:")
        output_dir = state.get('config', {}).get('output_dir', './output')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for platform in ['twitter', 'instagram', 'linkedin']:
            if platform in state['platform_content']:
                print(f"  ✓ {platform.capitalize()}")
                print(f"    📄 Text: {output_dir}/content/{platform}_content_{timestamp}.txt")
                print(f"    📋 JSON: {output_dir}/content/{platform}_content_{timestamp}.json")
    
    # Sentiment Analysis
    if "content_analysis" in state:
        analysis = state['content_analysis']
        print(f"\n✓ Content Analysis:")
        print(f"  Emotion: {analysis.get('dominant_emotion', 'N/A')}")
        print(f"  Humor: {analysis.get('humor_type', 'N/A')}")
        print(f"  Meme Score: {analysis.get('meme_worthiness_score', 0):.2f}")
    
    # Final Assets
    print(f"\n✓ Generated Assets:")
    
    if "final_meme" in state:
        path = state['final_meme'].get('final_meme_image_path', '')
        print(f"  🖼️ Final Meme: {path}")
    
    if "animated_meme" in state:
        path = state['animated_meme'].get('animated_meme_video_path', '')
        print(f"  🎬 Animation: {path}")
    
    # Execution metadata
    metadata = state.get('execution_metadata', {})
    print(f"\n⏱️ Execution:")
    print(f"  ID: {metadata.get('execution_id', 'N/A')}")
    print(f"  Started: {metadata.get('started_at', 'N/A')}")
    print(f"  Completed: {metadata.get('completed_at', 'N/A')}")
    
    print("\n" + "=" * 60)
