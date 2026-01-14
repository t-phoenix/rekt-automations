"""Flow 3: Animation Generation."""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from langgraph.graph import StateGraph, END

from .flow_base import FlowBase
from ..graph.state import GraphState
from ..nodes import meme_animation_node


class AnimationFlow(FlowBase):
    """Flow for animating memes."""
    
    def __init__(
        self,
        run_id: Optional[str] = None,
        config: Optional[Any] = None,
        override_string: Optional[str] = None
    ):
        """
        Initialize AnimationFlow.
        
        Args:
            run_id: Existing run ID to continue, or None to create new
            config: FlowConfig instance or None to create from defaults
            override_string: Configuration override string
        """
        super().__init__(run_id=run_id, config=config, override_string=override_string)
        self.flow_name = "animation"
    
    def _create_workflow(self) -> StateGraph:
        """
        Create the animation workflow.
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(GraphState)
        
        # Add node
        workflow.add_node("meme_animation", meme_animation_node)
        
        # Set entry point
        workflow.set_entry_point("meme_animation")
        
        # Define edge
        workflow.add_edge("meme_animation", END)
        
        return workflow.compile()
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the animation flow.
        
        Returns:
            Flow output with animated video and metadata
        """
        self.print_banner("ANIMATION GENERATION FLOW")
        
        # Check if animation is disabled
        if self.config.get("skip_animation", False):
            print("⚠️  Animation is disabled in config (skip_animation=True)")
            print("    Skipping animation generation\n")
            return {"skipped": True}
        
        # Validate configuration
        self.validate_config()
        
        # Load previous meme flow output
        meme_output = self.load_previous_flow_output("meme")
        if not meme_output:
            raise ValueError("No previous meme flow output found. Run meme generation flow first.")
        
        # Get meme image path
        final_meme = meme_output.get("final_meme", {})
        meme_image_path = final_meme.get("final_meme_image_path")
        
        if not meme_image_path:
            raise ValueError("No meme image path found in previous flow output")
        
        print(f"📸 Input meme: {meme_image_path}\n")
        
        # Create workflow
        app = self._create_workflow()
        
        # Initialize state with meme flow outputs
        initial_state = GraphState(
            config=self.config.to_dict(),
            execution_metadata={
                "execution_id": self.run_id,
                "flow": "animation",
                "started_at": datetime.now().isoformat(),
                "errors": []
            }
        )
        
        # Add meme flow outputs to state
        initial_state["final_meme"] = final_meme
        initial_state["content_analysis"] = meme_output.get("content_analysis", {})
        
        print(f"⏰ Started at: {initial_state['execution_metadata']['started_at']}\n")
        
        # Run workflow
        try:
            final_state = app.invoke(initial_state)
            
            # Update completion time
            final_state["execution_metadata"]["completed_at"] = datetime.now().isoformat()
            
            # Extract outputs
            output_data = {
                "animated_meme": final_state.get("animated_meme", {}),
                "execution_metadata": final_state.get("execution_metadata", {}),
            }
            
            # Save outputs to files
            self._save_outputs_to_files(output_data)
            
            # Save flow output metadata
            self.save_output(output_data)
            
            # Update run metadata
            self.update_run_metadata({
                "animation_flow_completed": True,
                "animation_flow_completed_at": datetime.now().isoformat(),
                "animated_video_path": output_data.get("animated_meme", {}).get("animated_meme_video_path"),
            })
            
            print("\n" + "=" * 60)
            print("✅ ANIMATION FLOW COMPLETED")
            print("=" * 60)
            self._print_summary(output_data)
            
            return output_data
            
        except Exception as e:
            print(f"\n❌ Animation flow failed: {e}")
            raise
    
    def _save_outputs_to_files(self, output_data: Dict[str, Any]) -> None:
        """
        Save outputs to individual files.
        
        Args:
            output_data: Output data from the flow
        """
        video_dir = self.run_dirs["video"]
        
        # Save animation metadata
        metadata_file = video_dir / "animation_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(output_data.get("animated_meme", {}), f, indent=2, ensure_ascii=False)
        print(f"  📋 Saved animation metadata: {metadata_file}")
        
        # Note: Actual video file is already saved by the node
        # Just log its location
        if "animated_meme" in output_data:
            video_path = output_data["animated_meme"].get("animated_meme_video_path")
            if video_path:
                print(f"  🎬 Animated video: {video_path}")
    
    def _print_summary(self, output_data: Dict[str, Any]) -> None:
        """
        Print flow summary.
        
        Args:
            output_data: Output data from the flow
        """
        print(f"\n📊 SUMMARY:")
        print("-" * 60)
        
        # Animation metadata
        if "animated_meme" in output_data:
            anim = output_data["animated_meme"]
            print(f"\n✓ Animation:")
            print(f"  Style: {anim.get('animation_metadata', {}).get('style', 'N/A')}")
            print(f"  Video: {anim.get('animated_meme_video_path', 'N/A')}")
        
        # Execution metadata
        metadata = output_data.get("execution_metadata", {})
        print(f"\n⏱️ Execution:")
        print(f"  Started: {metadata.get('started_at', 'N/A')}")
        print(f"  Completed: {metadata.get('completed_at', 'N/A')}")
        
        print("\n" + "=" * 60)
