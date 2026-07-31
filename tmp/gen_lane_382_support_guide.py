"""One-off: combined support guide for lane "SL MCSL 382: Iteration backlog",
excluding a given set of Trello card shortlinks. Emits .md + .pdf.

Resilient version: processes one card at a time with progress logging and a
hard per-card wall-clock timeout (SIGALRM), retrying once and skipping a card
that repeatedly stalls. The combined guide is assembled from the per-card
markdown that succeeded, mirroring generate_combined_support_guide().
"""
from __future__ import annotations

import re
import signal
import sys
import time
from pathlib import Path

import config  # noqa: F401 — loads .env (Trello + Anthropic creds)
from pipeline import handoff_docs as hd
from pipeline.support_guide_slack import _client, _ctx_for, _find_lane, _full_card

LANE_NAME = "SL MCSL 382: Iteration backlog"
EXCLUDE_SHORTLINKS = {
    "2VADptWP", "1v1iwRDS", "FSugx3SX", "TuoIk6Ik", "7hF2HxYq",
    "AH1WgQnW", "I8eVHiKr", "y8vhOmoA", "8MoVg84b", "dJYpGyep",
    "8pvBqtrE", "DHqqu0p0", "Rg646lBM",
}
OUT_DIR = Path("data/handoff_docs")
SLUG = "MCSL_382_Iteration_Backlog_Support_Guide_2026-06-24"
PER_CARD_TIMEOUT = 150  # seconds, hard cap per card (context + generation)


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


signal.signal(signal.SIGALRM, _alarm)


def log(msg: str) -> None:
    print(msg, flush=True)


def _shortlink(card) -> str:
    m = re.search(r"trello\.com/c/([A-Za-z0-9]+)", card.url or "")
    return m.group(1) if m else ""


def _summary_table_with_links(ctxs) -> str:
    """Index table mirroring handoff_docs._release_summary_table, plus a Trello card column."""
    rows = [
        "| Story / card | Platform | Carrier scope | Toggle / prerequisite signal | Trello card |",
        "|---|---|---|---|---|",
    ]
    for ctx in ctxs:
        platforms = ", ".join(ctx.platform_names) if ctx.platform_names else "Shopify"
        carriers = ", ".join(ctx.carrier_names) if ctx.carrier_names else "Carrier-neutral"
        toggles = ", ".join(ctx.toggle_names) if ctx.toggle_names else "None detected"
        url = ctx.card_url or ""
        m = re.search(r"trello\.com/c/([A-Za-z0-9]+)", url)
        link = f"[{m.group(1)}]({url})" if (m and url) else (url or "—")
        rows.append(f"| {hd._doc_title(ctx)} | {platforms} | {carriers} | {toggles} | {link} |")
    return "\n".join(rows)


def _build_one(client, card, lane_name):
    """Build context + per-card guide markdown under a hard timeout. Returns (ctx, md)."""
    signal.alarm(PER_CARD_TIMEOUT)
    try:
        full = _full_card(client, card)
        ctx = _ctx_for(client, full, release_name=lane_name)
        md = hd.generate_support_guide(ctx)
        return ctx, md
    finally:
        signal.alarm(0)


def main() -> None:
    client = _client()
    lane = _find_lane(client, LANE_NAME)
    if not lane:
        raise SystemExit(f"No Trello lane/list matching “{LANE_NAME}”.")

    cards = client.get_cards_in_list(lane.id)
    if not cards:
        raise SystemExit(f"Lane “{lane.name}” has no cards.")

    kept, skipped = [], []
    for c in cards:
        (skipped if _shortlink(c) in EXCLUDE_SHORTLINKS else kept).append(c)

    log(f"Lane: {lane.name}")
    log(f"Total cards: {len(cards)} | excluded: {len(skipped)} | included: {len(kept)}")
    for c in skipped:
        log(f"  excluded  {_shortlink(c)}  {c.name}")
    if not kept:
        raise SystemExit("Nothing left after exclusions; aborting.")

    results = []        # list of (ctx, per_card_md)
    failed = []         # list of (shortlink, name)
    for i, c in enumerate(kept, 1):
        sl = _shortlink(c)
        log(f"[{i}/{len(kept)}] {sl}  {c.name[:70]} ...")
        ok = False
        for attempt in (1, 2):
            t0 = time.time()
            try:
                ctx, md = _build_one(client, c, lane.name)
                results.append((ctx, md))
                log(f"    done in {time.time() - t0:.0f}s")
                ok = True
                break
            except _Timeout:
                log(f"    timed out after {PER_CARD_TIMEOUT}s (attempt {attempt})")
            except Exception as exc:  # noqa: BLE001
                log(f"    error (attempt {attempt}): {type(exc).__name__}: {exc}")
        if not ok:
            failed.append((sl, c.name))
            log(f"    SKIPPED {sl}")

    if not results:
        raise SystemExit("No cards generated successfully; aborting.")

    # Assemble the combined guide from the per-card markdown we already have
    # (mirrors handoff_docs.generate_combined_support_guide).
    ctxs = [ctx for ctx, _ in results]
    parts = [
        f"# {lane.name} Support Guide",
        "",
        "## Included Story Cards",
        _summary_table_with_links(ctxs),
        "",
        "## How Support Should Use This Package",
        "- Use each card section as the support/demo guide for that feature.",
        "- Confirm customer/test platform, live store, carrier account, order/product, and toggle state before promising behavior.",
        "- Capture the escalation packet listed in the relevant card section if behavior does not match.",
    ]
    for ctx, md in results:
        parts.extend(["", f"## {hd._doc_title(ctx)} - {ctx.card_name}", hd._demote_markdown(md)])
    combined_md = "\n".join(p for p in parts if p is not None).strip()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_DIR / f"{SLUG}.md"
    pdf_path = OUT_DIR / f"{SLUG}.pdf"
    md_path.write_text(combined_md)
    title = f"{lane.name} Support Guide"
    pdf_path.write_bytes(hd.render_pdf_bytes(title, combined_md))

    log("")
    log(f"Cards included in guide: {len(results)}/{len(kept)}")
    if failed:
        log(f"Cards skipped (failed): {len(failed)}")
        for sl, name in failed:
            log(f"  - {sl}  {name}")
    log(f"Markdown written: {md_path}")
    log(f"PDF written: {pdf_path}")


if __name__ == "__main__":
    main()
