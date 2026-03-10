"""Flow 4: Trend Research — standalone Twitter trend intelligence flow."""
import json
from datetime import datetime
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, TypedDict, List

from ..utils.supabase_client import get_supabase_client

from langgraph.graph import StateGraph, END

from .flow_base import FlowBase
from ..config.flow_config import FlowConfig


# ── Lightweight state just for this flow ──────────────────────────────────
class TrendResearchState(TypedDict, total=False):
    config: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    raw_trends: List[Dict]         # After Node 1
    researched_trends: List[Dict]  # After Node 2
    scored_trends: List[Dict]      # After Node 3
    trend_report: Dict[str, Any]   # After Node 4
    _trends_dir: Any               # pathlib.Path injected by flow


# ── Import nodes (late import to keep this module importable before install) ─
def _load_nodes():
    from ..nodes.twitter_trends import twitter_trends_node
    from ..nodes.perplexity_research import perplexity_research_node
    from ..nodes.rekt_relevance_scoring import rekt_relevance_scoring_node
    from ..nodes.trend_table_output import trend_table_output_node
    return (
        twitter_trends_node,
        perplexity_research_node,
        rekt_relevance_scoring_node,
        trend_table_output_node,
    )


class TrendResearchFlow(FlowBase):
    """
    Flow 4: Trend Research (standalone).

    Pipeline:
      twitter_trends → perplexity_research → rekt_relevance_scoring → trend_table_output → END

    This flow is fully independent — it doesn't require Flows 1-3.
    It creates its own run directory under output/runs/<run-id>/trends/.

    Usage:
        python main.py --flow trends
        python main.py --flow trends --override "dry_run=true"
    """

    def __init__(
        self,
        run_id: Optional[str] = None,
        config: Optional[FlowConfig] = None,
        override_string: Optional[str] = None,
        override_dict: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(run_id=run_id, config=config, override_string=override_string, override_dict=override_dict)
        self.flow_name = "trends"

        # Create the trends-specific output directory
        run_dir = self.run_manager.get_run_dir(self.run_id)
        self.trends_dir = run_dir / "trends"
        self.trends_dir.mkdir(parents=True, exist_ok=True)

    def _create_workflow(self) -> StateGraph:
        """Build and compile the trend research LangGraph workflow."""
        (
            twitter_trends_node,
            perplexity_research_node,
            rekt_relevance_scoring_node,
            trend_table_output_node,
        ) = _load_nodes()

        workflow = StateGraph(TrendResearchState)

        workflow.add_node("twitter_trends", twitter_trends_node)
        workflow.add_node("perplexity_research", perplexity_research_node)
        workflow.add_node("rekt_relevance_scoring", rekt_relevance_scoring_node)
        workflow.add_node("trend_table_output", trend_table_output_node)

        workflow.set_entry_point("twitter_trends")
        workflow.add_edge("twitter_trends", "perplexity_research")
        workflow.add_edge("perplexity_research", "rekt_relevance_scoring")
        workflow.add_edge("rekt_relevance_scoring", "trend_table_output")
        workflow.add_edge("trend_table_output", END)

        return workflow.compile()

    def run(self) -> Dict[str, Any]:
        """
        Execute the trend research flow.

        Returns:
            Flow output with scored trends, markdown report, and metadata.
        """
        self.print_banner("TREND RESEARCH FLOW")

        # Dry-run mode detection
        dry_run: bool = self.config.get("dry_run", False)
        if dry_run:
            print("  🧪 DRY RUN MODE — no real API calls will be made\n")

        app = self._create_workflow()

        initial_state = TrendResearchState(
            config=self.config.to_dict(),
            execution_metadata={
                "execution_id": self.run_id,
                "flow": "trend_research",
                "started_at": datetime.now().isoformat(),
                "errors": [],
            },
            # Inject the trends output directory so Node 4 can save files
            _trends_dir=self.trends_dir,
        )

        print(f"⏰ Started at: {initial_state['execution_metadata']['started_at']}\n")

        try:
            final_state = app.invoke(initial_state)

            final_state["execution_metadata"]["completed_at"] = datetime.now().isoformat()

            output_data = {
                "trend_report": final_state.get("trend_report", {}),
                "scored_trends": final_state.get("scored_trends", []),
                "execution_metadata": final_state.get("execution_metadata", {}),
            }

            # Save to standard flow output (for potential cross-flow use)
            self.save_output(output_data)

            self.update_run_metadata({
                "trends_flow_completed": True,
                "trends_flow_completed_at": datetime.now().isoformat(),
                "top_topic": output_data["trend_report"].get("top_topic"),
                "topic_count": output_data["trend_report"].get("topic_count", 0),
                "trends_dir": str(self.trends_dir),
            })

            print("\n" + "=" * 60)
            print("✅ TREND RESEARCH FLOW COMPLETED")
            print("=" * 60)
            self._print_summary(output_data)
            
            # Save to Supabase
            try:
                if self.run_id:
                    print(f"  💾 Saving to Supabase...")
                    sb = get_supabase_client()
                    
                    # 1. Upsert Automation Run
                    sb.table("rekt_meme_automation_runs").upsert({
                        "id": self.run_id,
                        "status": "trends_complete",
                        "configuration": self.config.to_dict()
                    }).execute()
                    
                    # 2. Insert Trend Research Outputs
                    # Pulling raw/filtered trends requires state inspection. We grab them from final_state.
                    sb.table("rekt_meme_trend_research").insert({
                        "run_id": self.run_id,
                        "raw_trends": final_state.get("raw_trends", []),
                        "filtered_trends": final_state.get("researched_trends", []),
                        "scored_trends": final_state.get("scored_trends", [])
                    }).execute()
                    
                    print(f"  ✅ Saved Trend Research to Supabase")
                    
            except Exception as e:
                print(f"  ⚠️  Failed to save to Supabase: {e}")
                traceback.print_exc()

            return output_data

        except Exception as e:
            print(f"\n❌ Trend research flow failed: {e}")
            raise

    def _print_summary(self, output_data: Dict[str, Any]) -> None:
        report = output_data.get("trend_report", {})
        scored = output_data.get("scored_trends", [])

        print(f"\n📊 SUMMARY:")
        print("-" * 60)
        print(f"  Topics analysed: {report.get('topic_count', 0)}")
        if report.get("top_topic"):
            top = scored[0] if scored else {}
            print(f"  🥇 Top topic:  {report['top_topic']}  (score: {report.get('top_score', 0):.2f})")
            print(f"     Momentum:   {top.get('momentum', 'N/A')}")
            print(f"     Forecast:   {top.get('forecast_7d_probability', 0):.0%} chance of trending next 7d")

        print(f"\n  📁 Output directory: {self.trends_dir}")
        print(f"     trend_report.md  — full Markdown table + deep-dives")
        print(f"     trend_data.json  — structured JSON")

        meta = output_data.get("execution_metadata", {})
        print(f"\n⏱️  Execution:")
        print(f"   Started:   {meta.get('started_at', 'N/A')}")
        print(f"   Completed: {meta.get('completed_at', 'N/A')}")
        print("\n" + "=" * 60)
