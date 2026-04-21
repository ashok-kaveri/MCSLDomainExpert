"""Manual QA bug drafting, duplicate check, and Trello backlog raise flow."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from textwrap import dedent

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

import config
from pipeline.trello_client import TrelloClient, TrelloCard

logger = logging.getLogger(__name__)

BACKLOG_LIST_NAME = "Backlog"


@dataclass
class BugDraft:
    title: str
    severity: str
    feature_area: str
    steps_to_reproduce: list[str]
    expected_behavior: str
    actual_behavior: str
    environment: str = "QA"
    labels: list[str] = field(default_factory=list)
    release: str = ""
    raw_description: str = ""

    def to_trello_desc(self) -> str:
        steps = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(self.steps_to_reproduce))
        labels_str = " · ".join(f"`{label}`" for label in self.labels)
        return dedent(
            f"""\
            ## Bug Report

            **Type:** Bug
            **Severity:** {self.severity}
            **Feature Area:** {self.feature_area}
            **Environment:** {self.environment}
            **Release:** {self.release or 'Unreleased'}
            **Labels:** {labels_str}

            ---

            ### Steps to Reproduce
            {steps}

            ### Expected Behaviour
            {self.expected_behavior}

            ### Actual Behaviour
            {self.actual_behavior}

            ---
            *Raised via MCSL QA Pipeline — Bug Reporter*
            """
        ).strip()

    def to_display_markdown(self) -> str:
        steps = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(self.steps_to_reproduce))
        sev_colors = {"P1": "🔴", "P2": "🟠", "P3": "🟡", "P4": "🟢"}
        sev_icon = sev_colors.get(self.severity, "⚪")
        return dedent(
            f"""\
            ### {sev_icon} [{self.severity}] {self.title}

            | Field | Value |
            |-------|-------|
            | **Severity** | {self.severity} |
            | **Feature Area** | {self.feature_area} |
            | **Environment** | {self.environment} |
            | **Release** | {self.release or 'Unreleased'} |
            | **Labels** | {', '.join(self.labels)} |

            **Steps to Reproduce**
            {steps}

            **Expected Behaviour**
            {self.expected_behavior}

            **Actual Behaviour**
            {self.actual_behavior}
            """
        ).strip()


@dataclass
class BugCheckResult:
    is_duplicate: bool
    duplicate_card: TrelloCard | None = None
    duplicate_reason: str = ""
    draft: BugDraft | None = None
    error: str = ""


FORMAT_BUG_PROMPT = dedent(
    """\
    You are a senior QA engineer writing a bug report for the MCSL Shopify multi-carrier app.

    A team member reported this issue during manual QA:
    {raw_description}

    Feature context: {feature_context}
    Release: {release}

    Format this into a structured bug report. Respond ONLY in this JSON (no markdown fences):
    {{
      "title": "<concise one-line bug summary — max 80 chars>",
      "severity": "P1" | "P2" | "P3" | "P4",
      "feature_area": "<which page, settings area, order flow, or label flow>",
      "steps_to_reproduce": ["<step 1>", "<step 2>", "<step 3>"],
      "expected_behavior": "<what should happen>",
      "actual_behavior": "<what actually happens>",
      "labels": ["QA Reported", "MCSL", "<P1|P2|P3|P4>"]
    }}

    Severity guide:
    - P1: label generation blocked, data loss, checkout broken broadly
    - P2: core carrier/label/rate behavior broken
    - P3: non-blocking behavior mismatch or scoped UI issue
    - P4: typo or cosmetic issue

    Rules:
    - steps_to_reproduce: minimum 2, maximum 6 steps
    - Be specific about page names, toggles, labels, or package/order areas when available
    - expected_behavior and actual_behavior: one sentence each
    - If severity is unclear, default to P3
    - labels ALWAYS include "QA Reported", "MCSL", and the severity label
    """
)

DUPLICATE_CHECK_PROMPT = dedent(
    """\
    You are a QA lead checking if a new bug report already exists in the backlog.

    NEW BUG BEING REPORTED:
    Title: {new_title}
    Description: {new_desc}

    EXISTING BACKLOG CARDS (title and description snippet):
    {existing_cards}

    Are any of the existing cards describing the same bug or the same root cause?

    Respond ONLY in this JSON (no markdown fences):
    {{
      "is_duplicate": true | false,
      "matching_card_index": <0-based index of the matching card, or -1 if none>,
      "confidence": "HIGH" | "MEDIUM" | "LOW",
      "reason": "<one sentence: why this is or is not a duplicate>"
    }}

    Rules:
    - is_duplicate = true only if HIGH or MEDIUM confidence
    - Different symptoms from the same root cause count as duplicate
    - Same symptom in a different feature area is NOT duplicate
    - If is_duplicate = false, set matching_card_index = -1
    """
)


def _get_claude() -> ChatAnthropic:
    return ChatAnthropic(
        model=config.CLAUDE_SONNET_MODEL,
        api_key=config.ANTHROPIC_API_KEY,
        temperature=0.1,
        max_tokens=1024,
    )


def _ask_claude(claude: ChatAnthropic, prompt: str) -> dict:
    resp = claude.invoke([HumanMessage(content=prompt)])
    raw = resp.content.strip()
    json_text = re.sub(r"```(?:json)?\n?", "", raw).strip().rstrip("`")
    return json.loads(json_text)


def _fetch_backlog_cards(list_name: str = BACKLOG_LIST_NAME) -> list[TrelloCard]:
    try:
        trello = TrelloClient()
        backlog = trello.get_list_by_name(list_name)
        if not backlog:
            return []
        return trello.get_cards_in_list(backlog.id)
    except Exception as exc:
        logger.warning("Could not fetch backlog cards: %s", exc)
        return []


def _quick_keyword_filter(new_title: str, cards: list[TrelloCard], top_n: int = 15) -> list[TrelloCard]:
    new_words = set(re.sub(r"[^a-z0-9 ]", " ", new_title.lower()).split())
    stop = {"the", "a", "an", "is", "in", "on", "at", "to", "for", "and", "or", "not", "with", "of", "it", "this", "that", "are", "was", "has"}
    new_words -= stop

    scored: list[tuple[int, TrelloCard]] = []
    for card in cards:
        card_words = set(re.sub(r"[^a-z0-9 ]", " ", card.name.lower()).split()) - stop
        scored.append((len(new_words & card_words), card))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [card for _, card in scored[:top_n]]


def check_and_draft_bug(
    issue_description: str,
    feature_context: str = "",
    release: str = "",
    backlog_list_name: str = BACKLOG_LIST_NAME,
) -> BugCheckResult:
    if not config.ANTHROPIC_API_KEY:
        return BugCheckResult(is_duplicate=False, error="ANTHROPIC_API_KEY not set")
    if not issue_description.strip():
        return BugCheckResult(is_duplicate=False, error="Issue description is empty")

    claude = _get_claude()
    try:
        fmt_prompt = FORMAT_BUG_PROMPT.format(
            raw_description=issue_description.strip(),
            feature_context=feature_context or "MCSL Shopify App",
            release=release or "Unknown",
        )
        data = _ask_claude(claude, fmt_prompt)
        draft = BugDraft(
            title=data.get("title", issue_description[:80]),
            severity=data.get("severity", "P3"),
            feature_area=data.get("feature_area", feature_context or "Unknown"),
            steps_to_reproduce=data.get("steps_to_reproduce", [issue_description]),
            expected_behavior=data.get("expected_behavior", ""),
            actual_behavior=data.get("actual_behavior", issue_description),
            labels=data.get("labels", ["QA Reported", "MCSL", "P3"]),
            release=release,
            raw_description=issue_description,
        )
    except Exception as exc:
        logger.error("Bug formatting failed: %s", exc)
        return BugCheckResult(is_duplicate=False, error=f"Could not format bug report: {exc}")

    backlog_cards = _fetch_backlog_cards(backlog_list_name)
    if not backlog_cards:
        return BugCheckResult(is_duplicate=False, draft=draft)

    candidate_cards = _quick_keyword_filter(draft.title, backlog_cards, top_n=15)
    if not candidate_cards:
        return BugCheckResult(is_duplicate=False, draft=draft)

    existing_cards_text = ""
    for idx, card in enumerate(candidate_cards):
        desc_snippet = (card.desc or "").strip()[:200]
        existing_cards_text += f"[{idx}] {card.name}\n    {desc_snippet}\n\n"

    try:
        dup_prompt = DUPLICATE_CHECK_PROMPT.format(
            new_title=draft.title,
            new_desc=draft.actual_behavior,
            existing_cards=existing_cards_text.strip(),
        )
        dup_data = _ask_claude(claude, dup_prompt)
        is_dup = dup_data.get("is_duplicate", False)
        idx = dup_data.get("matching_card_index", -1)
        reason = dup_data.get("reason", "")
        if is_dup and 0 <= idx < len(candidate_cards):
            return BugCheckResult(
                is_duplicate=True,
                duplicate_card=candidate_cards[idx],
                duplicate_reason=reason,
                draft=draft,
            )
    except Exception as exc:
        logger.warning("Duplicate check failed: %s — proceeding as new bug", exc)

    return BugCheckResult(is_duplicate=False, draft=draft)


def raise_bug(draft: BugDraft, backlog_list_name: str = BACKLOG_LIST_NAME) -> TrelloCard:
    trello = TrelloClient()
    backlog = trello.get_list_by_name(backlog_list_name)
    if not backlog:
        raise ValueError(f"Backlog list {backlog_list_name!r} not found on the selected Trello board")
    card = trello.create_card_in_list(
        list_id=backlog.id,
        name=draft.title,
        desc=draft.to_trello_desc(),
    )
    return card
