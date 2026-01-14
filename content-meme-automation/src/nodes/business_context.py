"""Node 1: Business Context Ingestion."""
import os
from pathlib import Path
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate

from ..utils import get_llm, get_docs_hash, parse_document, load_cache, save_cache
from ..graph.state import GraphState, BusinessContext


CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def load_cached_business_context(docs_hash: str) -> BusinessContext | None:
    """Load cached business context if hash matches."""
    cache_file = CACHE_DIR / f"business_context_{docs_hash}.json"
    return load_cache(cache_file)


def save_business_context_cache(docs_hash: str, context: BusinessContext) -> None:
    """Save business context to cache."""
    cache_file = CACHE_DIR / f"business_context_{docs_hash}.json"
    save_cache(cache_file, context)


def parse_all_documents(docs_path: str) -> str:
    """
    Recursively parse all documents in directory.
    
    Args:
        docs_path: Path to business_documents directory
        
    Returns:
        Concatenated text from all documents
    """
    docs_dir = Path(docs_path)
    
    if not docs_dir.exists():
        raise FileNotFoundError(f"Directory not found: {docs_path}")
    
    all_text = []
    supported_extensions = ['.txt', '.md', '.pdf', '.docx']
    
    for file_path in docs_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                text = parse_document(file_path)
                all_text.append(f"\n\n=== {file_path.name} ===\n{text}")
                print(f"✓ Parsed {file_path.name}")
            except Exception as e:
                print(f"⚠ Failed to parse {file_path.name}: {e}")
                continue
    
    if not all_text:
        raise ValueError(f"No parseable documents found in {docs_path}")
    
    return "\n\n".join(all_text)


def extract_business_context(documents_text: str) -> BusinessContext:
    """
    Use LLM to extract structured business context from documents.
    
    Args:
        documents_text: Concatenated document text
        
    Returns:
        Structured BusinessContext dict
    """
    llm = get_llm("analysis")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert brand strategist and content analyst. Extract comprehensive business context from the provided documents to enable varied, on-brand content creation.

Extract the following structured sections:

## 1. BRAND IDENTITY
- core_narrative: A detailed 3-4 paragraph narrative capturing the brand's origin story, mission, vision, and core values. This should be rich enough to inform content for months without updates.
- brand_pillars: 3-5 foundational pillars that support the brand (e.g., ["community empowerment", "financial sovereignty", "memetic culture"])
- unique_value_proposition: What makes this brand uniquely different in the Web3/crypto space
- brand_personality_traits: 5-7 personality traits (e.g., ["bold", "connecting", "memetic", "empathetic", "rebellious"])
- brand_archetype: Primary brand archetype (e.g., "Rebel", "Creator", "Sage", "Jester", "Hero")

## 2. COMMUNICATION STYLE
- tone_descriptors: Array of 5-7 descriptors (e.g., ["connecting", "memetic", "empathetic", "witty", "technical"])
- voice_characteristics: Detailed description of how the brand speaks (sentence structure, vocabulary level, formality)
- humor_style: Type of humor used (e.g., "self-aware irony with wordplay, memetic references, and community inside jokes")
- example_phrases: 5-10 actual phrases from the documents that exemplify the brand voice
- language_patterns: Recurring linguistic patterns (e.g., "uses rhetorical questions, references pop culture, embraces internet slang")

## 3. STRATEGIC MESSAGING
- key_messages: 5-7 core messages to consistently communicate
- messaging_frameworks: Object with keys "educational", "promotional", "community", "reactive" - each describing how to message in that context
- content_themes: 5-8 recurring themes to explore (e.g., ["financial freedom", "community wins", "market education", "meme culture"])

## 4. AUDIENCE INTELLIGENCE
- primary_audience: Detailed demographic and psychographic profile
- psychographics: Values, motivations, pain points, aspirations of the audience
- expertise_level: Technical/crypto knowledge level (e.g., "intermediate - familiar with DeFi basics but not advanced protocols")
- engagement_preferences: What type of content resonates (e.g., "visual memes, data-driven insights, community celebrations")

## 5. BRAND GUARDRAILS
- dos: Array of 5-7 things the brand SHOULD do in communications
- donts: Array of 5-7 things the brand should NEVER do
- sensitive_topics: Topics to handle carefully or avoid
- competitor_mentions: Policy on mentioning competitors (e.g., "acknowledge respectfully but focus on our strengths")

## 6. CONTENT VARIATION SEEDS
- perspectives: 5-7 different angles to approach content (e.g., ["technical educator", "community cheerleader", "market analyst", "meme lord", "visionary"])
- narrative_approaches: Different storytelling modes (e.g., ["data-driven", "personal stories", "provocative questions", "celebration posts", "educational threads"])
- emotional_ranges: Emotional tones to vary between (e.g., ["confident", "curious", "triumphant", "empathetic", "playful", "serious"])

Return ONLY a valid JSON object with these 6 top-level keys: brand_identity, communication_style, strategic_messaging, audience_intelligence, brand_guardrails, content_variation_seeds. 

Each should be an object with the sub-keys listed above. No markdown, no explanation, just pure JSON."""),
        ("user", "Business Documents:\n\n{documents}\n\nExtract the comprehensive business context as JSON:")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"documents": documents_text})
    
    # Parse JSON response
    import json
    content = response.content.strip()
    
    # Remove markdown code blocks if present
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    context_dict = json.loads(content)
    
    return BusinessContext(**context_dict)


def business_context_node(state: GraphState) -> GraphState:
    """
    Node 1: Parse and analyze business documents to extract brand context.
    
    This node:
    - Recursively scans business_documents/ folder
    - Parses .txt, .md, .pdf, .docx files
    - Uses LLM to extract structured context
    - Implements caching (cache invalidates when files change)
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with business_context populated
    """
    print("\n📚 NODE 1: Business Context Ingestion")
    print("=" * 50)
    
    docs_path = state["config"].get(
        "business_documents_path",
        os.getenv("BUSINESS_DOCS_PATH", "./business_documents")
    )
    
    force_refresh = state["config"].get("force_refresh_context", False)
    
    # Check cache first
    if not force_refresh:
        docs_hash = get_docs_hash(docs_path)
        cached = load_cached_business_context(docs_hash)
        
        if cached:
            print("✓ Using cached business context")
            state["business_context"] = cached
            return state
    
    # Parse all documents
    print(f"📄 Parsing documents from: {docs_path}")
    documents_text = parse_all_documents(docs_path)
    
    print(f"📊 Extracted {len(documents_text)} characters of text")
    
    # Extract context with LLM
    print("🤖 Analyzing with LLM...")
    context = extract_business_context(documents_text)
    
    print(f"✓ Extracted business context:")
    print(f"  - Brand Archetype: {context.get('brand_identity', {}).get('brand_archetype', 'N/A')}")
    print(f"  - Tone: {', '.join(context.get('communication_style', {}).get('tone_descriptors', [])[:3])}")
    print(f"  - Key Themes: {len(context.get('strategic_messaging', {}).get('content_themes', []))}")
    
    # Save to cache
    docs_hash = get_docs_hash(docs_path)
    save_business_context_cache(docs_hash, context)
    
    state["business_context"] = context
    return state
