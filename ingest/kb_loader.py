"""
KB Loader
=========
Reads all Markdown files from docs/kb_snapshots/ and returns chunked
LangChain Documents ready for indexing into ChromaDB (mcsl_knowledge).

Each article becomes one or more chunks tagged with:
  source_type : "kb_articles"
  source      : "kb_articles:{filename}"
  file_name   : original .md filename
  chunk_index : 0, 1, 2, ...
"""
from __future__ import annotations
import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

logger = logging.getLogger(__name__)


def load_kb_articles() -> list[Document]:
    """
    Walk docs/kb_snapshots/, read every .md file, chunk the content,
    and return LangChain Documents tagged with source_type='kb_articles'.

    Returns an empty list (with a warning) if the directory doesn't exist.
    Skips files with fewer than 50 characters of content.
    """
    kb_dir = config.BASE_DIR / "docs" / "kb_snapshots"
    if not kb_dir.exists():
        logger.warning("KB snapshots dir not found: %s — skipping kb_articles ingestion", kb_dir)
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )

    documents: list[Document] = []
    files_read = 0
    files_skipped = 0

    for md_file in sorted(kb_dir.glob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace").strip()
        except Exception as e:
            logger.warning("Could not read KB file %s: %s", md_file, e)
            continue

        if len(text) < 50:
            files_skipped += 1
            continue

        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "source":      f"kb_articles:{md_file.name}",
                    "source_url":  f"kb_articles:{md_file.name}",
                    "source_type": "kb_articles",
                    "file_name":   md_file.name,
                    "chunk_index": i,
                },
            ))

        files_read += 1
        logger.debug("KB: %s → %d chunks", md_file.name, len(chunks))

    logger.info(
        "KB loader: %d files read, %d files skipped → %d total chunks",
        files_read, files_skipped, len(documents),
    )
    return documents
