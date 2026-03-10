import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any

from src.api.models.workflows import (
    TrendResearchRequest, KolResearchRequest, CompetitionResearchRequest,
    TextContentRequest, MemeGenerationRequest, TwitterEngagementRequest, AnimationRequest
)

# Import flows
from src.flows import (
    TrendResearchFlow, KOLResearchFlow, CompetitionResearchFlow,
    TextContentFlow, MemeGenerationFlow, TwitterEngagementFlow, AnimationFlow
)

router = APIRouter()
logger = logging.getLogger(__name__)

def run_workflow_task(flow_class, override_dict: Dict[str, Any], run_id: str):
    """Background task to instantiate and run a flow."""
    try:
        flow = flow_class(run_id=run_id, override_dict=override_dict)
        logger.info(f"Starting {flow.flow_name} with run_id: {flow.run_id}")
        flow.run()
        logger.info(f"Completed {flow.flow_name} with run_id: {flow.run_id}")
    except Exception as e:
        logger.error(f"Flow {flow_class.__name__} failed: {e}")

@router.post("/trend-research")
async def trigger_trend_research(request: TrendResearchRequest, background_tasks: BackgroundTasks):
    override_dict = request.model_dump(exclude_unset=True)
    # Instantiate flow just to get the run_id before backgrounding
    flow = TrendResearchFlow(override_dict=override_dict)
    background_tasks.add_task(run_workflow_task, TrendResearchFlow, override_dict, flow.run_id)
    return {"message": "Trend research flow started", "run_id": flow.run_id}

@router.post("/kol-research")
async def trigger_kol_research(request: KolResearchRequest, background_tasks: BackgroundTasks):
    override_dict = request.model_dump(exclude_unset=True)
    flow = KOLResearchFlow(override_dict=override_dict)
    background_tasks.add_task(run_workflow_task, KOLResearchFlow, override_dict, flow.run_id)
    return {"message": "KOL research flow started", "run_id": flow.run_id}

@router.post("/competition-research")
async def trigger_competition_research(request: CompetitionResearchRequest, background_tasks: BackgroundTasks):
    override_dict = request.model_dump(exclude_unset=True)
    flow = CompetitionResearchFlow(override_dict=override_dict)
    background_tasks.add_task(run_workflow_task, CompetitionResearchFlow, override_dict, flow.run_id)
    return {"message": "Competition research flow started", "run_id": flow.run_id}

@router.post("/text-content")
async def trigger_text_content(request: TextContentRequest, background_tasks: BackgroundTasks):
    override_dict = request.model_dump(exclude_unset=True)
    flow = TextContentFlow(override_dict=override_dict)
    background_tasks.add_task(run_workflow_task, TextContentFlow, override_dict, flow.run_id)
    return {"message": "Text content flow started", "run_id": flow.run_id}

@router.post("/meme-generation")
async def trigger_meme_generation(request: MemeGenerationRequest, background_tasks: BackgroundTasks):
    override_dict = request.model_dump(exclude_unset=True)
    flow = MemeGenerationFlow(override_dict=override_dict)
    background_tasks.add_task(run_workflow_task, MemeGenerationFlow, override_dict, flow.run_id)
    return {"message": "Meme generation flow started", "run_id": flow.run_id}

@router.post("/twitter-engagement")
async def trigger_twitter_engagement(request: TwitterEngagementRequest, background_tasks: BackgroundTasks):
    override_dict = request.model_dump(exclude_unset=True)
    flow = TwitterEngagementFlow(override_dict=override_dict)
    background_tasks.add_task(run_workflow_task, TwitterEngagementFlow, override_dict, flow.run_id)
    return {"message": "Twitter engagement flow started", "run_id": flow.run_id}

@router.post("/animation")
async def trigger_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    override_dict = request.model_dump(exclude_unset=True)
    flow = AnimationFlow(override_dict=override_dict)
    background_tasks.add_task(run_workflow_task, AnimationFlow, override_dict, flow.run_id)
    return {"message": "Animation flow started", "run_id": flow.run_id}
