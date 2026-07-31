"""Rebuild ONLY the index table of the lane-382 support guide to add a Trello
card link column, then re-render the PDF. No per-card LLM regeneration — the
already-generated body sections in the .md are left untouched.
"""
from __future__ import annotations

import re
from pathlib import Path

import config  # noqa: F401 — loads .env
from pipeline import handoff_docs as hd
from pipeline.support_guide_slack import _client, _ctx_for, _find_lane, _full_card
from tmp.gen_lane_382_support_guide import (
    EXCLUDE_SHORTLINKS,
    LANE_NAME,
    OUT_DIR,
    SLUG,
    _shortlink,
    _summary_table_with_links,
)

MD_PATH = OUT_DIR / f"{SLUG}.md"
PDF_PATH = OUT_DIR / f"{SLUG}.pdf"


def main() -> None:
    client = _client()
    lane = _find_lane(client, LANE_NAME)
    cards = client.get_cards_in_list(lane.id)
    kept = [c for c in cards if _shortlink(c) not in EXCLUDE_SHORTLINKS]

    # Build contexts only (local detectors + Trello fetch; no LLM).
    ctxs = [_ctx_for(client, _full_card(client, c), release_name=lane.name) for c in kept]
    new_table = _summary_table_with_links(ctxs)

    md = MD_PATH.read_text()
    # Replace the table block between the index heading and the next H2.
    pattern = re.compile(
        r"(## Included Story Cards\n).*?(\n## How Support Should Use This Package)",
        re.DOTALL,
    )
    if not pattern.search(md):
        raise SystemExit("Could not locate the index table block in the markdown.")
    md = pattern.sub(lambda m: m.group(1) + new_table + m.group(2), md)

    MD_PATH.write_text(md)
    title = f"{lane.name} Support Guide"
    PDF_PATH.write_bytes(hd.render_pdf_bytes(title, md))
    print(f"Index rebuilt with Trello link column for {len(ctxs)} cards.")
    print("Markdown written:", MD_PATH)
    print("PDF written:", PDF_PATH)


if __name__ == "__main__":
    main()
