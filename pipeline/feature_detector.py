"""Detect whether a card maps to existing MCSL automation coverage."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from textwrap import dedent

import config
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from pipeline.automation_writer import find_pom
from rag.code_indexer import search_code

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    kind: str
    confidence: float
    reasoning: str
    related_files: list[str] = field(default_factory=list)
    related_chunks: list[str] = field(default_factory=list)


DETECTOR_PROMPT = dedent(
    """\
    You are a Playwright automation expert for the MCSL Shopify app.

    Decide whether the feature below is already covered by existing automation or
    whether it should be treated as a new automation area.

    FEATURE:
    {feature_summary}

    RETRIEVED AUTOMATION CONTEXT:
    {context}

    Respond in this exact JSON shape:
    {{
      "kind": "new" | "existing",
      "confidence": 0.0,
      "reasoning": "short explanation",
      "related_files": ["tests/...spec.ts", "support/pages/...ts"]
    }}
    """
)


def detect_feature(card_name: str, acceptance_criteria: str, top_k: int = 8) -> DetectionResult:
    """Classify MCSL automation coverage for a feature card."""
    query = f"{card_name}\n{(acceptance_criteria or '')[:500]}".strip()
    docs = search_code(query, k=top_k, source_type="automation") or []

    pom_match = find_pom(card_name, acceptance_criteria=acceptance_criteria)
    related_files: list[str] = []
    if pom_match:
        if pom_match.get("file"):
            related_files.append(pom_match["file"])
        if pom_match.get("spec_file"):
            related_files.append(pom_match["spec_file"])

    context_parts: list[str] = []
    for idx, doc in enumerate(docs, 1):
        file_path = doc.metadata.get("file_path", "")
        snippet = doc.page_content[:320]
        context_parts.append(f"[{idx}] {file_path}\n{snippet}")
        if file_path and file_path not in related_files:
            related_files.append(file_path)

    if not docs and not pom_match:
        return DetectionResult(
            kind="new",
            confidence=0.9,
            reasoning="No similar automation files were found in the indexed MCSL automation codebase.",
        )

    if not config.ANTHROPIC_API_KEY:
        kind = "existing" if related_files else "new"
        return DetectionResult(
            kind=kind,
            confidence=0.7 if kind == "existing" else 0.85,
            reasoning=(
                "Matched existing automation files in the MCSL codebase."
                if kind == "existing"
                else "No existing automation match was strong enough."
            ),
            related_files=related_files[:6],
            related_chunks=[doc.page_content[:200] for doc in docs[:3]],
        )

    try:
        claude = ChatAnthropic(
            model=getattr(config, "CLAUDE_HAIKU_MODEL", config.CLAUDE_SONNET_MODEL),
            api_key=config.ANTHROPIC_API_KEY,
            temperature=0,
            max_tokens=800,
        )
        prompt = DETECTOR_PROMPT.format(
            feature_summary=query,
            context="\n\n".join(context_parts) or "(none)",
        )
        response = claude.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip() if isinstance(response.content, str) else str(response.content)
        clean = re.sub(r"```(?:json)?\n?", "", raw).strip().rstrip("`")
        data = json.loads(clean)
        merged_files = list(dict.fromkeys([*(data.get("related_files", []) or []), *related_files]))
        return DetectionResult(
            kind=data.get("kind", "existing" if merged_files else "new"),
            confidence=float(data.get("confidence", 0.6)),
            reasoning=data.get("reasoning", ""),
            related_files=merged_files[:6],
            related_chunks=[doc.page_content[:200] for doc in docs[:3]],
        )
    except Exception as exc:
        logger.warning("MCSL feature detector fallback after Claude error: %s", exc)
        kind = "existing" if related_files else "new"
        return DetectionResult(
            kind=kind,
            confidence=0.65 if kind == "existing" else 0.8,
            reasoning=f"Claude detection unavailable; inferred from matched files: {related_files[:4]}",
            related_files=related_files[:6],
            related_chunks=[doc.page_content[:200] for doc in docs[:3]],
        )
