"""
RAG Auto-Updater
================
Embeds approved Trello card ACs and test cases into the mcsl_knowledge
ChromaDB collection after each sprint cycle.

Uses stable document IDs so re-running for the same card replaces
(not duplicates) the previous content.

Usage:
    from pipeline.rag_updater import embed_trello_card

    embed_trello_card(
        card_id="CARD-123",
        ac_text="Given the user has a FedEx account...",
        test_cases_text="TC-01: Verify label generated...",
    )
"""
from __future__ import annotations
import logging
import re
from langchain_core.documents import Document
from rag.vectorstore import upsert_documents

logger = logging.getLogger(__name__)

_MAX_CHUNK_CHARS = 3000


def _chunk_test_cases(text: str) -> list[str]:
    """Split TC markdown into per-TC blocks so each fits the embedding context window."""
    if not text:
        return []
    blocks = re.split(r"(?=^### TC-)", text, flags=re.MULTILINE)
    chunks = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # If a single block somehow exceeds the limit, split by newlines as fallback
        if len(block) > _MAX_CHUNK_CHARS:
            for i in range(0, len(block), _MAX_CHUNK_CHARS):
                chunks.append(block[i:i + _MAX_CHUNK_CHARS])
        else:
            chunks.append(block)
    return chunks or [text[:_MAX_CHUNK_CHARS]]


def embed_trello_card(
    card_id: str,
    ac_text: str,
    test_cases_text: str,
) -> None:
    """
    Embed a Trello card's AC and test cases into mcsl_knowledge using
    stable IDs so repeated calls replace rather than duplicate content.

    Args:
        card_id:         Unique Trello card identifier (e.g. "CARD-123")
        ac_text:         Full acceptance criteria text from the card
        test_cases_text: Full test cases text associated with the card
    """
    ac_id         = f"{card_id}__ac"
    test_cases_id = f"{card_id}__test_cases"

    docs: list[Document] = [
        Document(
            page_content=ac_text or f"[No AC text provided for {card_id}]",
            metadata={
                "source_type":  "trello_card",
                "source":       f"trello:{card_id}:ac",
                "source_url":   f"trello:{card_id}",
                "card_id":      card_id,
                "content_type": "ac",
                "chunk_index":  0,
            },
        ),
    ]
    ids = [ac_id]

    for i, chunk in enumerate(_chunk_test_cases(test_cases_text)):
        docs.append(Document(
            page_content=chunk,
            metadata={
                "source_type":  "trello_card",
                "source":       f"trello:{card_id}:test_cases",
                "source_url":   f"trello:{card_id}",
                "card_id":      card_id,
                "content_type": "test_cases",
                "chunk_index":  i,
            },
        ))
        ids.append(f"{test_cases_id}__{i}")

    upsert_documents(docs, ids=ids)
    logger.info("Embedded Trello card %s (AC + test cases) into mcsl_knowledge", card_id)


def update_rag_from_card(
    *,
    card_id: str,
    card_name: str,
    description: str = "",
    acceptance_criteria: str = "",
    test_cases: str = "",
    release: str = "",
) -> dict:
    """Upsert approved card artifacts with stable IDs.

    This is the richer card-cycle API used by Codex/Claude skills. It keeps the
    old AC/test-case behavior while also storing the original card description.
    """
    docs: list[Document] = []
    ids: list[str] = []

    docs.append(Document(
        page_content=description or f"[No description provided for {card_id}]",
        metadata={
            "source_type": "trello_card",
            "source": f"trello:{card_id}:description",
            "source_url": f"trello:{card_id}",
            "card_id": card_id,
            "card_name": card_name,
            "release": release,
            "content_type": "description",
            "chunk_index": 0,
        },
    ))
    ids.append(f"{card_id}__description")

    docs.append(Document(
        page_content=acceptance_criteria or f"[No AC text provided for {card_id}]",
        metadata={
            "source_type": "trello_card",
            "source": f"trello:{card_id}:ac",
            "source_url": f"trello:{card_id}",
            "card_id": card_id,
            "card_name": card_name,
            "release": release,
            "content_type": "ac",
            "chunk_index": 0,
        },
    ))
    ids.append(f"{card_id}__ac")

    tc_chunks = _chunk_test_cases(test_cases)
    for i, chunk in enumerate(tc_chunks):
        docs.append(Document(
            page_content=chunk,
            metadata={
                "source_type": "trello_card",
                "source": f"trello:{card_id}:test_cases",
                "source_url": f"trello:{card_id}",
                "card_id": card_id,
                "card_name": card_name,
                "release": release,
                "content_type": "test_cases",
                "chunk_index": i,
            },
        ))
        ids.append(f"{card_id}__test_cases__{i}")

    upsert_documents(docs, ids=ids)
    logger.info("Updated approved card RAG for %s (%d chunks)", card_id, len(docs))
    return {
        "chunks_added": len(docs),
        "ids": [
            f"{card_id}__description",
            f"{card_id}__ac",
            f"{card_id}__test_cases",
        ],
        "error": "",
    }
