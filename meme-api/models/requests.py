"""Request models for the Meme API."""
from typing import Optional
from pydantic import BaseModel, Field, validator


class MemeGenerateRequest(BaseModel):
    """Request model for meme generation."""
    
    content: Optional[str] = Field(
        None,
        description="Pre-written content text for the meme",
        min_length=3,
        max_length=5000
    )
    topic: Optional[str] = Field(
        None,
        description="Topic to generate meme content about",
        min_length=3,
        max_length=500
    )
    
    # Optional overrides
    tone: Optional[str] = Field(
        None,
        description="Tone for meme generation (edgy, professional, casual, etc.)"
    )
    humor_type: Optional[str] = Field(
        None,
        description="Type of humor (sarcastic, witty, ironic, etc.)"
    )
    
    @validator('content', 'topic')
    def at_least_one_required(cls, v, values):
        """Ensure at least content or topic is provided."""
        if not v and not values.get('content') and not values.get('topic'):
            raise ValueError('Either content or topic must be provided')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "When you finally understand DeFi",
                "tone": "edgy"
            }
        }
