"""Bug reporter for MCSL QA Pipeline.

Notifies developers via Slack DM when the AI QA Agent finds a failing verdict.
Also provides a domain expert Q&A helper backed by RAG + Claude.
"""
from __future__ import annotations

import logging
from textwrap import dedent

import config
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

BUG_DM_PROMPT = dedent("""\
    Hi {dev_name},

    A bug was found during QA testing of the MCSL Shopify App.

    *Card:* {card_name}
    *Bug Summary:* {bug_description}

    Please review the Trello card for full details and test steps.

    — MCSL QA Pipeline (automated)
""")

DOMAIN_EXPERT_PROMPT = dedent("""\
    You are a senior domain expert for the MCSL (Multi-Carrier Shipping Labels)
    Shopify App built by PluginHive. The app supports FedEx, UPS, DHL, USPS,
    and other carriers.

    A QA engineer has a question about a bug they found:

    Question: {question}

    Knowledge base context:
    {domain_context}

    Relevant code context:
    {code_context}

    Provide a concise, actionable answer (under 200 words). Focus on MCSL-specific
    behaviour and how it might relate to the bug. If you don't know, say so clearly.
""")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def notify_devs_of_bug(
    card_id: str,
    card_name: str,
    bug_description: str,
    trello_client,
    slack_client,
) -> dict:
    """DM all Trello card members about a bug found by the AI QA Agent.

    Returns {"sent_count": int, "error": str}. Never raises.
    """
    try:
        members = trello_client.get_card_members(card_id)
        if not members:
            return {"sent_count": 0, "error": ""}

        sent = 0
        for member in members:
            member_id = member.get("id", "")
            dev_name = member.get("fullName") or member.get("username") or "Developer"
            if not member_id:
                continue
            message = BUG_DM_PROMPT.format(
                dev_name=dev_name,
                card_name=card_name,
                bug_description=bug_description,
            )
            try:
                slack_client.send_dm(member_id, message)
                sent += 1
            except Exception as dm_err:
                logger.warning("Failed to DM %s for card %s: %s", member_id, card_id, dm_err)

        return {"sent_count": sent, "error": ""}
    except Exception as exc:
        logger.error("notify_devs_of_bug failed: %s", exc)
        return {"sent_count": 0, "error": str(exc)}


def ask_domain_expert(question: str, model: str | None = None) -> str:
    """Ask the MCSL domain expert a question backed by RAG + Claude.

    Returns an answer string. Never raises — returns a fallback on any failure.
    """
    # Fetch domain context
    domain_context = ""
    try:
        from rag.vectorstore import search
        docs = search(question, k=5)
        domain_context = "\n\n---\n\n".join(d.page_content for d in docs)
    except Exception as exc:
        logger.warning("Domain RAG search failed in ask_domain_expert: %s", exc)
        domain_context = "Knowledge base unavailable."

    # Fetch code context (MCSL-specific source types)
    code_context = ""
    try:
        from rag.code_indexer import search_code
        server_docs = search_code(question, k=3, source_type="storepepsaas_server")
        client_docs = search_code(question, k=2, source_type="storepepsaas_client")
        all_docs = server_docs + client_docs
        code_context = "\n\n---\n\n".join(d.page_content for d in all_docs)
    except Exception as exc:
        logger.warning("Code RAG search failed in ask_domain_expert: %s", exc)
        code_context = "Code context unavailable."

    if not getattr(config, "ANTHROPIC_API_KEY", ""):
        return "Domain expert unavailable: ANTHROPIC_API_KEY not configured."

    try:
        prompt = DOMAIN_EXPERT_PROMPT.format(
            question=question,
            domain_context=domain_context or "No context retrieved.",
            code_context=code_context or "No code context retrieved.",
        )
        llm = ChatAnthropic(
            model=model or config.CLAUDE_SONNET_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=0,
            max_tokens=512,
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as exc:
        logger.error("ask_domain_expert Claude call failed: %s", exc)
        return f"Domain expert query failed: {exc}"
