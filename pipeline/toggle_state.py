"""Live MCSL store/toggle state capture for Validate AC."""
from __future__ import annotations

import logging
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


def capture_store_and_toggle_state(app_url: str, timeout_ms: int = 12000) -> ToggleCaptureResult:
    """Open the MCSL app with stored auth and capture orders/toggles API data."""
    if not (app_url or "").strip():
        return ToggleCaptureResult(app_url=app_url, error="App URL is required.")

    pw = browser = ctx = page = None
    orders_payload: Any = None
    toggles_payload: Any = None
    deadline = time.time() + (timeout_ms / 1000)

    try:
        from pipeline.smart_ac_verifier import _launch_browser

        pw, browser, ctx, page = _launch_browser(headless=True)

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
                    if isinstance(data, dict) and ("orders" in data or "storeUUID" in str(data) or "accountUUID" in str(data)):
                        orders_payload = data
            except Exception:
                return

        page.on("response", _handle_response)
        page.goto(app_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3500)
        page.reload(wait_until="domcontentloaded")

        while time.time() < deadline and (orders_payload is None or toggles_payload is None):
            page.wait_for_timeout(500)

        toggle_map = _extract_toggle_map(toggles_payload)

        store_uuid = _walk_for_key(orders_payload, "storeUUID")
        account_uuid = _walk_for_key(orders_payload, "accountUUID")

        if not orders_payload and not toggles_payload:
            return ToggleCaptureResult(app_url=app_url, error="Could not capture orders/toggles API responses from the app.")

        return ToggleCaptureResult(
            app_url=app_url,
            store_uuid=store_uuid,
            account_uuid=account_uuid,
            toggle_map=toggle_map,
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
