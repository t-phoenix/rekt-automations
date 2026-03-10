"""Flow 5: Twitter Engagement — standalone Twitter engagement and reply generation flow."""
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
class TwitterEngagementState(TypedDict, total=False):
    config: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    scraped_tweets: List[Dict]       # After Node 1
    scored_tweets: List[Dict]        # After Node 2
    suggested_replies: List[Dict]    # After Node 3
    _engagement_dir: Any             # pathlib.Path injected by flow


# ── Import nodes (late import to keep this module importable before install) ─
def _load_nodes():
    from ..nodes.fetch_trending_tweets import fetch_trending_tweets_node
    from ..nodes.score_and_filter_tweets import score_and_filter_tweets_node
    from ..nodes.generate_replies import generate_replies_node
    from ..nodes.twitter_engagement_output import twitter_engagement_output_node
    return (
        fetch_trending_tweets_node,
        score_and_filter_tweets_node,
        generate_replies_node,
        twitter_engagement_output_node,
    )


class TwitterEngagementFlow(FlowBase):
    """
    Flow 5: Twitter Engagement (standalone).

    Pipeline:
      fetch_trending_tweets -> score_and_filter_tweets -> generate_replies -> twitter_engagement_output -> END

    This flow is fully independent — it grabs top tweets, scores them for Rekt CEO relevancy,
    and drafts savage replies to farm engagement.
    It creates its own run directory under output/runs/<run-id>/twitter_engagement/.

    Usage:
        python main.py --flow twitter_engagement
        python main.py --flow twitter_engagement --override "dry_run=true"
    """

    def __init__(
        self,
        run_id: Optional[str] = None,
        config: Optional[FlowConfig] = None,
        override_string: Optional[str] = None,
        override_dict: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(run_id=run_id, config=config, override_string=override_string, override_dict=override_dict)
        self.flow_name = "twitter_engagement"

        # Create the twitter-engagement-specific output directory
        run_dir = self.run_manager.get_run_dir(self.run_id)
        self.engagement_dir = run_dir / "twitter_engagement"
        self.engagement_dir.mkdir(parents=True, exist_ok=True)

    def _create_workflow(self) -> StateGraph:
        """Build and compile the twitter engagement LangGraph workflow."""
        (
            fetch_trending_tweets_node,
            score_and_filter_tweets_node,
            generate_replies_node,
            twitter_engagement_output_node,
        ) = _load_nodes()

        workflow = StateGraph(TwitterEngagementState)

        workflow.add_node("fetch_trending_tweets", fetch_trending_tweets_node)
        workflow.add_node("score_and_filter_tweets", score_and_filter_tweets_node)
        workflow.add_node("generate_replies", generate_replies_node)
        workflow.add_node("twitter_engagement_output", twitter_engagement_output_node)

        workflow.set_entry_point("fetch_trending_tweets")
        workflow.add_edge("fetch_trending_tweets", "score_and_filter_tweets")
        workflow.add_edge("score_and_filter_tweets", "generate_replies")
        workflow.add_edge("generate_replies", "twitter_engagement_output")
        workflow.add_edge("twitter_engagement_output", END)

        return workflow.compile()

    def run(self) -> Dict[str, Any]:
        """
        Execute the twitter engagement flow.

        Returns:
            Flow output with scored tweets, generated replies, and metadata.
        """
        self.print_banner("TWITTER ENGAGEMENT FLOW")

        # Dry-run mode detection
        dry_run: bool = self.config.get("dry_run", False)
        if dry_run:
            print("  🧪 DRY RUN MODE — no real API calls will be made\n")

        app = self._create_workflow()

        initial_state = TwitterEngagementState(
            config=self.config.to_dict(),
            execution_metadata={
                "execution_id": self.run_id,
                "flow": "twitter_engagement",
                "started_at": datetime.now().isoformat(),
                "errors": [],
            },
            # Inject the engagement output directory so the output node can save files
            _engagement_dir=self.engagement_dir,
        )

        print(f"⏰ Started at: {initial_state['execution_metadata']['started_at']}\n")

        try:
            final_state = app.invoke(initial_state)

            final_state["execution_metadata"]["completed_at"] = datetime.now().isoformat()

            output_data = {
                "suggested_replies": final_state.get("suggested_replies", []),
                "scored_tweets": final_state.get("scored_tweets", []),
                "execution_metadata": final_state.get("execution_metadata", {}),
            }

            # Save to standard flow output (for potential cross-flow use)
            self.save_output(output_data)

            self.update_run_metadata({
                "twitter_engagement_flow_completed": True,
                "twitter_engagement_flow_completed_at": datetime.now().isoformat(),
                "engagement_dir": str(self.engagement_dir),
            })

            print("\n" + "=" * 60)
            print("✅ TWITTER ENGAGEMENT FLOW COMPLETED")
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
                        "status": "twitter_engagement_complete",
                        "configuration": self.config.to_dict()
                    }).execute()
                    
                    # 2. Insert Twitter Engagement Outputs
                    sb.table("rekt_meme_twitter_engagement").insert({
                        "run_id": self.run_id,
                        "scraped_tweets": final_state.get("scraped_tweets", []),
                        "scored_tweets": final_state.get("scored_tweets", []),
                        "suggested_replies": final_state.get("suggested_replies", [])
                    }).execute()
                    
                    print(f"  ✅ Saved Twitter Engagement to Supabase")
                    
            except Exception as e:
                print(f"  ⚠️  Failed to save to Supabase: {e}")
                traceback.print_exc()

            return output_data

        except Exception as e:
            print(f"\n❌ Twitter engagement flow failed: {e}")
            raise

    def _print_summary(self, output_data: Dict[str, Any]) -> None:
        scored = output_data.get("scored_tweets", [])
        replies = output_data.get("suggested_replies", [])

        print(f"\n📊 SUMMARY:")
        print("-" * 60)
        print(f"  Tweets scraped & scored: {len(scored)}")
        print(f"  Replies generated: {len(replies)}")
        
        if replies:
            top_reply = replies[0]
            print(f"  🥇 Top target: @{top_reply.get('author_handle', 'unknown')} (Score: {top_reply.get('score', 0)})")
            print(f"     Preview: \"{top_reply.get('suggested_reply', '')[:60]}...\"")

        print(f"\n  📁 Output directory: {self.engagement_dir}")
        print(f"     engagement_report.md  — full Markdown table of tweets & replies")
        print(f"     engagement_data.json  — structured JSON")

        meta = output_data.get("execution_metadata", {})
        print(f"\n⏱️  Execution:")
        print(f"   Started:   {meta.get('started_at', 'N/A')}")
        print(f"   Completed: {meta.get('completed_at', 'N/A')}")
        print("\n" + "=" * 60)
