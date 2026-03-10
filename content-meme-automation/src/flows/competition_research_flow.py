"""Flow 6: Competition Research — scrape competitors and extract strategies."""
from datetime import datetime
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, TypedDict, List
from langgraph.graph import StateGraph, END

from .flow_base import FlowBase
from ..config.flow_config import FlowConfig


class CompetitionResearchState(TypedDict, total=False):
    config: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    discovered_competitors: List[str]
    raw_twitter_data: List[Dict]
    filtered_metrics: List[Dict]
    strategy_analysis: Dict[str, Any]
    competition_report_md: str
    _competition_dir: Any


def _load_nodes():
    from ..nodes.discover_competitors import discover_competitors_node
    from ..nodes.fetch_competitor_posts import fetch_competitor_posts_node
    from ..nodes.filter_and_rank_competitor_posts import filter_and_rank_competitor_posts_node
    from ..nodes.strategy_extraction import strategy_extraction_node
    from ..nodes.competition_research_output import competition_research_output_node
    
    return (
        discover_competitors_node,
        fetch_competitor_posts_node,
        filter_and_rank_competitor_posts_node,
        strategy_extraction_node,
        competition_research_output_node,
    )


class CompetitionResearchFlow(FlowBase):
    """
    Flow 6: Competition Research.
    Discovers competitors, fetches posts, extracts best strategies using RAG.
    """
    def __init__(
        self,
        run_id: Optional[str] = None,
        config: Optional[FlowConfig] = None,
        override_string: Optional[str] = None,
        override_dict: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(run_id=run_id, config=config, override_string=override_string, override_dict=override_dict)
        self.flow_name = "competition_research"

        run_dir = self.run_manager.get_run_dir(self.run_id)
        self.competition_dir = run_dir / "competition_research"
        self.competition_dir.mkdir(parents=True, exist_ok=True)

    def _create_workflow(self) -> StateGraph:
        """Build and compile the LangGraph workflow."""
        (n1, n2, n3, n4, n5) = _load_nodes()
        workflow = StateGraph(CompetitionResearchState)
        workflow.add_node("discover_competitors", n1)
        workflow.add_node("fetch_competitor_posts", n2)
        workflow.add_node("filter_and_rank_competitor_posts", n3)
        workflow.add_node("strategy_extraction", n4)
        workflow.add_node("competition_research_output", n5)

        workflow.set_entry_point("discover_competitors")
        workflow.add_edge("discover_competitors", "fetch_competitor_posts")
        workflow.add_edge("fetch_competitor_posts", "filter_and_rank_competitor_posts")
        workflow.add_edge("filter_and_rank_competitor_posts", "strategy_extraction")
        workflow.add_edge("strategy_extraction", "competition_research_output")
        workflow.add_edge("competition_research_output", END)
        return workflow.compile()

    def run(self) -> Dict[str, Any]:
        """Execute the flow."""
        self.print_banner("COMPETITION RESEARCH FLOW")

        dry_run: bool = self.config.get("dry_run", False)
        if dry_run:
            print("  🧪 DRY RUN MODE — no real API calls will be made\n")

        app = self._create_workflow()

        initial_state = CompetitionResearchState(
            config=self.config.to_dict(),
            execution_metadata={
                "execution_id": self.run_id,
                "flow": "competition_research",
                "started_at": datetime.now().isoformat(),
            },
            _competition_dir=self.competition_dir,
        )

        try:
            final_state = app.invoke(initial_state)
            final_state["execution_metadata"]["completed_at"] = datetime.now().isoformat()
            
            output_data = {
                "discovered_competitors": final_state.get("discovered_competitors"),
                "strategy_analysis": final_state.get("strategy_analysis"),
                "execution_metadata": final_state.get("execution_metadata"),
            }
            
            self.save_output(output_data)
            self.update_run_metadata({
                "competition_research_completed": True,
                "competition_dir": str(self.competition_dir),
            })
            
            print("\n✅ COMPETITION RESEARCH FLOW COMPLETED")
            return output_data
            
        except Exception as e:
            print(f"\n❌ Flow failed: {e}")
            raise
