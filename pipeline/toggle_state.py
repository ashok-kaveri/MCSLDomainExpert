"""Live MCSL store/toggle state capture for Validate AC."""
from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ToggleCaptureResult:
    app_url: str
    store_uuid: str = ""
    account_uuid: str = ""
    toggle_map: dict[str, bool] = field(default_factory=dict)
    error: str = ""


def _walk_for_key(payload: Any, key: str) -> str:
    if isinstance(payload, dict):
        if key in payload and payload.get(key):
            return str(payload.get(key))
        for value in payload.values():
            found = _walk_for_key(value, key)
            if found:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = _walk_for_key(item, key)
            if found:
                return found
    return ""


def _walk_for_any_key(payload: Any, keys: list[str]) -> str:
    for key in keys:
        found = _walk_for_key(payload, key)
        if found:
            return found
    return ""


def _extract_order_level_uuid(payload: Any, key: str) -> str:
    """Prefer UUIDs from concrete order items before any broader fallback search."""
    if not isinstance(payload, dict):
        return ""
    orders = payload.get("orders")
    if isinstance(orders, list):
        for item in orders:
            if isinstance(item, dict):
                value = item.get(key)
                if value:
                    return str(value)
    return ""


def _wait_networkidle_best_effort(page: Any, timeout_ms: int = 5000, fallback_ms: int = 2000) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        page.wait_for_timeout(fallback_ms)


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def normalize_toggle_name(name: str) -> str:
    return _normalize(name)


def compute_toggle_status(required_toggles: list[str], toggle_map: dict[str, bool]) -> dict[str, list[str]]:
    enabled_keys = {key for key, value in (toggle_map or {}).items() if bool(value)}
    disabled_keys = {key for key, value in (toggle_map or {}).items() if not bool(value)}

    enabled_labels: list[str] = []
    missing_labels: list[str] = []
    unknown_labels: list[str] = []

    for toggle in required_toggles or []:
        norm = normalize_toggle_name(toggle)
        matched_enabled = [key for key in enabled_keys if norm == key or norm in key or key in norm]
        matched_disabled = [key for key in disabled_keys if norm == key or norm in key or key in norm]
        if matched_enabled:
            enabled_labels.append(toggle)
        elif matched_disabled:
            missing_labels.append(toggle)
        else:
            unknown_labels.append(toggle)

    return {
        "enabled": enabled_labels,
        "missing": missing_labels + unknown_labels,
        "unknown": unknown_labels,
    }


def _extract_toggle_map(payload: Any) -> dict[str, bool]:
    toggle_map: dict[str, bool] = {}
    if not isinstance(payload, dict):
        return toggle_map

    raw_toggles = payload.get("toggles") or payload.get("data") or payload

    if isinstance(raw_toggles, dict):
        for key, value in raw_toggles.items():
            if isinstance(value, bool):
                toggle_map[normalize_toggle_name(str(key))] = value
            elif isinstance(value, dict):
                for marker in ("enabled", "active", "value", "status"):
                    if isinstance(value.get(marker), bool):
                        toggle_map[normalize_toggle_name(str(key))] = value[marker]
                        break
    elif isinstance(raw_toggles, list):
        for item in raw_toggles:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("key") or item.get("toggle") or item.get("id")
            if not name:
                continue
            enabled = None
            for marker in ("enabled", "active", "value", "status"):
                val = item.get(marker)
                if isinstance(val, bool):
                    enabled = val
                    break
            if enabled is not None:
                toggle_map[normalize_toggle_name(str(name))] = enabled
    return toggle_map


def _looks_like_orders_payload(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    if _walk_for_any_key(payload, ["storeUUID", "storeId", "store_id"]):
        return True
    if _walk_for_any_key(payload, ["accountUUID", "accountId", "account_id"]):
        orders = payload.get("orders")
        if isinstance(orders, list) and orders:
            return True
    return False


def _click_account_card_if_present(page: Any) -> None:
    """Mirror mcsl-test-automation account-card handling before app interactions."""
    try:
        if not page.get_by_role("heading", name="Choose an account").is_visible(timeout=750):
            return
    except Exception:
        return

    user_email = (
        os.getenv("SHOPIFY_EMAIL")
        or os.getenv("SHOPIFY_USERNAME")
        or os.getenv("USER_EMAIL")
        or ""
    ).strip()
    try:
        account_card = page.locator("a.choose-account-card")
        if user_email:
            candidate = account_card.filter(has_text=re.compile(re.escape(user_email), re.I))
            if candidate.count():
                account_card = candidate.first
            else:
                account_card = account_card.first
        else:
            account_card = account_card.first
        account_card.wait_for(state="visible", timeout=10000)
        account_card.click()
        _wait_networkidle_best_effort(page, timeout_ms=5000, fallback_ms=2000)
    except Exception as exc:
        logger.warning("Account-card selection failed: %s", exc)


def _prime_app_for_toggle_capture(page: Any, app_url: str) -> None:
    """Open the app, pass any account selector, and trigger orders/toggles API calls."""
    from pipeline.smart_ac_verifier import _get_app_frame, _navigate_in_app

    store_match = re.search(r"/store/([^/]+)/", app_url or "")
    store_slug = store_match.group(1) if store_match else ""

    page.goto(app_url, wait_until="domcontentloaded")
    _wait_networkidle_best_effort(page, timeout_ms=5000, fallback_ms=2000)

    # If the app is already open, move immediately. Only handle account card if it appears.
    deadline = time.time() + 20
    while time.time() < deadline:
        _click_account_card_if_present(page)
        app_frame = _get_app_frame(page)
        try:
            orders_button = app_frame.get_by_role("button", name=re.compile("orders", re.I))
            menu_button = app_frame.get_by_role("button", name="Menu")
            if orders_button.count() or menu_button.count():
                break
        except Exception:
            pass
        page.wait_for_timeout(500)

    _navigate_in_app(page, "orders", store_slug)
    page.wait_for_timeout(3000)


def _retry_capture_if_partial(page: Any, app_url: str) -> None:
    """Re-trigger app bootstrap when only one of the required API payloads was observed."""
    try:
        page.reload(wait_until="domcontentloaded")
    except Exception:
        try:
            page.goto(app_url, wait_until="domcontentloaded")
        except Exception as exc:
            logger.warning("Toggle capture retry navigation failed: %s", exc)
            return
    _wait_networkidle_best_effort(page, timeout_ms=5000, fallback_ms=1500)
    _prime_app_for_toggle_capture(page, app_url)


def capture_store_and_toggle_state(app_url: str, timeout_ms: int = 25000) -> ToggleCaptureResult:
    """Open the MCSL app with stored auth and capture orders/toggles API data."""
    if not (app_url or "").strip():
        return ToggleCaptureResult(app_url=app_url, error="App URL is required.")

    pw = browser = ctx = page = None
    orders_payload: Any = None
    toggles_payload: Any = None
    deadline = time.time() + (timeout_ms / 1000)

    try:
        from pipeline.smart_ac_verifier import _launch_browser

        pw, browser, ctx, page = _launch_browser(headless=False)

        def _handle_response(response) -> None:
            nonlocal orders_payload, toggles_payload
            try:
                url = (response.url or "").lower()
                if response.status != 200:
                    return
                if "toggles" in url and toggles_payload is None:
                    toggles_payload = response.json()
                elif "orders" in url and orders_payload is None:
                    data = response.json()
                    if _looks_like_orders_payload(data):
                        orders_payload = data
            except Exception:
                return

        page.on("response", _handle_response)
        _prime_app_for_toggle_capture(page, app_url)
        try:
            page.reload(wait_until="domcontentloaded")
            _click_account_card_if_present(page)
            page.wait_for_timeout(2500)
        except Exception as exc:
            logger.warning("Toggle capture reload step skipped: %s", exc)

        retried_partial = False
        while time.time() < deadline and (orders_payload is None or toggles_payload is None):
            if not retried_partial and (orders_payload is not None or toggles_payload is not None):
                retried_partial = True
                _retry_capture_if_partial(page, app_url)
            page.wait_for_timeout(500)

        toggle_map = _extract_toggle_map(toggles_payload)

        store_uuid = (
            _extract_order_level_uuid(orders_payload, "storeUUID")
            or _walk_for_any_key(orders_payload, ["storeUUID"])
        )
        account_uuid = (
            _extract_order_level_uuid(orders_payload, "accountUUID")
            or _walk_for_any_key(orders_payload, ["accountUUID"])
            or _walk_for_any_key(orders_payload, ["accountId", "account_id"])
        )

        if not orders_payload and not toggles_payload:
            return ToggleCaptureResult(app_url=app_url, error="Could not capture orders/toggles API responses from the app.")

        partial_error = ""
        if orders_payload and not toggles_payload:
            partial_error = "Captured orders API response, but no toggles API response was observed."
        elif toggles_payload and not orders_payload:
            partial_error = "Captured toggles API response, but no orders API response was observed."
        elif orders_payload and not store_uuid:
            partial_error = "Captured orders API response, but no storeUUID was found in the payload."

        return ToggleCaptureResult(
            app_url=app_url,
            store_uuid=store_uuid,
            account_uuid=account_uuid,
            toggle_map=toggle_map,
            error=partial_error,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("capture_store_and_toggle_state failed: %s", exc)
        return ToggleCaptureResult(app_url=app_url, error=str(exc))
    finally:
        for obj in (ctx, browser, pw):
            try:
                if obj:
                    obj.close()
            except Exception:
                pass
