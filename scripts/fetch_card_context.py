#!/usr/bin/env python3
"""Fetch one MCSL Trello card + all relevant RAG/research context (no LLM calls).

Usage:
    PYTHONPATH=. .venv/bin/python scripts/fetch_card_context.py <card_id_or_url>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: F401


def _card_ref(value: str) -> str:
    value = (value or "").strip()
    m = re.search(r"trello\.com/c/([^/?#\s]+)", value)
    if m:
        return m.group(1)
    return value.rstrip("/").split("/")[-1] if value.startswith("http") else value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("card")
    args = parser.parse_args()

    from pipeline.trello_client import TrelloClient

    trello = TrelloClient()
    card = trello.get_card(_card_ref(args.card))

    print(f"### CARD")
    print(f"ID: {card.id}")
    print(f"URL: {card.url}")
    print(f"NAME: {card.name}")
    print(f"LABELS: {card.labels}")
    print()
    print(f"### DESCRIPTION")
    print(card.desc or "(empty)")
    print()
    print(f"### CHECKLISTS")
    for cl in card.checklists or []:
        print(f"- {cl.get('name','')}")
        for item in cl.get("items", []) or []:
            print(f"   • [{item.get('state','')}] {item.get('name','')}")
    print()
    print(f"### ATTACHMENTS")
    for a in card.attachments or []:
        print(f"- {a.get('name','')} -> {a.get('url','')}")
    print()
    print(f"### COMMENTS ({len(card.comments or [])})")
    for i, c in enumerate(card.comments or [], 1):
        print(f"--- Comment {i} ---")
        print(c[:2500])
    print()

    raw = f"{card.name}\n\n{card.desc or ''}".strip()
    labels_text = "\n".join(card.labels or [])

    print(f"### CARRIER RESEARCH CONTEXT")
    try:
        from pipeline.carrier_knowledge import carrier_research_context, detect_carrier_scope

        scope = detect_carrier_scope(card.name, card.desc or "", labels_text)
        print(f"detected carriers: {[c.name for c in scope.matched]}")
        ctx = carrier_research_context(card.name, card.desc or "", "\n".join(card.comments or []), labels_text)
        print(ctx[:5000])
    except Exception as e:
        print(f"(error: {e})")
    print()

    print(f"### REQUIREMENT RESEARCH CONTEXT")
    try:
        from pipeline.requirement_research import build_requirement_research_context

        rc = build_requirement_research_context(f"{raw}\n{labels_text}".strip())
        print(rc[:6000])
    except Exception as e:
        print(f"(error: {e})")
    print()

    print(f"### RAG VECTORSTORE HITS (top 5)")
    try:
        from rag.vectorstore import search

        for doc in search(raw, k=5):
            meta = doc.metadata or {}
            print(f"- [{meta.get('source_type','?')}] {meta.get('source','?')}")
            print(f"   {doc.page_content[:400].replace(chr(10),' / ')}")
    except Exception as e:
        print(f"(error: {e})")
    print()

    print(f"### CODE INDEX HITS (top 5)")
    try:
        from rag.code_indexer import search_code

        for doc in search_code(raw, k=5):
            meta = doc.metadata or {}
            print(f"- {meta.get('file_path','?')}:{meta.get('start_line','?')}")
            print(f"   {doc.page_content[:400].replace(chr(10),' / ')}")
    except Exception as e:
        print(f"(error: {e})")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
