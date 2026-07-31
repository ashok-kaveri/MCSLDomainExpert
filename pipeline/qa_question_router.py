"""Route a natural-language QA question to the right answerer.

Two paths:
  1. Deterministic metric intents (automation coverage, latest release run) →
     ``pipeline/qa_metrics.py``. Fast, exact, no LLM.
  2. Everything else → RAG over BOTH knowledge collections (wiki/KB via
     ``rag.vectorstore.search`` and automation/code via
     ``rag.code_indexer.search_code``), then answered with the domain-expert LLM.

This is the brain behind the Slack QA bot (``pipeline/slack_qa_bot.py``) but is
import-safe and unit-testable on its own — it never touches Slack.
"""
from __future__ import annotations

import logging
import re

from pipeline import qa_metrics

logger = logging.getLogger(__name__)

# ── Intent patterns ─────────────────────────────────────────────────────────
# Order matters: the first matching intent wins.
_AUTOMATED_COUNT_RE = re.compile(
    r"how many.*(?:cases?|tests?|specs?).*(?:automat|written|cover)"
    r"|(?:number|count).*(?:automat|specs?)"
    r"|how many.*(?:automat).*(?:cases?|tests?)",
    re.IGNORECASE,
)
_RELEASE_RUN_RE = re.compile(
    r"how many.*(?:cases?|tests?).*(?:ran|run|executed)"
    r"|(?:cases?|tests?).*(?:ran|run|executed).*(?:release|run|suite)"
    r"|(?:release|last run|latest run).*(?:result|status|pass|fail|how many)"
    r"|how (?:did|many).*(?:release|run).*(?:go|pass|fail)",
    re.IGNORECASE,
)
_REGRESSION_COUNT_RE = re.compile(
    r"(?:how many|number of|count of|total)\s+(?:test\s*)?(?:cases?|tests?|tcs?)\b"
    r".*(?:regression|sheet|tc sheet|google sheet)"
    r"|(?:regression|tc)\s+sheet.*(?:how many|count|total|number)",
    re.IGNORECASE,
)


def _format_automated(stats: dict) -> str:
    lines = [
        f"*Automated cases:* {stats['test_blocks']} test cases "
        f"across {stats['spec_files']} spec files in {stats['folders']} areas.",
    ]
    top = sorted(stats["by_folder"].items(), key=lambda kv: kv[1], reverse=True)[:8]
    if top:
        lines.append("Top areas by spec count:")
        lines += [f"  • {folder}: {n}" for folder, n in top]
    lines.append("_(test-case count is an approximate `test()` block count)_")
    return "\n".join(lines)


def _format_regression(stats: dict) -> str:
    if not stats.get("available"):
        return f":warning: Couldn't read the regression sheet: {stats.get('error', 'unknown error')}"
    lines = [
        f"*Regression sheet:* {stats['total']} test-case rows across {stats['tab_count']} tabs."
    ]
    top = sorted(stats["by_tab"].items(), key=lambda kv: kv[1], reverse=True)[:10]
    if top:
        lines.append("By tab:")
        lines += [f"  • {tab}: {n}" for tab, n in top]
    lines.append("_(counts non-empty data rows per tab, minus a header row)_")
    return "\n".join(lines)


def _format_release_run(run: dict) -> str:
    if not run.get("available"):
        return f":warning: {run.get('error', 'No release run data available.')}"
    lines = [
        f"*Latest run:* {run['total']} cases ran — "
        f"{run['passed']} passed, {run['failures']} failed "
        f"(failure rate {run['failure_rate'] or 'n/a'}).",
    ]
    if run.get("decision"):
        lines.append(f"Decision: *{run['decision']}* (risk {run['risk_level'] or 'n/a'}).")
    if run.get("reason"):
        lines.append(f"_{run['reason']}_")
    if run.get("flaky"):
        lines.append(f"Flaky flagged: {len(run['flaky'])} — e.g. {run['flaky'][0]}")
    lines.append("_(reflects the most recent stored run, not a per-release-tag history)_")
    return "\n".join(lines)


def _rag_answer(question: str) -> str:
    """Answer a free-form question using both knowledge collections + the LLM."""
    from collections import defaultdict

    from rag.chain import get_llm, _SOURCE_LABELS
    from rag.prompts import QA_PROMPT
    from rag.vectorstore import search
    from rag.code_indexer import search_code

    docs = []
    try:
        docs += search(question, k=8)
    except Exception as exc:  # noqa: BLE001 — empty/unreachable store shouldn't break the bot
        logger.warning("wiki search failed: %s", exc)
    for source_type in ("automation", "storepepsaas_server", "storepepsaas_client"):
        try:
            docs += search_code(question, k=4, source_type=source_type) or []
        except Exception as exc:  # noqa: BLE001
            logger.warning("code search (%s) failed: %s", source_type, exc)

    if not docs:
        return ("I couldn't find anything relevant in the knowledge base. "
                "Try rephrasing, or ask about a specific feature, carrier, spec, or POM.")

    groups: dict[str, list] = defaultdict(list)
    for doc in docs:
        groups[doc.metadata.get("source_type", "unknown")].append(doc)
    sections = []
    for source_type in sorted(groups):
        label = _SOURCE_LABELS.get(source_type, source_type.replace("_", " ").title())
        body = "\n\n".join(d.page_content for d in groups[source_type])
        sections.append(f"### [{label}]\n{body}")
    context = "\n\n---\n\n".join(sections)

    llm = get_llm()
    from langchain_core.messages import HumanMessage
    resp = llm.invoke([HumanMessage(content=QA_PROMPT.format(context=context, question=question))])
    return resp.content.strip()


def answer_question(text: str) -> str:
    """Route `text` to a metric answer or a RAG answer and return Slack-ready text."""
    question = (text or "").strip()
    if not question:
        return "Ask me about automation coverage, the latest release run, or any MCSL feature/carrier."

    # Regression-sheet count is checked first: "how many test cases in the regression
    # sheet" otherwise gets answered (poorly) by RAG over wiki.
    if _REGRESSION_COUNT_RE.search(question):
        return _format_regression(qa_metrics.count_regression_cases())
    # Release-run intent is checked before automation-count: "how many cases ran"
    # contains "how many cases" which the broader automation regex could also match.
    if _RELEASE_RUN_RE.search(question):
        return _format_release_run(qa_metrics.latest_release_run())
    if _AUTOMATED_COUNT_RE.search(question):
        return _format_automated(qa_metrics.count_automated_cases())

    return _rag_answer(question)
