"""Meme generation service that wraps the LangGraph flow."""
import os
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.graph.state import GraphState
from src.nodes import (
    sentiment_analysis_node,
    template_image_analysis_node,
    text_generation_node,
    text_selection_node
)
from src.utils.llm_utils import get_llm
from config import settings, MINIMAL_BUSINESS_CONTEXT


class MemeService:
    """Service for generating meme text using the LangGraph workflow."""
    
    def __init__(self):
        """Initialize the meme service."""
        self.temp_dir = Path(tempfile.gettempdir()) / "meme-api"
        self.temp_dir.mkdir(exist_ok=True)
        
    async def generate_meme_text(
        self,
        topic: str,
        is_twitter_post: bool = False,
        template_image_path: str = None,
        tone: Optional[str] = None,
        humor_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate meme text using the simplified workflow.
        
        Args:
            topic: Topic text or full Twitter post
            is_twitter_post: True if topic is a full Twitter post, False if short topic
            template_image_path: Path to template image (REQUIRED)
            tone: Optional tone override
            humor_type: Optional humor type override
            
        Returns:
            Dict with top 3 options and metadata
        """
        try:
            # Verify LLM is available
            if not settings.has_llm_key:
                raise ValueError("No LLM API key configured")
            
            # Test LLM connection
            try:
                llm = get_llm()
            except Exception as e:
                raise ValueError(f"Failed to initialize LLM: {e}")
            
            # Create initial state with minimal context and direct input
            input_type = "twitter_post" if is_twitter_post else "topic"
            
            state = GraphState(
                config={
                    "platforms": ["twitter"],
                    "tone": tone or "edgy",
                    "humor_type": humor_type or "relatable"
                },
                execution_metadata={
                    "execution_id": f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "flow": "meme_api",
                    "started_at": datetime.now().isoformat(),
                    "errors": []
                },
                business_context=MINIMAL_BUSINESS_CONTEXT,
                input_text=topic,
                input_type=input_type
            )
            
            # Node 1: Sentiment Analysis
            print(f"🔍 Analyzing content sentiment...")
            state = sentiment_analysis_node(state)
            
            # Validate template image is required
            if not template_image_path or not Path(template_image_path).exists():
                raise ValueError("Template image is required. Please upload a meme template image.")
            
            print(f"🖼️  Using provided template: {Path(template_image_path).name}")
            state["template_selection"] = {
                "template_image_path": template_image_path,
                "template_metadata": {
                    "category": "user_upload",
                    "source": "api"
                }
            }
            
            # Node 2: Template Image Analysis
            print(f"🔬 Analyzing template image...")
            state = template_image_analysis_node(state)
            
            # Node 3: Text Generation (10 options, NO brand context)
            print(f"💬 Generating 10 meme text options...")
            state = text_generation_node(state)
            
            # Node 4: Text Selection (Top 3)
            print(f"🎯 Selecting top 3 options...")
            state = text_selection_node(state)
            
            # Extract results from Node 4
            text_selection = state.get("text_selection", {})
            top_3_options = text_selection.get("top_3_options", [])
            selection_metadata = text_selection.get("selection_metadata", {})
            content_analysis = state.get("content_analysis", {})
            image_analysis = state.get("image_analysis", {})
            
            result = {
                "options": top_3_options,
                "metadata": {
                    "dominant_emotion": content_analysis.get("dominant_emotion"),
                    "humor_type": content_analysis.get("humor_type"),
                    "meme_format": image_analysis.get("meme_format"),
                    "total_options_considered": selection_metadata.get("total_options_considered", 10),
                    "weighting": selection_metadata.get("weighting", "60% text input, 40% image coherence")
                }
            }
            
            print(f"✅ Generated top 3 options")
            return result
            
        except Exception as e:
            print(f"❌ Meme generation failed: {e}")
            raise

    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary file."""
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp file {file_path}: {e}")


# Global service instance
meme_service = MemeService()
