# Brand Knowledge Base

This folder is the single source of truth for all Rekt CEO brand knowledge.
The RAG system (`src/rag/`) indexes every file here so any flow can query it.

## Adding new documents

1. Drop a `.txt`, `.md`, `.pdf`, or `.docx` file in the appropriate subfolder below
2. Re-run the ingest script from the project root:
   ```bash
   python scripts/ingest_brand_knowledge.py
   ```
3. Done — the FAISS index in `.cache/rag_index/` will be rebuilt automatically.

No code changes needed.

---

## Folder Structure

| Folder | What belongs here |
|---|---|
| `brand_identity/` | Core brand docs, brand briefs, origin story |
| `visuals/` | Color palette, typography, graphic guidelines |
| `voice_and_tone/` | Writing samples, tone guides, example social posts |
| `ceo_content/` | CEO bio, interview transcripts, personal brand notes |
| `campaigns/` | Past campaign briefs, what worked / what didn't |
| `competitors/` | Competitor analysis (used for guardrail avoidance) |
| `audience/` | Audience personas, psychographic research |

---

## How it works

Each subfolder is recursively scanned. Documents are chunked into ~400-token
passages and embedded with OpenAI `text-embedding-3-small`. Nodes query the
index with a natural-language question and receive the most relevant passages.

The index auto-invalidates whenever file names or modification timestamps change.
