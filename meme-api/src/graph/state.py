"""State schema for LangGraph workflow."""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class BrandIdentity(TypedDict, total=False):
    """Core brand identity components."""
    core_narrative: str
    brand_pillars: List[str]
    unique_value_proposition: str
    brand_personality_traits: List[str]
    brand_archetype: str


class CommunicationStyle(TypedDict, total=False):
    """How the brand communicates."""
    tone_descriptors: List[str]
    voice_characteristics: str
    humor_style: str
    example_phrases: List[str]
    language_patterns: str


class StrategicMessaging(TypedDict, total=False):
    """Strategic messaging framework."""
    key_messages: List[str]
    messaging_frameworks: Dict[str, str]
    content_themes: List[str]


class AudienceIntelligence(TypedDict, total=False):
    """Target audience intelligence."""
    primary_audience: str
    psychographics: str
    expertise_level: str
    engagement_preferences: str


class BrandGuardrails(TypedDict, total=False):
    """Brand guidelines and constraints."""
    dos: List[str]
    donts: List[str]
    sensitive_topics: List[str]
    competitor_mentions: str


class ContentVariationSeeds(TypedDict, total=False):
    """Seeds for content variation to prevent repetition."""
    perspectives: List[str]
    narrative_approaches: List[str]
    emotional_ranges: List[str]


class BusinessContext(TypedDict, total=False):
    """Output from Node 1: Business Context Ingestion (Enhanced)."""
    brand_identity: BrandIdentity
    communication_style: CommunicationStyle
    strategic_messaging: StrategicMessaging
    audience_intelligence: AudienceIntelligence
    brand_guardrails: BrandGuardrails
    content_variation_seeds: ContentVariationSeeds


class TrendingTopic(TypedDict, total=False):
    """Individual trending topic (Enhanced for Web3)."""
    topic: str
    domain: str  # e.g., "memecoins", "defi", "nfts", "rwa", "blockchain_infrastructure"
    chains_affected: List[str]  # e.g., ["ethereum", "base", "solana"]
    description: str
    reason: str
    sentiment: str
    relevance_score: float
    virality_potential: float
    meme_angles: List[str]
    technical_depth: str  # "low", "medium", "high"
    source: str
    engagement_metrics: Optional[Dict[str, int]]


class TrendIntelligence(TypedDict, total=False):
    """Output from Node 2: Trend Intelligence."""
    trending_topics: List[TrendingTopic]
    selected_topic: TrendingTopic


class PlatformContent(TypedDict, total=False):
    """Output from Node 3: Platform Content Curation."""
    twitter: Optional[Dict[str, Any]]
    instagram: Optional[Dict[str, Any]]
    linkedin: Optional[Dict[str, Any]]


class ContentAnalysis(TypedDict, total=False):
    """Output from Node 4: Content Context & Sentiment Analysis."""
    dominant_emotion: str
    humor_type: str
    meme_worthiness_score: float
    meme_angle: str
    visual_vibe: str
    narrative_intent: str
    suggested_template_categories: List[str]


class TemplateSelection(TypedDict, total=False):
    """Output from Node 5: Meme Template Selection."""
    template_image_path: str
    template_metadata: Dict[str, Any]


class ImageAnalysis(TypedDict, total=False):
    """Output from Node 5.5: Template Image Analysis (NEW)."""
    image_description: str
    visual_elements: List[str]
    emotional_context: str
    meme_format: str
    text_placement_suitability: Dict[str, str]
    suggested_narrative_structure: str
    cultural_references: List[str]
    humor_opportunities: List[str]


class MemeTextOption(TypedDict, total=False):
    """Single meme text option."""
    top_text: str
    bottom_text: str
    virality_score: float
    image_coherence_score: float
    humor_pattern_used: str
    character_counts: Dict[str, int]


class TextSelection(TypedDict, total=False):
    """Output from Node 4: Text Selection (Top 3)."""
    top_3_options: List[MemeTextOption]  # Top 3 selected options with ranking_score
    selection_metadata: Dict[str, Any]


class BrandedTemplate(TypedDict, total=False):
    """Output from Node 6: Brand Identity Blending."""
    branded_template_image_path: str
    modifications_applied: Dict[str, bool]
    preview_metadata: Dict[str, str]


class MemeText(TypedDict, total=False):
    """Output from Node 3: Meme Text Generation (Multiple Options)."""
    options: List[MemeTextOption]  # List of 10 generated options


class FinalMeme(TypedDict, total=False):
    """Output from Node 8: Final Meme Rendering."""
    final_meme_image_path: str
    rendering_metadata: Dict[str, Any]


class AnimatedMeme(TypedDict, total=False):
    """Output from Node 9: Meme Animation."""
    animated_meme_video_path: str
    animation_metadata: Dict[str, Any]


class ExecutionMetadata(TypedDict, total=False):
    """Execution tracking metadata."""
    execution_id: str
    started_at: str
    completed_at: Optional[str]
    errors: List[str]


class GraphState(TypedDict, total=False):
    """
    Main state object that accumulates outputs from all nodes.
    This is the central data structure passed between LangGraph nodes.
    """
    # Configuration inputs
    config: Dict[str, Any]
    
    # Input data (NEW - for API flow)
    input_text: Optional[str]  # Raw input from user (topic or Twitter post)
    input_type: Optional[str]  # Either "topic" or "twitter_post"
    
    # Node outputs
    business_context: Optional[BusinessContext]
    content_analysis: Optional[ContentAnalysis]
    template_selection: Optional[TemplateSelection]
    image_analysis: Optional[ImageAnalysis]
    meme_text: Optional[MemeText]
    text_selection: Optional[TextSelection]
    
    # Unused in API flow (kept for compatibility with full automation flow)
    trend_intelligence: Optional[TrendIntelligence]
    platform_content: Optional[PlatformContent]
    branded_template: Optional[BrandedTemplate]
    final_meme: Optional[FinalMeme]
    animated_meme: Optional[AnimatedMeme]
    
    # Variation tracking
    previous_meme_angles: Optional[List[str]]
    
    # Execution metadata
    execution_metadata: ExecutionMetadata
