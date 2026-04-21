"""Shared locator knowledge for AI QA and automation writing."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MEMORY_FILE = Path(__file__).resolve().parent.parent / "data" / "locator_memory.json"

_LOCATOR_PATTERNS = [
    r'getByRole\([^)]+\)',
    r'getByText\([^)]+\)',
    r'getByLabel\([^)]+\)',
    r'getByPlaceholder\([^)]+\)',
    r'locator\([^)]+\)',
    r'frameLocator\([^)]+\)',
]

_AREA_KEYWORDS: dict[str, tuple[str, ...]] = {
    "orders": ("order", "orders", "prepare shipment", "generate label", "mark as fulfilled"),
    "order_summary": ("order summary", "label summary", "rate summary", "print documents", "view log"),
    "products": ("product", "products", "dry ice", "alcohol", "battery", "signature"),
    "carriers": ("carrier", "carriers", "account", "credentials"),
    "automation": ("automation", "rule", "rate automation", "label automation"),
    "shopify_products": ("shopify product", "variant", "variants"),
    "shopify_orders": ("shopify order", "fulfillment", "tracking"),
    "pickup": ("pickup", "schedule pickup"),
}

_SOURCE_CONFIDENCE: dict[str, float] = {
    "role_button_exact": 0.95,
    "role_link_exact": 0.95,
    "label_exact": 0.94,
    "label": 0.92,
    "text_exact": 0.90,
    "placeholder": 0.88,
    "text_fuzzy": 0.82,
    "css_locator": 0.78,
    "css_dispatch": 0.70,
    "runtime": 0.75,
}

_STATUS_BONUS: dict[str, float] = {
    "pass": 0.20,
    "partial": 0.08,
    "qa_needed": 0.02,
    "fail": -0.10,
}

_TRUST_BONUS = 0.12


def _load_memory() -> list[dict]:
    if not _MEMORY_FILE.exists():
        return []
    try:
        data = json.loads(_MEMORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as exc:
        logger.debug("Locator memory read failed: %s", exc)
        return []


def _save_memory(items: list[dict]) -> None:
    _MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _MEMORY_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def extract_locator_hints_from_text(text: str, *, limit: int = 12) -> list[str]:
    hints: list[str] = []
    for pattern in _LOCATOR_PATTERNS:
        for match in re.findall(pattern, text or ""):
            clean = " ".join(str(match).split())
            if clean and clean not in hints:
                hints.append(clean)
            if len(hints) >= limit:
                return hints
    return hints


def _normalize_words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def _infer_tags(*texts: str) -> list[str]:
    combined = " ".join(texts).lower()
    tags: list[str] = []
    for tag, phrases in _AREA_KEYWORDS.items():
        if any(phrase in combined for phrase in phrases):
            tags.append(tag)
    return tags


def _infer_tags_from_url(url: str) -> list[str]:
    lower = (url or "").lower()
    tags: list[str] = []
    if "/orders" in lower or "order" in lower:
        tags.append("orders")
    if "/products" in lower or "product" in lower:
        tags.append("products")
    if "carrier" in lower:
        tags.append("carriers")
    if "automation" in lower:
        tags.append("automation")
    if "pickup" in lower:
        tags.append("pickup")
    if "shopify.com" in lower and "/orders" in lower:
        tags.append("shopify_orders")
    if "shopify.com" in lower and "/products" in lower:
        tags.append("shopify_products")
    return tags


def _score_match(query: str, item: dict) -> float:
    if item.get("blocked"):
        return 0.0
    qwords = _normalize_words(query)
    qtags = set(_infer_tags(query))
    if not qwords and not qtags:
        return 0.0
    text = " ".join(str(item.get(key, "")) for key in ("card_name", "scenario", "target", "description", "selector"))
    iwords = _normalize_words(text)
    overlap = len(qwords & iwords)
    tag_matches = len(qtags & set(item.get("tags", []) or []))
    page_url = str(item.get("page_url", "") or "")
    page_match = 0.0
    if page_url and qwords:
        page_words = _normalize_words(page_url)
        page_match = len(qwords & page_words) / max(len(qwords), 1)
    if not overlap and not tag_matches and page_match <= 0:
        return 0.0
    base = overlap / max(len(qwords), 1) if qwords else 0.0
    confidence = float(item.get("confidence", 0.5) or 0.5)
    status_bonus = _STATUS_BONUS.get(str(item.get("scenario_status", "")).lower(), 0.0)
    proven_bonus = 0.08 if item.get("proven") else 0.0
    trust_bonus = _TRUST_BONUS if item.get("trusted") else 0.0
    tag_bonus = min(tag_matches * 0.08, 0.24)
    return base * 0.45 + confidence * 0.25 + page_match * 0.10 + tag_bonus + status_bonus + proven_bonus + trust_bonus


def fetch_code_locator_hints(query: str, *, source_type: str = "automation", k: int = 5, limit: int = 12) -> list[str]:
    try:
        from rag.code_indexer import search_code

        docs = search_code(query, k=k, source_type=source_type) or []
    except Exception as exc:
        logger.debug("Code locator hint search failed: %s", exc)
        return []

    hints: list[str] = []
    for doc in docs:
        file_path = doc.metadata.get("file_path", "")
        for locator in extract_locator_hints_from_text(doc.page_content, limit=limit):
            entry = f"[{file_path}] {locator}" if file_path else locator
            if entry not in hints:
                hints.append(entry)
            if len(hints) >= limit:
                return hints
    return hints


def save_runtime_locator_memory(
    card_name: str,
    scenario: str,
    steps: list[Any],
    *,
    scenario_status: str = "",
) -> None:
    entries = _load_memory()
    prior_selectors = {
        (str(item.get("selector", "")).strip(), str(item.get("page_url", "")).strip())
        for item in entries
        if not item.get("blocked")
    }
    useful = [
        {
            "card_name": card_name,
            "scenario": scenario,
            "action": step.action,
            "target": step.target,
            "selector": step.selector,
            "locator_source": step.locator_source,
            "description": step.description,
            "page_url": getattr(step, "page_url", ""),
            "destination": getattr(step, "destination", ""),
            "tags": sorted(set(
                _infer_tags(
                    card_name,
                    scenario,
                    getattr(step, "target", ""),
                    getattr(step, "description", ""),
                    getattr(step, "destination", ""),
                ) + _infer_tags_from_url(getattr(step, "page_url", ""))
            )),
            "confidence": _SOURCE_CONFIDENCE.get(getattr(step, "locator_source", ""), 0.72),
            "scenario_status": scenario_status,
            "proven": scenario_status in {"pass", "partial"},
            "known_before_run": (
                str(getattr(step, "selector", "")).strip(),
                str(getattr(step, "page_url", "")).strip(),
            ) in prior_selectors,
            "learned_this_run": (
                str(getattr(step, "selector", "")).strip(),
                str(getattr(step, "page_url", "")).strip(),
            ) not in prior_selectors,
            "trusted": False,
            "blocked": False,
        }
        for step in steps
        if getattr(step, "selector", "").strip()
    ]
    if not useful:
        return

    retained = [
        item for item in entries
        if not (
            item.get("card_name") == card_name
            and item.get("scenario") == scenario
        )
    ]
    retained.extend(useful[:20])
    _save_memory(retained[-500:])


def load_runtime_locator_memory_context(query: str, *, limit: int = 12) -> list[str]:
    ranked = sorted(
        _load_memory(),
        key=lambda item: _score_match(query, item),
        reverse=True,
    )
    matches: list[str] = []
    for item in ranked:
        score = _score_match(query, item)
        if score <= 0:
            continue
        selector = item.get("selector", "")
        if not selector:
            continue
        tag_text = ",".join(item.get("tags", []) or [])
        conf = float(item.get("confidence", 0.0) or 0.0)
        page_url = item.get("page_url", "")
        status = item.get("scenario_status", "")
        proof = "trusted" if item.get("trusted") else ("proven" if item.get("proven") else "unproven")
        line = (
            f"[memory/{item.get('card_name', 'card')}] "
            f"{selector} ({item.get('locator_source', 'runtime')}, confidence={conf:.2f}, {proof}"
            f"{', status=' + status if status else ''}"
            f"{', learned' if item.get('learned_this_run') else ', reused'}"
            f"{', tags=' + tag_text if tag_text else ''}"
            f"{', page=' + page_url if page_url else ''})"
        )
        if line not in matches:
            matches.append(line)
        if len(matches) >= limit:
            break
    return matches


def build_locator_context(query: str, *, limit: int = 12) -> str:
    code_hints = fetch_code_locator_hints(query, limit=limit)
    memory_hints = load_runtime_locator_memory_context(query, limit=limit)
    sections: list[str] = []
    if code_hints:
        sections.append("Automation locator hints:\n" + "\n".join(f"- {line}" for line in code_hints))
    if memory_hints:
        sections.append("Runtime-discovered locator hints:\n" + "\n".join(f"- {line}" for line in memory_hints))
    return "\n\n".join(sections)


def get_scenario_locator_entries(card_name: str, scenario: str) -> list[dict]:
    entries = [
        item for item in _load_memory()
        if item.get("card_name") == card_name and item.get("scenario") == scenario
    ]
    return sorted(
        entries,
        key=lambda item: (
            bool(item.get("trusted")),
            bool(item.get("proven")),
            float(item.get("confidence", 0.0) or 0.0),
        ),
        reverse=True,
    )


def update_scenario_locator_review(
    card_name: str,
    scenario: str,
    *,
    trusted: bool | None = None,
    blocked: bool | None = None,
    learned_only: bool = False,
) -> int:
    entries = _load_memory()
    changed = 0
    for item in entries:
        if item.get("card_name") != card_name or item.get("scenario") != scenario:
            continue
        if learned_only and not item.get("learned_this_run"):
            continue
        if trusted is not None:
            item["trusted"] = trusted
        if blocked is not None:
            item["blocked"] = blocked
        changed += 1
    if changed:
        _save_memory(entries)
    return changed
