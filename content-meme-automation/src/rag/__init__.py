"""RAG module for Rekt CEO brand knowledge retrieval.

Usage (from any node):
    from ..rag import query_brand_context

    context = query_brand_context("Rekt CEO brand tone and voice")
"""
from .retriever import query_brand_context, get_retriever

__all__ = ["query_brand_context", "get_retriever"]
