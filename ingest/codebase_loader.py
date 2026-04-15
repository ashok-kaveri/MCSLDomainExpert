"""
Codebase Loader
===============
Generic source code directory walker that returns chunked LangChain Documents.
Used as a standalone loader for code files (JS, TS, JSX, etc.).

This is a library module — run_ingest.py uses rag.code_indexer.index_codebase()
for code sources that go into mcsl_code_knowledge. This module is available as
a fallback loader or for testing purposes.

Default exclusions include carrier-envs/ which contains per-carrier credential
.env files that must never be indexed.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

logger = logging.getLogger(__name__)

# Directories to skip by default — always exclude credential dirs + build output
_DEFAULT_SKIP_DIRS: set[str] = {
    "node_modules", ".git", "dist", "build", "__pycache__",
    ".venv", "venv", "coverage",
    # MCSL-specific: carrier env files contain credentials — must never be indexed
    "carrier-envs",
    # Test output dirs
    "allure-report", "test-results", "reports",
}

_DEFAULT_EXTENSIONS: set[str] = {".ts", ".js", ".jsx", ".tsx", ".md", ".py"}

# Max file size to index (skip huge generated/minified files)
_MAX_FILE_BYTES = 100_000   # 100 KB


def load_codebase(
    path: str,
    source_type: str = "codebase",
    extensions: set | list | None = None,
    exclude_dirs: set | list | None = None,
) -> list[Document]:
    """
    Walk a code directory and return chunked LangChain Documents.

    Args:
        path:         Root directory to walk (required).
        source_type:  ChromaDB source_type tag stored in metadata.
        extensions:   File extensions to include (e.g. [".js", ".jsx"]).
                      Defaults to {".ts", ".js", ".jsx", ".tsx", ".md", ".py"}.
        exclude_dirs: Directory names to skip. Always includes carrier-envs/,
                      node_modules/, and other default exclusions. Pass additional
                      dirs to skip on top of defaults.

    Returns:
        List of chunked LangChain Document objects.
        Returns [] (not exception) if path does not exist.
    """
    root = Path(path)
    if not root.exists():
        logger.warning("Codebase path does not exist: %s — skipping", root)
        return []

    exts = set(extensions) if extensions else _DEFAULT_EXTENSIONS
    # Always include default skip dirs; caller can add more via exclude_dirs
    skip = _DEFAULT_SKIP_DIRS | (set(exclude_dirs) if exclude_dirs else set())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n\n", "\n\n", "\n", " ", ""],
    )

    documents: list[Document] = []
    files_read = 0
    files_skipped = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped dirs in-place so os.walk doesn't descend into them
        dirnames[:] = [d for d in dirnames if d not in skip]

        for fname in filenames:
            fpath = Path(dirpath) / fname

            # Extension filter
            if not any(fname.endswith(ext) for ext in exts):
                continue

            # Size filter
            try:
                size = fpath.stat().st_size
            except OSError:
                continue
            if size > _MAX_FILE_BYTES or size == 0:
                files_skipped += 1
                continue

            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")
                if len(text.strip()) < 50:
                    files_skipped += 1
                    continue

                rel = str(fpath.relative_to(root))
                chunks = splitter.split_text(text)
                for i, chunk in enumerate(chunks):
                    documents.append(Document(
                        page_content=f"// File: {rel}\n\n{chunk}",
                        metadata={
                            "source_type": source_type,
                            "file_path":   rel,
                            "source":      "codebase",
                            "chunk_index": i,
                        },
                    ))
                files_read += 1
            except Exception as e:
                logger.warning("Failed to read %s: %s", fpath, e)
                files_skipped += 1

    logger.info(
        "codebase_loader: %d files read, %d skipped → %d chunks from %s (%s)",
        files_read, files_skipped, len(documents), path, source_type,
    )
    return documents
