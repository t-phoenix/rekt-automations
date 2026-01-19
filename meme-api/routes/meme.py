"""Meme generation API routes."""
import os
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Request
from fastapi.responses import JSONResponse

from models import (
    MemeTextResponse,
    ErrorResponse,
    HealthResponse
)
from services import meme_service
from config import settings

# Import limiter from app (will be accessed via request.app.state.limiter)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/meme", tags=["meme"])


@router.post(
    "/generate",
    response_model=MemeTextResponse,
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Generate meme text",
    description="Generate top 3 meme text options. Rate limited to 1 request per 2 minutes per IP."
)
@limiter.limit("1/2minutes")
async def generate_meme(
    request: Request,
    topic: Optional[str] = Form(None, description="Topic or Twitter post text"),
    is_twitter_post: bool = Form(False, description="Toggle: True if input is a full Twitter post, False if short topic"),
    tone: Optional[str] = Form(None, description="Tone (edgy, professional, casual)"),
    humor_type: Optional[str] = Form(None, description="Humor type (sarcastic, witty, ironic)"),
    template_image: UploadFile = File(..., description="Meme template image (REQUIRED)")
):
    """Generate meme text from topic or Twitter post."""
    
    # Validation
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'topic' must be provided"
        )
    
    temp_file_path = None
    
    try:
        # Handle template image upload
        if template_image:
            # Validate file type
            if template_image.content_type not in settings.allowed_image_formats:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file format. Allowed: {', '.join(settings.allowed_image_formats)}"
                )
            
            # Validate file size
            content_data = await template_image.read()
            if len(content_data) > settings.max_file_size_bytes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
                )
            
            # Save to temp file
            suffix = Path(template_image.filename).suffix if template_image.filename else ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content_data)
                temp_file_path = tmp.name
        
        # Generate meme text (returns top 3 options)
        result = await meme_service.generate_meme_text(
            topic=topic,
            is_twitter_post=is_twitter_post,
            template_image_path=temp_file_path,
            tone=tone,
            humor_type=humor_type
        )
        
        # Build response with top 3 options
        response = MemeTextResponse(
            options=result.get("options", []),
            metadata=result.get("metadata", {})
        )
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error generating meme: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate meme text"
        )
    finally:
        # Cleanup temp file
        if temp_file_path:
            meme_service.cleanup_temp_file(temp_file_path)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the meme generation service is healthy"
)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        llm_available=settings.has_llm_key
    )
