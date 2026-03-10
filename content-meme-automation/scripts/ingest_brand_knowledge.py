#!/usr/bin/env python3
"""
Ingest Brand Knowledge — rebuild the RAG FAISS index from brand_knowledge/

Usage:
    python scripts/ingest_brand_knowledge.py           # Incremental (skip if unchanged)
    python scripts/ingest_brand_knowledge.py --force   # Force full rebuild
"""
import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

def main():
    parser = argparse.ArgumentParser(description="Rebuild the Rekt CEO brand knowledge RAG index.")
    parser.add_argument("--force", "-f", action="store_true", help="Force full rebuild even if documents haven't changed.")
    parser.add_argument("--knowledge-path", default=os.getenv("BRAND_KNOWLEDGE_PATH", "./brand_knowledge"))
    args = parser.parse_args()

    knowledge_path = Path(args.knowledge_path).resolve()
    index_path = Path(os.getenv("RAG_INDEX_PATH", "./.cache/rag_index")).resolve()

    print("=" * 60)
    print("🧠 REKT CEO BRAND KNOWLEDGE INGEST")
    print("=" * 60)
    print(f"  Knowledge base: {knowledge_path}")
    print(f"  Index path:     {index_path}")
    print(f"  Force rebuild:  {args.force}")
    print()

    if not knowledge_path.exists():
        print(f"❌ Knowledge path not found: {knowledge_path}")
        print("   Create the brand_knowledge/ directory and add your documents.")
        sys.exit(1)

    try:
        from src.rag.indexer import build_index
        build_index(knowledge_path=knowledge_path, index_path=index_path, force=args.force)
        print()
        print("=" * 60)
        print("✅ RAG index ready!")
        print("=" * 60)
        print()
        print("Query from any node:")
        print("  from src.rag import query_brand_context")
        print('  ctx = query_brand_context("Rekt CEO brand tone and voice")')
    except Exception as e:
        print(f"\n❌ Ingest failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
