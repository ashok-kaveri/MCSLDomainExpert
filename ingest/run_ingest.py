#!/usr/bin/env python3
"""
MCSL Domain Expert — Master Ingestion Pipeline
================================================
Ingests all knowledge sources into ChromaDB:
  - kb_articles       → mcsl_knowledge (26 KB article .md files from docs/kb_snapshots/)
  - sheets            → mcsl_knowledge (MCSL TC Google Sheet, all tabs)
  - wiki              → mcsl_knowledge (241 docs from mcsl-wiki/wiki/)
  - storepepsaas_server → mcsl_code_knowledge (server/src/shared/ .js files)
  - storepepsaas_client → mcsl_code_knowledge (client/src/ .js/.jsx files)
  - automation        → mcsl_code_knowledge (mcsl-test-automation .ts/.js/.md files)

Each doc source: delete_by_source_type() first, then add_documents() (prevents duplicates on re-run).
Each code source: index_codebase(clear_existing=True) (handles delete internally).

Usage:
    python ingest/run_ingest.py                                        # All 6 sources
    python ingest/run_ingest.py --sources kb_articles                  # Only KB articles
    python ingest/run_ingest.py --sources wiki automation              # Two sources
    python ingest/run_ingest.py --sources storepepsaas_server storepepsaas_client
"""
from __future__ import annotations
import argparse
import logging
import sys
import time

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Canonical list of all supported source names (matches --sources choices)
_ALL_SOURCES = [
    "kb_articles",
    "sheets",
    "wiki",
    "storepepsaas_server",
    "storepepsaas_client",
    "automation",
]


def run_ingest(sources: list[str] | None = None) -> None:
    """
    Run ingestion for the specified sources (or all sources if None).

    For document sources (kb_articles, sheets, wiki):
      delete_by_source_type(source_type) → load_*() → add_documents(docs)

    For code sources (storepepsaas_server, storepepsaas_client, automation):
      index_codebase(clear_existing=True) which handles deletion internally.

    Args:
        sources: List of source names to ingest. None means all 6 sources.
    """
    from rag.vectorstore import delete_by_source_type, add_documents
    from rag.code_indexer import index_codebase
    from ingest.kb_loader import load_kb_articles
    from ingest.sheets_loader import load_test_cases
    from ingest.wiki_loader import load_wiki_docs

    active = sources if sources is not None else _ALL_SOURCES
    start = time.time()

    print("=" * 60)
    print("MCSL Domain Expert — Knowledge Base Ingestion")
    print(f"Sources: {', '.join(active)}")
    print("=" * 60)

    # ── Document sources (→ mcsl_knowledge) ──────────────────────────────────

    if "kb_articles" in active:
        logger.info("Ingesting KB articles from docs/kb_snapshots/...")
        docs = load_kb_articles()
        logger.info("KB articles: %d chunks loaded", len(docs))
        delete_by_source_type("kb_articles")
        add_documents(docs)
        print(f"  kb_articles: {len(docs)} chunks ingested")

    if "sheets" in active:
        logger.info("Ingesting MCSL TC sheet (Google Sheets)...")
        docs = load_test_cases()
        logger.info("TC sheet: %d chunks loaded", len(docs))
        delete_by_source_type("sheets")
        add_documents(docs)
        print(f"  sheets: {len(docs)} chunks ingested")

    if "wiki" in active:
        logger.info("Ingesting MCSL wiki from %s...", config.WIKI_PATH)
        docs = load_wiki_docs()
        logger.info("Wiki: %d chunks loaded", len(docs))
        delete_by_source_type("wiki")
        add_documents(docs)
        print(f"  wiki: {len(docs)} chunks ingested")

    # ── Code sources (→ mcsl_code_knowledge) ─────────────────────────────────

    if "storepepsaas_server" in active:
        logger.info("Indexing storepepSAAS server (server/src/shared/)...")
        result = index_codebase(
            code_path=config.STOREPEPSAAS_SERVER_PATH,
            source_type="storepepsaas_server",
            extensions=[".js"],
            clear_existing=True,
        )
        logger.info("storepepsaas_server: %s", result)
        print(f"  storepepsaas_server: {result.get('chunks_added', 0)} chunks indexed")

    if "storepepsaas_client" in active:
        logger.info("Indexing storepepSAAS client (client/src/)...")
        result = index_codebase(
            code_path=config.STOREPEPSAAS_CLIENT_PATH,
            source_type="storepepsaas_client",
            extensions=[".js", ".jsx"],
            clear_existing=True,
        )
        logger.info("storepepsaas_client: %s", result)
        print(f"  storepepsaas_client: {result.get('chunks_added', 0)} chunks indexed")

    if "automation" in active:
        logger.info("Indexing mcsl-test-automation repo (skipping carrier-envs/)...")
        result = index_codebase(
            code_path=config.MCSL_AUTOMATION_REPO_PATH,
            source_type="automation",
            extensions=[".ts", ".js", ".md"],
            clear_existing=True,
        )
        logger.info("automation: %s", result)
        print(f"  automation: {result.get('chunks_added', 0)} chunks indexed")

    elapsed = time.time() - start
    print()
    print(f"Done: all sources indexed in {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rebuild MCSL Domain Expert knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--sources",
        nargs="*",
        choices=_ALL_SOURCES,
        metavar="SOURCE",
        help=(
            f"Which sources to ingest (default: all 6). "
            f"Choices: {', '.join(_ALL_SOURCES)}"
        ),
    )
    args = parser.parse_args()
    run_ingest(args.sources)
