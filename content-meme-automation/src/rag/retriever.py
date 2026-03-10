"""RAG Retriever: Query the brand knowledge vector store.

Public API used by all nodes:

    from src.rag import query_brand_context

    context_str = query_brand_context(
        "Rekt CEO brand tone, meme style, audience personality",
        k=5,
    )

The retriever is a lazy singleton — the index is only loaded the first time
query_brand_context() is called, then cached in-process.
"""
import os
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS

from .indexer import build_index


# ── Singleton state ────────────────────────────────────────────────────────────
_vectorstore: Optional[FAISS] = None


def _resolve_paths() -> tuple[Path, Path]:
    """Resolve brand_knowledge and index cache paths from env or defaults."""
    knowledge_path = Path(
        os.getenv("BRAND_KNOWLEDGE_PATH", "./brand_knowledge")
    ).resolve()
    index_path = Path(
        os.getenv("RAG_INDEX_PATH", "./.cache/rag_index")
    ).resolve()
    return knowledge_path, index_path


def _get_vectorstore(force_rebuild: bool = False) -> FAISS:
    """Return the singleton FAISS vectorstore, building it if needed."""
    global _vectorstore
    if _vectorstore is None or force_rebuild:
        knowledge_path, index_path = _resolve_paths()
        _vectorstore = build_index(
            knowledge_path=knowledge_path,
            index_path=index_path,
            force=force_rebuild,
        )
    return _vectorstore


def get_retriever(k: int = 5):
    """
    Return a LangChain retriever for use in LCEL chains.

    Args:
        k: Number of documents to retrieve per query

    Returns:
        VectorStoreRetriever
    """
    vs = _get_vectorstore()
    return vs.as_retriever(search_kwargs={"k": k})


def query_brand_context(question: str, k: int = 5) -> str:
    """
    Query the brand knowledge base and return relevant context as a string.

    This is the primary function used by all nodes. Pass a natural-language
    question describing what brand information you need and you'll get back
    the most relevant passages from the brand_knowledge/ documents.

    Args:
        question: Natural language question, e.g.
            "Rekt CEO brand tone, voice and humor style"
            "color palette and visual identity"
            "audience psychographics and crypto expertise level"
        k: Number of document chunks to retrieve (default 5)

    Returns:
        Concatenated string of the top-k most relevant passages,
        each labeled with its source file.

    Example:
        >>> ctx = query_brand_context("brand tone and meme style")
        >>> # Returns passages from Rekt_CEO_Private.txt and branding_brief.txt
    """
    vs = _get_vectorstore()
    docs = vs.similarity_search(question, k=k)

    if not docs:
        return "[No brand context retrieved — check brand_knowledge/ folder and re-run ingest]"

    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        category = doc.metadata.get("category", "")
        label = f"[{category}/{Path(source).name}]" if category else f"[{Path(source).name}]"
        parts.append(f"{label}\n{doc.page_content.strip()}")

    return "\n\n---\n\n".join(parts)


def reset_retriever() -> None:
    """Force the singleton to reload on next query (useful after re-ingesting)."""
    global _vectorstore
    _vectorstore = None
