import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from src.utils.supabase_client import get_supabase_client

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_TABLES = [
    "rekt_meme_automation_runs",
    "rekt_meme_content_generations",
    "rekt_meme_trend_research",
    "rekt_meme_generations",
    "rekt_meme_twitter_engagement",
    "rekt_competition_research",
    "rekt_kol_research"
]

@router.get("/runs")
def get_runs(
    status: Optional[str] = Query(None, description="Filter by run status (e.g. running, completed)"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO)"),
    limit: int = Query(50, description="Max runs to return"),
    latest: bool = Query(False, description="Fetch the exact latest run")
):
    """Fetch automation runs."""
    return fetch_from_table("rekt_meme_automation_runs", start_date, end_date, limit, latest, status=status)

@router.get("/{table_name}")
def get_table_data(
    table_name: str,
    start_date: Optional[datetime] = Query(None, description="Start date (ISO)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO)"),
    limit: int = Query(50, description="Max rows to return"),
    latest: bool = Query(False, description="Fetch the absolute latest row only")
):
    """Dynamically fetch from any supported results table."""
    return fetch_from_table(table_name, start_date, end_date, limit, latest)

def fetch_from_table(
    table_name: str, 
    start_date: Optional[datetime], 
    end_date: Optional[datetime], 
    limit: int, 
    latest: bool,
    status: Optional[str] = None
) -> Dict[str, Any]:
    
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail=f"Table {table_name} is not allowed or does not exist.")
    
    try:
        supabase = get_supabase_client()
        query = supabase.table(table_name).select("*")
        
        # Apply filters
        if status and table_name == "rekt_meme_automation_runs":
            query = query.eq("status", status)
        
        if start_date:
            query = query.gte("created_at", start_date.isoformat())
        if end_date:
            query = query.lte("created_at", end_date.isoformat())
            
        # Apply limits & ordering
        query = query.order("created_at", desc=True)
        
        if latest:
            query = query.limit(1)
        else:
            query = query.limit(limit)
            
        response = query.execute()
        return {"data": response.data, "count": len(response.data)}
        
    except Exception as e:
        logger.error(f"Error reading from {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
