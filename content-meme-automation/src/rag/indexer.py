"""RAG Indexer: Ingest brand_knowledge/ docs into a persistent FAISS vector store.

This module is responsible for:
- Recursively scanning brand_knowledge/ for .txt, .md, .pdf, .docx files
- Splitting documents into chunks
- Embedding chunks via OpenAI text-embedding-3-small
- Persisting the FAISS index to .cache/rag_index/

The index is rebuilt only when file content has changed (hash-based check).
"""
import hashlib
import json
import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ── Constants ─────────────────────────────────────────────────────────────────
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
CHUNK_SIZE = 500          # tokens ≈ characters / 4 — generous for brand context
CHUNK_OVERLAP = 80


def _get_embedding_model() -> OpenAIEmbeddings:
    """Return OpenAI embeddings model (text-embedding-3-small)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not set. Required for RAG embeddings. "
            "Add it to your .env file."
        )
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key,
    )


def _compute_knowledge_hash(knowledge_path: Path) -> str:
    """Hash all file names + modification times in brand_knowledge/."""
    files = sorted(knowledge_path.rglob("*"))
    fingerprint = "".join(
        f.name + str(f.stat().st_mtime)
        for f in files
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return hashlib.md5(fingerprint.encode()).hexdigest()


def _load_document(file_path: Path) -> List[Document]:
    """Load a single document into LangChain Document objects."""
    suffix = file_path.suffix.lower()
    try:
        if suffix in {".txt", ".md"}:
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs = loader.load()
        elif suffix == ".pdf":
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
        elif suffix == ".docx":
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(str(file_path))
            docs = loader.load()
        else:
            return []

        # Tag each document with its source path for debugging
        for doc in docs:
            doc.metadata["source"] = str(file_path)
            doc.metadata["category"] = file_path.parent.name  # e.g. "brand_identity"
        return docs

    except Exception as e:
        print(f"    ⚠️  Could not load {file_path.name}: {e}")
        return []


def _ingest_all_documents(knowledge_path: Path) -> List[Document]:
    """Load and chunk all documents from brand_knowledge/."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: List[Document] = []
    file_count = 0

    for file_path in sorted(knowledge_path.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        # Skip the folder READMEs (they're meta, not brand content)
        if file_path.name.lower() == "readme.md" and file_path.parent != knowledge_path:
            continue

        raw_docs = _load_document(file_path)
        if not raw_docs:
            continue

        chunks = splitter.split_documents(raw_docs)
        all_chunks.extend(chunks)
        file_count += 1
        print(f"    ✓ {file_path.relative_to(knowledge_path)}  →  {len(chunks)} chunks")

    print(f"\n    📦 Total: {file_count} files  →  {len(all_chunks)} chunks")
    return all_chunks


def build_index(
    knowledge_path: Path,
    index_path: Path,
    force: bool = False,
) -> FAISS:
    """
    Build (or load) the FAISS vector store.

    Args:
        knowledge_path: Path to brand_knowledge/ directory
        index_path: Where to persist the FAISS index
        force: If True, always rebuild even if hash matches

    Returns:
        Loaded FAISS vector store
    """
    # ── Hash check ──────────────────────────────────────────────────────────
    hash_file = index_path / "knowledge_hash.txt"
    current_hash = _compute_knowledge_hash(knowledge_path)

    if not force and index_path.exists() and hash_file.exists():
        stored_hash = hash_file.read_text().strip()
        if stored_hash == current_hash:
            print("  ✓ RAG index is up-to-date — loading from cache")
            embeddings = _get_embedding_model()
            return FAISS.load_local(
                str(index_path),
                embeddings,
                allow_dangerous_deserialization=True,
            )

    # ── Build ────────────────────────────────────────────────────────────────
    print(f"  🔨 Building RAG index from: {knowledge_path}")
    chunks = _ingest_all_documents(knowledge_path)

    if not chunks:
        raise ValueError(
            f"No documents found in {knowledge_path}. "
            "Add .txt, .md, .pdf, or .docx files to brand_knowledge/."
        )

    print(f"\n  🔗 Embedding {len(chunks)} chunks with OpenAI text-embedding-3-small ...")
    embeddings = _get_embedding_model()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # ── Persist ──────────────────────────────────────────────────────────────
    index_path.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(index_path))
    hash_file.write_text(current_hash)
    print(f"  💾 Index saved to: {index_path}")

    return vectorstore
