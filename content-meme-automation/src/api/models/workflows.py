from pydantic import BaseModel, Field
from typing import List, Optional

class TrendResearchRequest(BaseModel):
    limit: int = Field(5, description="Number of trends to fetch/process")
    timeframe: str = Field("7d", description="Timeframe for trend research")
    custom_keywords: Optional[List[str]] = Field(None, description="Inject explicit keywords to force consideration and weightage")
    platforms: Optional[List[str]] = Field(None, description="Limit platforms to search trends from")

class KolResearchRequest(BaseModel):
    target_niche: Optional[str] = Field(None, description="Specific niche out of the default tech/web3")
    min_followers: Optional[int] = Field(None, description="Minimum followers threshold")
    max_followers: Optional[int] = Field(None, description="Maximum followers constraint")
    platforms: Optional[List[str]] = Field(None, description="Allowed social media platforms")

class CompetitionResearchRequest(BaseModel):
    competitor_handles: Optional[List[str]] = Field(None, description="Specific handles to research, overriding default db config")
    analysis_depth: str = Field("basic", description="Depth of analysis: 'basic' or 'deep'")

class TextContentRequest(BaseModel):
    business_context: Optional[str] = Field(None, description="String contextualizing the goal to append to vector db output")
    tone: Optional[str] = Field(None, description="Desired brand voice tone, e.g. edgy, professional")
    platforms: Optional[List[str]] = Field(None, description="Target platforms to generate text content for")

class MemeGenerationRequest(BaseModel):
    user_text: Optional[str] = Field(None, description="Direct text input for the meme (overrides trend flow)")
    platform: Optional[str] = Field(None, description="Target platform for the direct text input (e.g., 'twitter', 'linkedin')")
    theme: Optional[str] = Field(None, description="Specific theme or topic to meme about")
    tone: Optional[str] = Field(None, description="Meme humor style/tone")
    platforms: Optional[List[str]] = Field(None, description="Optimize for specific platform dimensions")
    template_preference: Optional[str] = Field(None, description="Enforce a specific layout or meme format template")

class TwitterEngagementRequest(BaseModel):
    target_accounts: Optional[List[str]] = Field(None, description="Specific Twitter handles to reply to")
    reply_tone: Optional[str] = Field(None, description="Voice/tone for the generated replies")

class AnimationRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="Explicit textual prompt for generation")
    style: Optional[str] = Field("auto", description="Video stylistic choice flag")
