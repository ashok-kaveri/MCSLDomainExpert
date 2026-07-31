"""Generate MCSL support guides for a Trello card or lane, for the Slack QA bot.

Reuses the dashboard handoff pipeline:
  - Trello fetch: ``pipeline.trello_client.TrelloClient``
  - Context + generation: ``pipeline.handoff_docs``

Triggered from Slack, the guide is built from Trello card content (description,
comments, checklists, members, and detected toggles/carriers/navigation). It does
NOT include the dashboard's in-session AC draft / TCs / AI-QA evidence, which live
in Streamlit session state rather than on the card.
"""
from __future__ import annotations

import logging
import re

import config  # noqa: F401 — side effect: loads .env so Trello/Anthropic creds are present

logger = logging.getLogger(__name__)

# "support guide" or "support doc"
_TRIGGER_RE = re.compile(r"\bsupport\s+(?:guide|doc(?:ument)?)s?\b", re.IGNORECASE)
_PER_CARD_RE = re.compile(r"\b(?:per[\s-]?card|each\s+card|every\s+card|card[\s-]?by[\s-]?card)\b", re.IGNORECASE)
_LANE_KW_RE = re.compile(r"\b(?:lane|list)\b", re.IGNORECASE)
# Trello card URL → capture the shortlink, or a raw 24-hex / 8-char shortlink id.
_CARD_URL_RE = re.compile(r"trello\.com/c/([A-Za-z0-9]+)", re.IGNORECASE)
_CARD_ID_RE = re.compile(r"\b([a-f0-9]{24}|[A-Za-z0-9]{8})\b")


def parse_support_guide_request(text: str) -> dict | None:
    """Classify a support-guide request. Returns a dict or None if not a request.

    dict shapes:
        {"kind": "card", "card_ref": "<id-or-shortlink>"}
        {"kind": "lane", "lane_name": "<name>"}
        {"kind": "lane_per_card", "lane_name": "<name>"}
    """
    if not text or not _TRIGGER_RE.search(text):
        return None

    # A Trello card URL is the strongest signal → single-card guide.
    url_match = _CARD_URL_RE.search(text)
    if url_match:
        return {"kind": "card", "card_ref": url_match.group(1)}

    is_lane = bool(_LANE_KW_RE.search(text))
    lane_name = _extract_lane_name(text) if is_lane else ""

    if is_lane and lane_name:
        kind = "lane_per_card" if _PER_CARD_RE.search(text) else "lane"
        return {"kind": kind, "lane_name": lane_name}

    # No URL, no lane → look for a bare card id/shortlink token.
    for m in _CARD_ID_RE.finditer(text):
        token = m.group(1)
        if token.lower() not in {"support", "generate", "document"}:
            return {"kind": "card", "card_ref": token}

    # It mentioned "support guide" but we couldn't find a target.
    return {"kind": "unknown"}


def _extract_lane_name(text: str) -> str:
    """Pull the lane/list name: prefer a quoted string, else text after lane/list."""
    quoted = re.search(r"[\"“']([^\"”']+)[\"”']", text)
    if quoted:
        return quoted.group(1).strip()
    # e.g. "...for lane MCSL 381" / "...for list Ready for QA"
    after = re.search(r"\b(?:lane|list)\b[:\s]+(.+)$", text, re.IGNORECASE)
    if after:
        # Trim trailing politeness/punctuation.
        name = re.split(r"\b(?:per[\s-]?card|each\s+card)\b", after.group(1), flags=re.IGNORECASE)[0]
        return name.strip(" .?!\"'").strip()
    return ""


# ── Trello + generation ──────────────────────────────────────────────────────

def _client():
    from pipeline.trello_client import TrelloClient
    return TrelloClient()


def _full_card(client, card):
    """Re-fetch a card by id so comments/checklists are populated (list endpoint omits them)."""
    try:
        return client.get_card(card.id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("get_card(%s) failed, using list-level card: %s", card.id, exc)
        return card


def _ctx_for(client, card, release_name: str = ""):
    from pipeline.handoff_docs import build_handoff_context
    members = []
    try:
        members = client.get_card_members(card.id)
    except Exception:  # noqa: BLE001
        members = []
    return build_handoff_context(
        card=card,
        release_name=release_name,
        acceptance_criteria=card.desc or "",
        members=members,
    )


def _find_lane(client, lane_name: str):
    """Case-insensitive exact match first, then a 'contains' match."""
    lists = client.get_lists()
    low = lane_name.lower()
    for lst in lists:
        if lst.name.lower() == low:
            return lst
    for lst in lists:
        if low in lst.name.lower():
            return lst
    return None


def generate_card_guide(card_ref: str) -> tuple[str, str]:
    """Return (title, markdown) for a single card. Raises ValueError if not found."""
    from pipeline.handoff_docs import generate_support_guide

    client = _client()
    try:
        card = client.get_card(card_ref)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Could not fetch Trello card `{card_ref}`: {exc}") from exc
    ctx = _ctx_for(client, card)
    md = generate_support_guide(ctx)
    return (card.name or card_ref, md)


def generate_lane_combined(lane_name: str) -> tuple[str, str, int]:
    """Return (title, markdown, card_count) — one combined guide for the lane."""
    from pipeline.handoff_docs import generate_combined_support_guide

    client = _client()
    lane = _find_lane(client, lane_name)
    if not lane:
        raise ValueError(f"No Trello lane/list matching “{lane_name}”.")
    cards = client.get_cards_in_list(lane.id)
    if not cards:
        raise ValueError(f"Lane “{lane.name}” has no cards.")
    contexts = [_ctx_for(client, _full_card(client, c), release_name=lane.name) for c in cards]
    md = generate_combined_support_guide(contexts, lane.name)
    return (lane.name, md, len(cards))


def generate_lane_per_card(lane_name: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (lane_name, [(card_name, markdown), ...]) — one guide per card."""
    from pipeline.handoff_docs import generate_support_guide

    client = _client()
    lane = _find_lane(client, lane_name)
    if not lane:
        raise ValueError(f"No Trello lane/list matching “{lane_name}”.")
    cards = client.get_cards_in_list(lane.id)
    if not cards:
        raise ValueError(f"Lane “{lane.name}” has no cards.")
    guides = []
    for c in cards:
        full = _full_card(client, c)
        ctx = _ctx_for(client, full, release_name=lane.name)
        guides.append((full.name or full.id, generate_support_guide(ctx)))
    return (lane.name, guides)
