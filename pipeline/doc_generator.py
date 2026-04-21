"""Feature documentation generation for the MCSL automation pipeline."""
from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path
from textwrap import dedent

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

import config
from rag.vectorstore import search

logger = logging.getLogger(__name__)

CODEBASE = Path(config.MCSL_AUTOMATION_REPO_PATH) if config.MCSL_AUTOMATION_REPO_PATH else None
DOCS_DIR = CODEBASE / "docs" / "features" if CODEBASE else None
CHANGELOG = CODEBASE / "docs" / "CHANGELOG.md" if CODEBASE else None


DOC_PROMPT = dedent(
    """\
    You are a senior QA engineer writing technical feature documentation for
    the MCSL Shopify multi-carrier Playwright automation suite.

    Write a concise feature document in Markdown using EXACTLY this structure
    (no extra sections, no omissions):

    # {card_name}

    **Release:** {release}
    **Date:** {today}
    **Spec:** `{spec_file}`
    **POM:** `{pom_file}`

    ## Overview
    (2-3 sentences: what the feature changes, why QA/support should care)

    ## Test Coverage
    (Bullet list of automated coverage — positive scenarios, edge cases, exclusions)

    ## Key UI Elements
    (Exact labels, toggles, sections, order areas, or buttons used in tests)

    ## Known Constraints
    (Carrier, Shopify, account, toggle, or packaging prerequisites from context below)

    ## QA Notes
    (Manual checks still needed, risky areas, or useful debugging clues)

    ---
    Source data:

    Card: {card_name}
    Release: {release}

    Acceptance Criteria:
    {ac}

    Test Cases:
    {test_cases}

    KB Context (constraints & behaviour):
    {kb_context}

    Rules:
    - Each section: 3-5 bullet points maximum
    - Write for a QA/support engineer who has never seen this feature before
    - Keep the tone direct and factual
    - Mention carriers, toggles, request logs, labels, packaging, or fulfillment only when grounded in the source data
    - Do NOT add sections not listed above
"""
)


def generate_feature_doc(
    card_name: str,
    acceptance_criteria: str,
    test_cases: str = "",
    spec_file: str = "",
    pom_file: str = "",
    release: str = "",
) -> dict:
    """Generate a markdown feature doc and append a changelog entry."""
    result = {
        "doc_path": "",
        "doc_content": "",
        "changelog_entry": "",
        "error": "",
    }

    if CODEBASE is None or DOCS_DIR is None or CHANGELOG is None:
        result["error"] = "MCSL_AUTOMATION_REPO_PATH is not set"
        return result
    if not config.ANTHROPIC_API_KEY:
        result["error"] = "ANTHROPIC_API_KEY not set"
        return result

    today = date.today().isoformat()
    try:
        rag_query = f"{card_name} {acceptance_criteria[:300]}"
        docs = search(rag_query, k=4)
        kb_context = "\n\n".join(
            f"[{doc.metadata.get('source', 'KB')}]\n{doc.page_content}"
            for doc in docs
        )
    except Exception as exc:
        logger.warning("RAG search failed in doc_generator: %s", exc)
        kb_context = "No KB context available."

    prompt = DOC_PROMPT.format(
        card_name=card_name,
        release=release or "Unknown",
        today=today,
        spec_file=spec_file or "(not generated yet)",
        pom_file=pom_file or "(not generated yet)",
        ac=acceptance_criteria[:2000],
        test_cases=test_cases[:1500],
        kb_context=kb_context[:1200],
    )

    try:
        llm = ChatAnthropic(
            model=config.CLAUDE_SONNET_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=0.2,
            max_tokens=1800,
        )
        resp = llm.invoke([HumanMessage(content=prompt)])
        result["doc_content"] = resp.content.strip()
    except Exception as exc:
        logger.error("Claude doc generation failed: %s", exc)
        result["error"] = f"Claude error: {exc}"
        return result

    slug = re.sub(r"[^a-z0-9]+", "-", card_name.lower()).strip("-")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    doc_path = DOCS_DIR / f"{slug}.md"
    try:
        doc_path.write_text(result["doc_content"], encoding="utf-8")
        result["doc_path"] = str(doc_path.relative_to(CODEBASE))
    except Exception as exc:
        logger.error("Failed to write doc file: %s", exc)
        result["error"] = f"File write error: {exc}"
        return result

    changelog_entry = (
        f"\n### [{release or 'Unreleased'}] — {today}\n"
        f"- **{card_name}**\n"
        f"  - Spec: `{spec_file or '(not generated yet)'}`\n"
        f"  - Docs: [docs/features/{slug}.md](docs/features/{slug}.md)\n"
    )
    result["changelog_entry"] = changelog_entry.strip()

    try:
        CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
        if CHANGELOG.exists():
            existing = CHANGELOG.read_text(encoding="utf-8")
            lines = existing.splitlines()
            insert_idx = 1
            for idx, line in enumerate(lines):
                if line.startswith("### [") or line.startswith("## ["):
                    insert_idx = idx
                    break
            lines.insert(insert_idx, changelog_entry)
            CHANGELOG.write_text("\n".join(lines), encoding="utf-8")
        else:
            CHANGELOG.write_text(
                f"# MCSL Automation — Changelog\n{changelog_entry}",
                encoding="utf-8",
            )
    except Exception as exc:
        logger.warning("CHANGELOG update failed (doc still saved): %s", exc)

    return result


def generate_release_docs(release: str, cards_data: list[dict]) -> list[dict]:
    """Generate docs for every card in a release."""
    return [
        generate_feature_doc(
            card_name=card.get("card_name", "Unknown"),
            acceptance_criteria=card.get("acceptance_criteria", ""),
            test_cases=card.get("test_cases", ""),
            spec_file=card.get("spec_file", ""),
            pom_file=card.get("pom_file", ""),
            release=release,
        )
        for card in cards_data
    ]
