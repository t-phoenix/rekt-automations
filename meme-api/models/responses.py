"""Response models for the Meme API."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class MemeOption(BaseModel):
    """A single meme text option."""
    
    top_text: str = Field(..., description="Top text for the meme")
    bottom_text: str = Field(..., description="Bottom text for the meme")
    ranking_score: float = Field(..., description="Overall ranking score (0-1)")
    virality_score: float = Field(..., description="Virality score (0-1)")
    image_coherence_score: float = Field(..., description="Text-image coherence (0-1)")
    text_alignment_score: float = Field(..., description="Alignment with user input (0-1)")
    humor_pattern_used: str = Field(..., description="Humor pattern used")


class MemeTextResponse(BaseModel):
    """Response model for meme text generation - Top 3 options."""
    
    options: list[MemeOption] = Field(..., description="Top 3 meme text options ranked by quality")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Selection metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "options": [
                    {
                        "top_text": "WHEN YOU FINALLY",
                        "bottom_text": "UNDERSTAND DEFI",
                        "ranking_score": 0.89,
                        "virality_score": 0.85,
                        "image_coherence_score": 0.92,
                        "text_alignment_score": 0.87,
                        "humor_pattern_used": "triumphant_flex"
                    },
                    {
                        "top_text": "ME EXPLAINING DEFI",
                        "bottom_text": "TO MY CAT",
                        "ranking_score": 0.84,
                        "virality_score": 0.80,
                        "image_coherence_score": 0.88,
                        "text_alignment_score": 0.82,
                        "humor_pattern_used": "absurdist"
                    },
                    {
                        "top_text": "DEFI BE LIKE",
                        "bottom_text": "IT'S COMPLICATED",
                        "ranking_score": 0.81,
                        "virality_score": 0.78,
                        "image_coherence_score": 0.85,
                        "text_alignment_score": 0.79,
                        "humor_pattern_used": "relatable_struggle"
                    }
                ],
                "metadata": {
                    "dominant_emotion": "confidence",
                    "meme_format": "top_bottom_classic",
                    "total_options_considered": 10
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid file format",
                "detail": "Only JPEG, PNG, and WebP images are supported",
                "code": "INVALID_FILE_FORMAT"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    llm_available: bool = Field(..., description="Whether LLM is available")
