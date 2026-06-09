#!/usr/bin/env python3
"""Run the dashboard pipeline (AC + TC + Trello publish + Sheets append) for one card.

Usage:
    PYTHONPATH=. .venv/bin/python scripts/process_mcsl381_card.py <card_id_or_url> [--release "MCSL 381"]
"""
from __future__ import annotations

import argparse
import re
import sys
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: F401  loads .env

from pipeline.trello_client import TrelloClient
from pipeline.card_processor import (
    generate_acceptance_criteria,
    generate_test_cases,
    write_test_cases_to_card,
    get_last_ac_review,
)
from pipeline.requirement_research import build_requirement_research_context


def _card_ref(value: str) -> str:
    value = (value or "").strip()
    m = re.search(r"trello\.com/c/([^/?#\s]+)", value)
    if m:
        return m.group(1)
    return value.rstrip("/").split("/")[-1] if value.startswith("http") else value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("card", help="Trello card id, shortlink, or URL")
    parser.add_argument("--release", default="MCSL 381")
    parser.add_argument("--skip-trello-ac", action="store_true", help="Do not post AC comment")
    parser.add_argument("--skip-trello-tc", action="store_true", help="Do not post TC comment")
    parser.add_argument("--skip-sheets", action="store_true", help="Do not append to Sheets")
    parser.add_argument("--dry-run", action="store_true", help="Generate but do not publish anywhere")
    args = parser.parse_args()

    trello = TrelloClient()
    card = trello.get_card(_card_ref(args.card))

    print(f"\n=== Card: {card.name}")
    print(f"URL: {card.url}")
    print(f"Labels: {card.labels}")

    raw = f"{card.name}\n\n{card.desc or ''}".strip()
    comments = "\n".join(getattr(card, "comments", []) or [])
    labels_text = "\n".join(getattr(card, "labels", []) or [])

    print("\n[1/4] Building requirement research context…")
    research = build_requirement_research_context(f"{raw}\n{labels_text}".strip())

    print("[2/4] Generating User Story & AC…")
    ac_markdown = generate_acceptance_criteria(
        raw_request=raw,
        attachments=card.attachments or None,
        checklists=card.checklists or None,
        research_context=research,
        comments_context=comments,
        labels=card.labels or [],
        labels_context=labels_text,
        review=True,
    )
    review_meta = get_last_ac_review()
    print(f"   AC length: {len(ac_markdown)} chars; review: {review_meta.get('summary','')[:120]}")

    print("[3/4] Generating Test Cases…")
    tc_markdown = generate_test_cases(card, ac_text=ac_markdown, labels_context=labels_text)
    print(f"   TC length: {len(tc_markdown)} chars")

    if args.dry_run:
        print("\n--- AC ---\n" + ac_markdown)
        print("\n--- TC ---\n" + tc_markdown[:3000])
        return 0

    print("[4/4] Publishing…")
    if not args.skip_trello_ac:
        ac_comment = (
            f"## Acceptance Criteria — {args.release}\n"
            f"_Generated via MCSL pipeline (mcsl-ac-writer-reviewer)._\n\n"
            + ac_markdown
        )
        trello.add_comment(card.id, ac_comment)
        print("   ✓ AC posted as Trello comment")
    else:
        print("   – AC Trello comment skipped")

    if not args.skip_trello_tc:
        write_test_cases_to_card(
            card_id=card.id,
            test_cases=tc_markdown,
            trello=trello,
            release=args.release,
            card_name=card.name,
        )
        print("   ✓ TCs posted as Trello comment")
    else:
        print("   – TC Trello comment skipped")

    if not args.skip_sheets:
        try:
            from pipeline.sheets_writer import append_to_sheet, create_new_tab

            tab_name = args.release.replace("PROD ", "").strip()
            try:
                create_new_tab(tab_name)
            except Exception as e:
                # ok if tab exists
                print(f"   (create_new_tab: {e})")
            result = append_to_sheet(
                card_name=card.name,
                test_cases_markdown=tc_markdown,
                epic=card.name,
                tab_name=tab_name,
                release=args.release,
                card_url=card.url,
            )
            print(f"   ✓ Sheets append: tab={result.get('tab')} rows_added={result.get('rows_added')} url={result.get('sheet_url')}")
        except Exception as e:
            print(f"   ✗ Sheets append failed: {e}")
            traceback.print_exc()
    else:
        print("   – Sheets append skipped")

    print(f"\nDONE: {card.name}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
