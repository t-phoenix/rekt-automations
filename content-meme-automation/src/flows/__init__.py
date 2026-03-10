"""Flows module."""
from .flow_base import FlowBase
from .text_content_flow import TextContentFlow
from .meme_generation_flow import MemeGenerationFlow
from .animation_flow import AnimationFlow
from .trend_research_flow import TrendResearchFlow
from .twitter_engagement_flow import TwitterEngagementFlow
from .competition_research_flow import CompetitionResearchFlow
from .kol_research_flow import KOLResearchFlow

__all__ = ["FlowBase", "TextContentFlow", "MemeGenerationFlow", "AnimationFlow", "TrendResearchFlow", "TwitterEngagementFlow", "CompetitionResearchFlow", "KOLResearchFlow"]
