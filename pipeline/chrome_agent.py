"""Chrome Agent for MCSL QA Pipeline.

Navigates to the live MCSL Shopify app (headless), captures the accessibility tree
and screenshot for a given feature, and extracts key selector data to enrich
automation code generation in automation_writer.py.

Reuses browser infrastructure from smart_ac_verifier — no new Playwright setup.
"""
from __future__ import annotations

import base64
import json
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import browser infrastructure from smart_ac_verifier at module level so
# tests can patch pipeline.chrome_agent._launch_browser etc. directly.
from pipeline.smart_ac_verifier import _launch_browser, _ax_tree, _navigate_in_app  # noqa: E402

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ExplorationResult:
    feature_name: str
    nav_destination: str = ""
    ax_tree_text: str = ""
    screenshot_b64: str = ""
    elements_json: str = ""
    error: str = ""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_nav_destination(feature_name: str, nav_hint: str = "") -> str:
    """Map feature name to MCSL nav destination (orders, labels, settings, etc.)."""
    if nav_hint:
        return nav_hint.lower()
    name = feature_name.lower()
    if any(k in name for k in ("order", "label", "shipment")):
        return "orders"
    if any(k in name for k in ("carrier", "fedex", "ups", "dhl", "usps")):
        return "carriers"
    if any(k in name for k in ("product", "item")):
        return "products"
    if any(k in name for k in ("setting", "config", "account")):
        return "settings"
    return ""


def _extract_elements_with_claude(ax_tree: str, feature_name: str) -> str:
    """Use Claude to extract key selectors from AX tree. Returns JSON string."""
    try:
        import config
        if not getattr(config, "ANTHROPIC_API_KEY", ""):
            return json.dumps({"error": "ANTHROPIC_API_KEY not set"})
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage
        prompt = (
            f"Extract key UI element selectors from this accessibility tree for the '{feature_name}' feature "
            f"in the MCSL Shopify app.\n\nReturn a JSON array of objects with keys: role, name, selector_hint.\n"
            f"Focus on buttons, inputs, and interactive elements relevant to {feature_name}.\n\n"
            f"AX Tree (truncated to 3000 chars):\n{ax_tree[:3000]}"
        )
        llm = ChatAnthropic(
            model=config.CLAUDE_SONNET_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=0,
            max_tokens=1024,
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip() if hasattr(response, "content") else str(response)
        # Extract JSON array from response
        json_match = re.search(r"\[.*\]", raw, re.DOTALL)
        return json_match.group(0) if json_match else json.dumps([])
    except Exception as exc:
        logger.warning("Element extraction failed: %s", exc)
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def explore_feature(feature_name: str, nav_hint: str = "") -> ExplorationResult:
    """Navigate to the MCSL app feature section and capture element data.

    Returns ExplorationResult. Never raises — returns error field on any failure.
    Uses headless=True for background exploration from Streamlit.
    """
    pw = browser = ctx = page = None
    try:
        import config

        pw, browser, ctx, page = _launch_browser(headless=True)

        store = getattr(config, "STORE", "")
        if not store:
            return ExplorationResult(
                feature_name=feature_name,
                error="STORE not configured in config.py",
            )

        # Navigate to MCSL app
        page.goto(
            f"https://{store}.myshopify.com/admin/apps/mcsl-qa",
            wait_until="domcontentloaded",
        )
        page.wait_for_timeout(5000)  # Wait for iframe to fully load

        # Navigate to feature section
        destination = _resolve_nav_destination(feature_name, nav_hint)
        if destination:
            try:
                _navigate_in_app(page, destination, store)
                page.wait_for_timeout(2000)
            except Exception as nav_exc:
                logger.debug("Navigation to %s failed (non-fatal): %s", destination, nav_exc)

        # Capture AX tree and screenshot
        ax = _ax_tree(page)
        screenshot_bytes = page.screenshot(type="png")
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()

        # Extract element selectors with Claude
        elements_json = _extract_elements_with_claude(ax, feature_name)

        return ExplorationResult(
            feature_name=feature_name,
            nav_destination=destination or "home",
            ax_tree_text=ax,
            screenshot_b64=screenshot_b64,
            elements_json=elements_json,
        )

    except Exception as exc:
        logger.warning("explore_feature failed for '%s': %s", feature_name, exc)
        return ExplorationResult(feature_name=feature_name, error=str(exc))
    finally:
        try:
            if page:
                page.close()
            if ctx:
                ctx.close()
            if browser:
                browser.close()
            if pw:
                pw.stop()
        except Exception:
            pass
