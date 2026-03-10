"""Flow 7: KOL / Ideal Audience Research — discover matching KOLs and brainstorm engagement."""
from datetime import datetime
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, TypedDict, List
from langgraph.graph import StateGraph, END

from .flow_base import FlowBase
from ..config.flow_config import FlowConfig


class KOLResearchState(TypedDict, total=False):
    config: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    discovered_kols: List[str]
    kol_data: List[Dict]
    scored_kols: List[Dict]
    engagement_plans: List[Dict]
    kol_report_md: str
    _kol_dir: Any


def _load_nodes():
    from ..nodes.kol_discovery import kol_discovery_node
    from ..nodes.kol_profile_content_fetch import kol_profile_content_fetch_node
    from ..nodes.alignment_scoring import alignment_scoring_node
    from ..nodes.engagement_brainstorm import engagement_brainstorm_node
    from ..nodes.kol_research_output import kol_research_output_node
    
    return (
        kol_discovery_node,
        kol_profile_content_fetch_node,
        alignment_scoring_node,
        engagement_brainstorm_node,
        kol_research_output_node,
    )


class KOLResearchFlow(FlowBase):
    """
    Flow 7: KOL Research.
    Discovers KOLs, evaluates their fit, drafts highly-targeted replies.
    """
    def __init__(
        self,
        run_id: Optional[str] = None,
        config: Optional[FlowConfig] = None,
        override_string: Optional[str] = None,
        override_dict: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(run_id=run_id, config=config, override_string=override_string, override_dict=override_dict)
        self.flow_name = "kol_research"

        run_dir = self.run_manager.get_run_dir(self.run_id)
        self.kol_dir = run_dir / "kol_research"
        self.kol_dir.mkdir(parents=True, exist_ok=True)

    def _create_workflow(self) -> StateGraph:
        """Build and compile the LangGraph workflow."""
        (n1, n2, n3, n4, n5) = _load_nodes()
        workflow = StateGraph(KOLResearchState)
        workflow.add_node("kol_discovery", n1)
        workflow.add_node("kol_profile_content_fetch", n2)
        workflow.add_node("alignment_scoring", n3)
        workflow.add_node("engagement_brainstorm", n4)
        workflow.add_node("kol_research_output", n5)

        workflow.set_entry_point("kol_discovery")
        workflow.add_edge("kol_discovery", "kol_profile_content_fetch")
        workflow.add_edge("kol_profile_content_fetch", "alignment_scoring")
        workflow.add_edge("alignment_scoring", "engagement_brainstorm")
        workflow.add_edge("engagement_brainstorm", "kol_research_output")
        workflow.add_edge("kol_research_output", END)
        return workflow.compile()

    def run(self) -> Dict[str, Any]:
        """Execute the flow."""
        self.print_banner("KOL RESEARCH FLOW")

        dry_run: bool = self.config.get("dry_run", False)
        if dry_run:
            print("  🧪 DRY RUN MODE — no real API calls will be made\n")

        app = self._create_workflow()

        initial_state = KOLResearchState(
            config=self.config.to_dict(),
            execution_metadata={
                "execution_id": self.run_id,
                "flow": "kol_research",
                "started_at": datetime.now().isoformat(),
            },
            _kol_dir=self.kol_dir,
        )

        try:
            final_state = app.invoke(initial_state)
            final_state["execution_metadata"]["completed_at"] = datetime.now().isoformat()
            
            output_data = {
                "scored_kols": final_state.get("scored_kols"),
                "engagement_plans": final_state.get("engagement_plans"),
                "execution_metadata": final_state.get("execution_metadata"),
            }
            
            self.save_output(output_data)
            self.update_run_metadata({
                "kol_research_completed": True,
                "kol_dir": str(self.kol_dir),
            })
            
            print("\n✅ KOL RESEARCH FLOW COMPLETED")
            return output_data
            
        except Exception as e:
            print(f"\n❌ Flow failed: {e}")
            raise
