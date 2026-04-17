"""
pipeline/release_analyser.py — Cross-card release risk and conflict analysis.
Phase 07 Plan 02 — RQA-05

Exports: analyse_release, CardSummary, ReleaseAnalysis
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from textwrap import dedent

import config
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage


@dataclass
class CardSummary:
    card_id: str
    card_name: str
    card_desc: str


@dataclass
class ReleaseAnalysis:
    release_name: str = ""
    risk_level: str = "LOW"           # "LOW" | "MEDIUM" | "HIGH"
    risk_summary: str = ""
    conflicts: list[dict] = field(default_factory=list)
    ordering: list[dict] = field(default_factory=list)
    coverage_gaps: list[str] = field(default_factory=list)
    kb_context_summary: str = ""
    sources: list[str] = field(default_factory=list)
    error: str = ""


RELEASE_ANALYSIS_PROMPT = dedent("""\
    You are a senior QA lead and MCSL (Multi-Carrier Shipping Labels) Shopify App domain expert
    for PluginHive. The app supports FedEx, UPS, DHL, USPS, and other carriers.

    A release "{release_name}" contains the following cards:
    {cards_summary}

    Knowledge base context for this release area:
    {context}

    Analyse the release and respond in this EXACT JSON format (no extra text, no markdown fences):
    {{
      "risk_level": "LOW" | "MEDIUM" | "HIGH",
      "risk_summary": "<one sentence overall risk assessment>",
      "conflicts": [
        {{"cards": ["card name 1", "card name 2"], "area": "...", "description": "..."}}
      ],
      "ordering": [
        {{"position": 1, "card_name": "...", "reason": "..."}}
      ],
      "coverage_gaps": ["<area not covered by any card>"],
      "kb_context_summary": "<key MCSL domain facts relevant to this release>"
    }}
""")


def analyse_release(release_name: str, cards: list[CardSummary]) -> ReleaseAnalysis:
    """Analyse a release for cross-card risks, conflicts, and ordering.

    Returns ReleaseAnalysis — never raises.
    """
    # Guard: empty cards
    if not cards:
        return ReleaseAnalysis(
            release_name=release_name,
            risk_level="LOW",
            error="Empty card list — no analysis performed.",
        )

    # Guard: no API key
    if not getattr(config, "ANTHROPIC_API_KEY", ""):
        return ReleaseAnalysis(
            release_name=release_name,
            error="ANTHROPIC_API_KEY not configured",
        )

    # Build combined query and fetch RAG context
    combined_query = " ".join(f"{c.card_name} {c.card_desc[:100]}" for c in cards)
    k = min(6 * len(cards), 20)
    context = ""
    sources = []
    try:
        from rag.vectorstore import search
        docs = search(combined_query, k=k)
        context = "\n\n---\n\n".join(d.page_content for d in docs)
        sources = [d.metadata.get("source", "") for d in docs if d.metadata.get("source")]
    except Exception as exc:
        logging.warning("RAG search failed in analyse_release: %s", exc)
        context = "Knowledge base unavailable."

    # Build cards summary for prompt
    cards_summary = "\n".join(
        f"- [{c.card_id}] {c.card_name}: {c.card_desc[:200]}" for c in cards
    )
    prompt = RELEASE_ANALYSIS_PROMPT.format(
        release_name=release_name,
        cards_summary=cards_summary,
        context=context or "No context retrieved.",
    )

    max_tokens = min(3000 + len(cards) * 400, 6000)
    try:
        llm = ChatAnthropic(
            model=config.CLAUDE_SONNET_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=0,
            max_tokens=max_tokens,
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(m.group(0) if m else raw)
        return ReleaseAnalysis(
            release_name=release_name,
            risk_level=data.get("risk_level", "LOW"),
            risk_summary=data.get("risk_summary", ""),
            conflicts=data.get("conflicts", []),
            ordering=data.get("ordering", []),
            coverage_gaps=data.get("coverage_gaps", []),
            kb_context_summary=data.get("kb_context_summary", ""),
            sources=sources,
        )
    except Exception as exc:
        logging.error("analyse_release failed: %s", exc)
        return ReleaseAnalysis(
            release_name=release_name,
            error=f"Analysis failed: {exc}",
            sources=sources,
        )
