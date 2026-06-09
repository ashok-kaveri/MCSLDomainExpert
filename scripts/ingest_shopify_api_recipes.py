"""Ingest docs/MCSL_SHOPIFY_API_RATE_SHOPPING.md into the RAG vector store
under source_type='shopify_api_recipes'.

Chunks by markdown H2/H3 sections so each retrievable chunk is a coherent
recipe (Add Market, Trigger rates via draftOrderCalculate, etc.). Re-ingesting
deletes the previous shopify_api_recipes chunks first so this script is
idempotent — safe to re-run after edits to the doc.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

# Allow `python scripts/ingest_shopify_api_recipes.py` from repo root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langchain_core.documents import Document

from rag.vectorstore import (
    delete_by_source_type,
    get_source_count,
    upsert_documents,
)

DOC_PATH    = ROOT / "docs" / "MCSL_SHOPIFY_API_RATE_SHOPPING.md"
SOURCE_TYPE = "shopify_api_recipes"
SOURCE_NAME = "docs:MCSL_SHOPIFY_API_RATE_SHOPPING.md"


def chunk_by_heading(text: str) -> list[tuple[str, str]]:
    """Split a markdown doc into (heading, body) chunks at H2 (`## `) boundaries.

    H3 (`### `) sub-sections are kept inside the parent H2 chunk so each chunk
    has enough context to stand alone in retrieval. EXCEPT when an H2 chunk
    grows past ``MAX_CHARS`` — Ollama's nomic-embed-text caps inputs at ~2048
    tokens (~8000 chars). In that case, split the oversized H2 chunk at its
    H3 boundaries so each sub-chunk fits.
    """
    MAX_CHARS = 6000  # leave headroom under the ~8000-char embedding limit

    # First pass: split at H2 boundaries
    lines = text.splitlines()
    h2_chunks: list[tuple[str, str]] = []
    current_heading = "Preamble"
    buf: list[str] = []
    for line in lines:
        if line.startswith("## ") and not line.startswith("### "):
            if buf:
                h2_chunks.append((current_heading, "\n".join(buf).strip()))
            current_heading = line.lstrip("#").strip()
            buf = [line]
        else:
            buf.append(line)
    if buf:
        h2_chunks.append((current_heading, "\n".join(buf).strip()))

    # Second pass: split any oversized H2 chunk at H3 boundaries
    out: list[tuple[str, str]] = []
    for heading, body in h2_chunks:
        if not body:
            continue
        if len(body) <= MAX_CHARS:
            out.append((heading, body))
            continue
        # Sub-split at H3
        sub_heading = heading
        sub_buf: list[str] = []
        for line in body.splitlines():
            if line.startswith("### "):
                if sub_buf:
                    out.append((sub_heading, "\n".join(sub_buf).strip()))
                sub_heading = f"{heading} — {line.lstrip('#').strip()}"
                sub_buf = [line]
            else:
                sub_buf.append(line)
        if sub_buf:
            out.append((sub_heading, "\n".join(sub_buf).strip()))
    return [(h, b) for h, b in out if b]


def chunk_id(heading: str) -> str:
    """Stable id per heading so re-ingesting upserts rather than duplicates."""
    slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
    h = hashlib.sha1(f"{SOURCE_NAME}:{heading}".encode()).hexdigest()[:8]
    return f"{SOURCE_TYPE}:{slug}:{h}"


def main() -> int:
    if not DOC_PATH.exists():
        print(f"ERROR: {DOC_PATH} not found", file=sys.stderr)
        return 2

    text = DOC_PATH.read_text(encoding="utf-8")
    chunks = chunk_by_heading(text)
    print(f"Doc size: {len(text):,} chars → {len(chunks)} chunk(s)")

    # Clear out previous chunks for this source_type to keep things tidy
    before = get_source_count(SOURCE_TYPE)
    if before:
        deleted = delete_by_source_type(SOURCE_TYPE)
        print(f"Removed {deleted} pre-existing chunk(s) from source_type='{SOURCE_TYPE}'")

    docs: list[Document] = []
    ids: list[str] = []
    for heading, body in chunks:
        cid = chunk_id(heading)
        docs.append(Document(
            page_content=body,
            metadata={
                "source":      SOURCE_NAME,
                "source_type": SOURCE_TYPE,
                "heading":     heading,
                "doc_path":    str(DOC_PATH.relative_to(ROOT)),
            },
        ))
        ids.append(cid)
        print(f"  + {cid:60s}  {heading}")

    upsert_documents(docs, ids)

    after = get_source_count(SOURCE_TYPE)
    print(f"\nDone. source_type='{SOURCE_TYPE}' now has {after} chunk(s) in the vector store.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
