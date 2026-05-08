"""Durable QA feedback memory for MCSL card cycles.

The dashboard treats this as optional context: failures here should not block
TC generation, but the Codex/Claude knowledge-maintainer skill needs a real
module to store and retrieve scenario learnings.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import logging
import re
from typing import Any

from langchain_core.documents import Document

from rag.vectorstore import search_filtered, upsert_documents

logger = logging.getLogger(__name__)


@dataclass
class ScenarioLearning:
    scenario: str
    root_cause: str = ""
    correct_navigation: str = ""
    correct_order_action: str = ""
    verification_signal: str = ""
    notes: str = ""

    def to_markdown(self) -> str:
        parts = [f"Scenario: {self.scenario}"]
        if self.root_cause:
            parts.append(f"Root cause: {self.root_cause}")
        if self.correct_navigation:
            parts.append(f"Correct navigation: {self.correct_navigation}")
        if self.correct_order_action:
            parts.append(f"Correct order action: {self.correct_order_action}")
        if self.verification_signal:
            parts.append(f"Verification signal: {self.verification_signal}")
        if self.notes:
            parts.append(f"Notes: {self.notes}")
        return "\n".join(parts)


@dataclass
class QAFeedback:
    card_id: str
    card_name: str
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    ac_misses: list[str] = field(default_factory=list)
    tc_issues: list[str] = field(default_factory=list)
    automation_issues: list[str] = field(default_factory=list)
    what_went_well: list[str] = field(default_factory=list)
    overall_notes: str = ""
    scenario_learnings: list[ScenarioLearning] = field(default_factory=list)

    def to_markdown(self) -> str:
        def _section(title: str, values: list[str]) -> str:
            if not values:
                return ""
            return f"\n## {title}\n" + "\n".join(f"- {item}" for item in values if item)

        body = [
            f"# QA Feedback: {self.card_name}",
            f"Card ID: {self.card_id}",
            f"Date: {self.date}",
        ]
        body.append(_section("AC misses", self.ac_misses))
        body.append(_section("TC issues", self.tc_issues))
        body.append(_section("Automation issues", self.automation_issues))
        body.append(_section("What went well", self.what_went_well))
        if self.overall_notes:
            body.append(f"\n## Overall notes\n{self.overall_notes}")
        if self.scenario_learnings:
            body.append(
                "\n## Scenario learnings\n"
                + "\n\n".join(item.to_markdown() for item in self.scenario_learnings)
            )
        return "\n".join(part for part in body if part).strip()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-") or "unknown"


def _feedback_id(feedback: QAFeedback) -> str:
    return f"qa_feedback__{feedback.card_id or _slug(feedback.card_name)}"


def save_feedback(feedback: QAFeedback) -> dict[str, Any]:
    """Upsert one QA feedback record into the main knowledge collection."""
    doc_id = _feedback_id(feedback)
    doc = Document(
        page_content=feedback.to_markdown(),
        metadata={
            "source_type": "qa_feedback",
            "source": f"qa_feedback:{feedback.card_id}",
            "card_id": feedback.card_id,
            "card_name": feedback.card_name,
            "date": feedback.date,
            "payload": json.dumps(asdict(feedback), ensure_ascii=False),
        },
    )
    upsert_documents([doc], ids=[doc_id])
    logger.info("Saved QA feedback for card %s", feedback.card_id)
    return {"id": doc_id, "source_type": "qa_feedback"}


def build_feedback_context(query: str, k: int = 4) -> str:
    """Return compact retrospective context for TC/AI-QA prompting."""
    try:
        docs = search_filtered(query, k=k, source_type="qa_feedback")
    except Exception as exc:
        logger.debug("QA feedback search skipped: %s", exc)
        return ""

    snippets: list[str] = []
    seen: set[str] = set()
    for doc in docs:
        card_name = doc.metadata.get("card_name", "")
        key = doc.metadata.get("card_id", "") or card_name or doc.page_content[:80]
        if key in seen:
            continue
        seen.add(key)
        header = f"[{card_name}]" if card_name else "[QA feedback]"
        snippets.append(f"{header}\n{doc.page_content[:900]}")
    return "\n\n---\n".join(snippets)
