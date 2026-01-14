"""Flow 2: Meme Generation."""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from langgraph.graph import StateGraph, END

from .flow_base import FlowBase
from ..graph.state import GraphState
from ..nodes import (
    sentiment_analysis_node,
    template_selection_node,
    template_image_analysis_node,
    brand_blending_node,
    text_generation_node,
    meme_rendering_node,
)


class MemeGenerationFlow(FlowBase):
    """Flow for generating branded memes."""
    
    def __init__(
        self,
        run_id: Optional[str] = None,
        config: Optional[Any] = None,
        override_string: Optional[str] = None
    ):
        """
        Initialize MemeGenerationFlow.
        
        Args:
            run_id: Existing run ID to continue, or None to create new
            config: FlowConfig instance or None to create from defaults
            override_string: Configuration override string
        """
        super().__init__(run_id=run_id, config=config, override_string=override_string)
        self.flow_name = "meme"
    
    def _create_workflow(self) -> StateGraph:
        """
        Create the meme generation workflow.
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("sentiment_analysis", sentiment_analysis_node)
        workflow.add_node("template_selection", template_selection_node)
        workflow.add_node("image_analysis", template_image_analysis_node)
        workflow.add_node("brand_blending", brand_blending_node)
        workflow.add_node("text_generation", text_generation_node)
        workflow.add_node("meme_rendering", meme_rendering_node)
        
        # Set entry point
        workflow.set_entry_point("sentiment_analysis")
        
        # Define edges
        workflow.add_edge("sentiment_analysis", "template_selection")
        workflow.add_edge("template_selection", "image_analysis")
        workflow.add_edge("image_analysis", "brand_blending")
        workflow.add_edge("brand_blending", "text_generation")
        workflow.add_edge("text_generation", "meme_rendering")
        workflow.add_edge("meme_rendering", END)
        
        return workflow.compile()
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the meme generation flow.
        
        Returns:
            Flow output with meme assets and metadata
        """
        self.print_banner("MEME GENERATION FLOW")
        
        # Validate configuration
        self.validate_config()
        
        # Load previous text flow output if available
        text_output = self.load_previous_flow_output("text")
        if not text_output:
            print("⚠️  Warning: No previous text flow output found")
            print("    Meme generation will use minimal context\n")
        
        # Create workflow
        app = self._create_workflow()
        
        # Initialize state with text flow outputs if available
        initial_state = GraphState(
            config=self.config.to_dict(),
            execution_metadata={
                "execution_id": self.run_id,
                "flow": "meme_generation",
                "started_at": datetime.now().isoformat(),
                "errors": []
            }
        )
        
        # Add text flow outputs to state if available
        if text_output:
            initial_state["business_context"] = text_output.get("business_context", {})
            initial_state["trend_intelligence"] = text_output.get("trend_intelligence", {})
            initial_state["platform_content"] = text_output.get("platform_content", {})
        
        print(f"⏰ Started at: {initial_state['execution_metadata']['started_at']}\n")
        
        # Run workflow
        try:
            final_state = app.invoke(initial_state)
            
            # Update completion time
            final_state["execution_metadata"]["completed_at"] = datetime.now().isoformat()
            
            # Extract outputs
            output_data = {
                "content_analysis": final_state.get("content_analysis", {}),
                "template_selection": final_state.get("template_selection", {}),
                "branded_template": final_state.get("branded_template", {}),
                "meme_text": final_state.get("meme_text", {}),
                "final_meme": final_state.get("final_meme", {}),
                "execution_metadata": final_state.get("execution_metadata", {}),
            }
            
            # Save outputs to files
            self._save_outputs_to_files(output_data)
            
            # Save flow output metadata
            self.save_output(output_data)
            
            # Update run metadata
            self.update_run_metadata({
                "meme_flow_completed": True,
                "meme_flow_completed_at": datetime.now().isoformat(),
                "final_meme_path": output_data.get("final_meme", {}).get("final_meme_image_path"),
            })
            
            print("\n" + "=" * 60)
            print("✅ MEME GENERATION FLOW COMPLETED")
            print("=" * 60)
            self._print_summary(output_data)
            
            return output_data
            
        except Exception as e:
            print(f"\n❌ Meme generation flow failed: {e}")
            raise
    
    def _save_outputs_to_files(self, output_data: Dict[str, Any]) -> None:
        """
        Save outputs to individual files.
        
        Args:
            output_data: Output data from the flow
        """
        memes_dir = self.run_dirs["memes"]
        
        # Save meme metadata
        metadata_file = memes_dir / "meme_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "content_analysis": output_data.get("content_analysis", {}),
                "meme_text": output_data.get("meme_text", {}),
                "template_metadata": output_data.get("template_selection", {}).get("template_metadata", {}),
            }, f, indent=2, ensure_ascii=False)
        print(f"  📋 Saved meme metadata: {metadata_file}")
        
        # Note: Actual image files are already saved by the nodes
        # Just log their locations
        if "final_meme" in output_data:
            meme_path = output_data["final_meme"].get("final_meme_image_path")
            if meme_path:
                print(f"  🖼️  Final meme: {meme_path}")
        
        if "branded_template" in output_data:
            template_path = output_data["branded_template"].get("branded_template_image_path")
            if template_path:
                print(f"  🎨 Branded template: {template_path}")
    
    def _print_summary(self, output_data: Dict[str, Any]) -> None:
        """
        Print flow summary.
        
        Args:
            output_data: Output data from the flow
        """
        print(f"\n📊 SUMMARY:")
        print("-" * 60)
        
        # Content Analysis
        if "content_analysis" in output_data:
            analysis = output_data["content_analysis"]
            print(f"\n✓ Content Analysis:")
            print(f"  Emotion: {analysis.get('dominant_emotion', 'N/A')}")
            print(f"  Humor: {analysis.get('humor_type', 'N/A')}")
            print(f"  Meme Score: {analysis.get('meme_worthiness_score', 0):.2f}")
        
        # Meme Text
        if "meme_text" in output_data:
            text = output_data["meme_text"]
            print(f"\n✓ Meme Text:")
            print(f"  TOP: {text.get('top_text', 'N/A')}")
            print(f"  BOTTOM: {text.get('bottom_text', 'N/A')}")
        
        # Final Assets
        if "final_meme" in output_data:
            path = output_data["final_meme"].get("final_meme_image_path")
            print(f"\n✓ Generated Assets:")
            print(f"  🖼️  Meme: {path}")
        
        # Execution metadata
        metadata = output_data.get("execution_metadata", {})
        print(f"\n⏱️ Execution:")
        print(f"  Started: {metadata.get('started_at', 'N/A')}")
        print(f"  Completed: {metadata.get('completed_at', 'N/A')}")
        
        print("\n" + "=" * 60)
