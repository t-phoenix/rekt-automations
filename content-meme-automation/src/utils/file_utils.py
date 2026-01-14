"""File utility functions for document parsing and caching."""
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Document parsing
from PyPDF2 import PdfReader
import docx


def get_docs_hash(docs_path: str) -> str:
    """
    Generate hash of all files in a directory for cache invalidation.
    
    Args:
        docs_path: Path to directory
        
    Returns:
        MD5 hash of file names and modification times
    """
    files = sorted(Path(docs_path).rglob("*"))
    content = "".join([
        f.name + str(f.stat().st_mtime) 
        for f in files if f.is_file()
    ])
    return hashlib.md5(content.encode()).hexdigest()


def parse_text_file(file_path: Path) -> str:
    """Parse .txt or .md file."""
    return file_path.read_text(encoding='utf-8')


def parse_pdf_file(file_path: Path) -> str:
    """Parse PDF file and extract text."""
    reader = PdfReader(str(file_path))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n\n".join(text_parts)


def parse_docx_file(file_path: Path) -> str:
    """Parse .docx file and extract text."""
    doc = docx.Document(str(file_path))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n\n".join(paragraphs)


def parse_document(file_path: Path) -> str:
    """
    Parse a document file based on extension.
    
    Args:
        file_path: Path to document
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file type is unsupported
    """
    suffix = file_path.suffix.lower()
    
    if suffix in ['.txt', '.md']:
        return parse_text_file(file_path)
    elif suffix == '.pdf':
        return parse_pdf_file(file_path)
    elif suffix == '.docx':
        return parse_docx_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def load_cache(cache_file: Path) -> Optional[Dict[str, Any]]:
    """Load JSON cache file if it exists."""
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    return None


def save_cache(cache_file: Path, data: Dict[str, Any]) -> None:
    """Save data to JSON cache file."""
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(data, indent=2))


def load_cached_with_expiry(
    cache_file: Path,
    expiry_hours: int
) -> Optional[Dict[str, Any]]:
    """
    Load cached data if it exists and hasn't expired.
    
    Args:
        cache_file: Path to cache file
        expiry_hours: Number of hours before cache expires
        
    Returns:
        Cached data or None if expired/missing
    """
    if not cache_file.exists():
        return None
        
    cache_data = json.loads(cache_file.read_text())
    
    if "cached_at" not in cache_data:
        return None
        
    cached_at = datetime.fromisoformat(cache_data["cached_at"])
    age = datetime.now() - cached_at
    
    if age < timedelta(hours=expiry_hours):
        age_minutes = age.seconds // 60
        print(f"✓ Using cached data (age: {age_minutes}min)")
        return cache_data.get("data")
    
    return None


def save_cache_with_timestamp(cache_file: Path, data: Dict[str, Any]) -> None:
    """Save data to cache with timestamp."""
    cache_data = {
        "cached_at": datetime.now().isoformat(),
        "data": data
    }
    save_cache(cache_file, cache_data)
