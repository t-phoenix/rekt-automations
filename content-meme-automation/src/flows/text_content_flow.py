"""Flow 1: Text Content Generation."""
import json
from datetime import datetime
import traceback
from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.supabase_client import get_supabase_client

from langgraph.graph import StateGraph, END

from .flow_base import FlowBase
from ..graph.state import GraphState
from ..nodes import (
    trend_intelligence_node,
    content_curation_node,
)


class TextContentFlow(FlowBase):
    """Flow for generating platform-specific text content."""
    
    def __init__(
        self,
        run_id: Optional[str] = None,
        config: Optional[Any] = None,
        override_string: Optional[str] = None,
        override_dict: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize TextContentFlow.
        
        Args:
            run_id: Existing run ID to continue, or None to create new
            config: FlowConfig instance or None to create from defaults
            override_string: Configuration override string
            override_dict: Configuration override dictionary
        """
        super().__init__(run_id=run_id, config=config, override_string=override_string, override_dict=override_dict)
        self.flow_name = "text"
    
    def _create_workflow(self) -> StateGraph:
        """
        Create the text content generation workflow.
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node("trend_intelligence", trend_intelligence_node)
        workflow.add_node("content_curation", content_curation_node)

        # Set entry point directly to trend intelligence (RAG replaces business_context node)
        workflow.set_entry_point("trend_intelligence")

        # Define edges
        workflow.add_edge("trend_intelligence", "content_curation")
        workflow.add_edge("content_curation", END)

        return workflow.compile()
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the text content generation flow.
        
        Returns:
            Flow output with platform content, trends, and business context
        """
        self.print_banner("TEXT CONTENT GENERATION FLOW")
        
        # Validate configuration
        self.validate_config()
        
        # Create workflow
        app = self._create_workflow()
        
        # Initialize state
        initial_state = GraphState(
            config=self.config.to_dict(),
            execution_metadata={
                "execution_id": self.run_id,
                "flow": "text_content",
                "started_at": datetime.now().isoformat(),
                "errors": []
            }
        )
        
        print(f"⏰ Started at: {initial_state['execution_metadata']['started_at']}\n")
        
        # Run workflow
        try:
            final_state = app.invoke(initial_state)
            
            # Update completion time
            final_state["execution_metadata"]["completed_at"] = datetime.now().isoformat()
            
            # Extract outputs
            output_data = {
                "trend_intelligence": final_state.get("trend_intelligence", {}),
                "platform_content": final_state.get("platform_content", {}),
                "execution_metadata": final_state.get("execution_metadata", {}),
            }
            
            # Save outputs to files
            self._save_outputs_to_files(output_data)
            
            # Save flow output metadata
            self.save_output(output_data)
            
            # Update run metadata
            self.update_run_metadata({
                "text_flow_completed": True,
                "text_flow_completed_at": datetime.now().isoformat(),
                "platforms": self.config.get("platforms", []),
            })
            
            print("\n" + "=" * 60)
            print("✅ TEXT CONTENT FLOW COMPLETED")
            print("=" * 60)
            self._print_summary(output_data)
            
            # Save to Supabase
            try:
                # Get trends and content gracefully
                ti = output_data.get("trend_intelligence", {})
                pc = output_data.get("platform_content", {})
                
                # Check if we should save (we need at least a run ID)
                if self.run_id:
                    print(f"  💾 Saving to Supabase...")
                    sb = get_supabase_client()
                    
                    # 1. Upsert Automation Run
                    sb.table("rekt_meme_automation_runs").upsert({
                        "id": self.run_id,
                        "status": "text_complete",
                        "configuration": self.config.to_dict()
                    }).execute()
                    
                    # 2. Insert Content Generations
                    platforms = list(pc.keys()) if pc else []
                    sb.table("rekt_meme_content_generations").insert({
                        "run_id": self.run_id,
                        "platforms": platforms,
                        "trends_data": ti,
                        "business_context": final_state.get("business_context", {}),
                        "generated_text": pc,
                    }).execute()
                    print(f"  ✅ Saved Text Outputs to Supabase")
                    
            except Exception as e:
                print(f"  ⚠️  Failed to save to Supabase: {e}")
                traceback.print_exc()
            
            return output_data
            
        except Exception as e:
            print(f"\n❌ Text content flow failed: {e}")
            raise
    
    def _save_outputs_to_files(self, output_data: Dict[str, Any]) -> None:
        """
        Save outputs to individual files.
        
        Args:
            output_data: Output data from the flow
        """
        content_dir = self.run_dirs["content"]
        
        # Save platform content
        if "platform_content" in output_data:
            platform_file = content_dir / "platform_content.json"
            with open(platform_file, 'w', encoding='utf-8') as f:
                json.dump(output_data["platform_content"], f, indent=2, ensure_ascii=False)
            print(f"  📄 Saved platform content: {platform_file}")
            
            # Also save individual platform files
            for platform, content in output_data["platform_content"].items():
                if content:
                    platform_file = content_dir / f"{platform}_content.txt"
                    text = content.get("post") or content.get("caption") or content.get("article") or content.get("content", "")
                    with open(platform_file, 'w', encoding='utf-8') as f:
                        f.write(f"Platform: {platform.upper()}\n")
                        f.write(f"Run ID: {self.run_id}\n")
                        f.write("=" * 60 + "\n\n")
                        f.write(text)
                    print(f"  📝 Saved {platform}: {platform_file}")
        
        # Save trends
        if "trend_intelligence" in output_data:
            trends_file = content_dir / "trends.json"
            with open(trends_file, 'w', encoding='utf-8') as f:
                json.dump(output_data["trend_intelligence"], f, indent=2, ensure_ascii=False)
            print(f"  📊 Saved trends: {trends_file}")
    
    def _print_summary(self, output_data: Dict[str, Any]) -> None:
        """
        Print flow summary.
        
        Args:
            output_data: Output data from the flow
        """
        print(f"\n📊 SUMMARY:")
        print("-" * 60)
        
        # Trends
        if "trend_intelligence" in output_data:
            topic = output_data["trend_intelligence"].get("selected_topic", {})
            print(f"\n✓ Trending Topic:")
            print(f"  {topic.get('topic', 'N/A')}")
            print(f"  Relevance: {topic.get('relevance_score', 0):.2f}")
        
        # Platform Content
        if "platform_content" in output_data:
            print(f"\n✓ Platform Content Generated:")
            for platform in output_data["platform_content"].keys():
                print(f"  ✓ {platform.capitalize()}")
        
        # Execution metadata
        metadata = output_data.get("execution_metadata", {})
        print(f"\n⏱️ Execution:")
        print(f"  Started: {metadata.get('started_at', 'N/A')}")
        print(f"  Completed: {metadata.get('completed_at', 'N/A')}")
        
        print("\n" + "=" * 60)
