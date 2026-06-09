#!/usr/bin/env python3
"""Publish pre-written AC and TC markdown for one MCSL card.

Posts:
  - AC as a plain Trello comment (with header)
  - TCs via write_test_cases_to_card (dashboard-formatted comment)
  - Positive TC rows appended to Google Sheet tab (release)

No LLM calls. Pure publishing.

Usage:
    PYTHONPATH=. .venv/bin/python scripts/publish_ac_tc.py \\
        --card <card_id_or_url> \\
        --ac-file path/to/ac.md \\
        --tc-file path/to/tc.md \\
        [--release "MCSL 381"] [--skip-sheets] [--skip-trello-ac] [--skip-trello-tc]
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

import config  # noqa: F401


def _card_ref(value: str) -> str:
    value = (value or "").strip()
    m = re.search(r"trello\.com/c/([^/?#\s]+)", value)
    if m:
        return m.group(1)
    return value.rstrip("/").split("/")[-1] if value.startswith("http") else value


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--card", required=True)
    p.add_argument("--ac-file", required=True)
    p.add_argument("--tc-file", required=True)
    p.add_argument("--release", default="MCSL 381")
    p.add_argument("--skip-trello-ac", action="store_true")
    p.add_argument("--skip-trello-tc", action="store_true")
    p.add_argument("--skip-sheets", action="store_true")
    args = p.parse_args()

    ac_md = Path(args.ac_file).read_text(encoding="utf-8")
    tc_md = Path(args.tc_file).read_text(encoding="utf-8")

    from pipeline.trello_client import TrelloClient
    from pipeline.card_processor import write_test_cases_to_card

    trello = TrelloClient()
    card = trello.get_card(_card_ref(args.card))
    print(f"Card: {card.name}\nURL: {card.url}")

    if not args.skip_trello_ac:
        ac_comment = (
            f"## Acceptance Criteria — {args.release}\n"
            f"_Generated via MCSL AC Writer & Reviewer skill (mcsl-ac-writer-reviewer)._\n\n"
            + ac_md
        )
        trello.add_comment(card.id, ac_comment)
        print("✓ AC comment posted")

    if not args.skip_trello_tc:
        write_test_cases_to_card(
            card_id=card.id,
            test_cases=tc_md,
            trello=trello,
            release=args.release,
            card_name=card.name,
        )
        print("✓ TC comment posted")

    if not args.skip_sheets:
        try:
            from pipeline.sheets_writer import append_to_sheet, create_new_tab

            tab = args.release.replace("PROD ", "").strip()
            try:
                create_new_tab(tab)
            except Exception as e:
                print(f"(create_new_tab: {e})")
            r = append_to_sheet(
                card_name=card.name,
                test_cases_markdown=tc_md,
                epic=card.name,
                tab_name=tab,
                release=args.release,
                card_url=card.url,
            )
            print(f"✓ Sheets: tab={r.get('tab')} rows={r.get('rows_added')} url={r.get('sheet_url')}")
        except Exception as e:
            print(f"✗ Sheets failed: {e}")
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
