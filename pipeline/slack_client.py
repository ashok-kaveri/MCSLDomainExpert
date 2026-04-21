"""Slack integration for MCSL QA Pipeline.

Dual delivery: webhook preferred, bot token fallback.
Uses raw requests — do NOT add slack_sdk dependency.
"""
from __future__ import annotations

import logging
import os
import re
from typing import Any

import requests

logger = logging.getLogger(__name__)

SLACK_API = "https://slack.com/api"


class SlackClient:
    def __init__(self, token=None, channel=None, webhook_url=None):
        self.webhook_url = webhook_url if webhook_url is not None else os.getenv("SLACK_WEBHOOK_URL", "")
        self.token       = token       if token       is not None else os.getenv("SLACK_BOT_TOKEN", "")
        self.channel     = channel     if channel     is not None else os.getenv("SLACK_CHANNEL", "")
        if not self.webhook_url and not self.token:
            raise ValueError(
                "Slack credentials missing. Set SLACK_WEBHOOK_URL OR SLACK_BOT_TOKEN in .env"
            )

    def _bot_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def _slack_error(self, api_name: str, error_code: str) -> RuntimeError:
        if error_code == "invalid_auth":
            return RuntimeError(
                f"{api_name} error: invalid_auth (check SLACK_BOT_TOKEN; it may be expired, revoked, or from the wrong workspace)"
            )
        return RuntimeError(f"{api_name} error: {error_code}")

    def _post(self, payload: dict, channel: str | None = None) -> dict:
        """Webhook-first delivery. Falls back to chat.postMessage with bot token."""
        if self.webhook_url:
            resp = requests.post(self.webhook_url, json=payload, timeout=15)
            resp.raise_for_status()
            return {"ok": True, "ts": ""}  # webhook returns "ok" text not JSON
        target = channel or self.channel
        payload["channel"] = target
        resp = requests.post(
            f"{SLACK_API}/chat.postMessage",
            headers=self._bot_headers(),
            json=payload,
            timeout=15,
        )
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack API error: {data.get('error')}")
        return data

    def send_dm(self, user_id: str, text: str) -> str:
        """Open a DM channel with user_id then post text. Returns message timestamp."""
        open_resp = requests.post(
            f"{SLACK_API}/conversations.open",
            headers=self._bot_headers(),
            json={"users": user_id},
            timeout=15,
        )
        open_resp.raise_for_status()
        dm_channel = open_resp.json()["channel"]["id"]
        msg_resp = requests.post(
            f"{SLACK_API}/chat.postMessage",
            headers=self._bot_headers(),
            json={"channel": dm_channel, "text": text, "mrkdwn": True},
            timeout=15,
        )
        msg_resp.raise_for_status()
        return msg_resp.json().get("ts", "")

    def post_to_channel(self, text: str, channel: str | None = None) -> dict:
        """Post text to a channel. channel overrides self.channel."""
        target = channel or self.channel
        resp = requests.post(
            f"{SLACK_API}/chat.postMessage",
            headers=self._bot_headers(),
            json={"channel": target, "text": text, "mrkdwn": True},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def post_signoff(self, message: str, channel: str | None = None) -> dict:
        """Post a sign-off message via webhook or bot token."""
        return self._post({"text": message, "mrkdwn": True}, channel=channel)

    def search_users(self, query: str) -> list[dict]:
        """Paginated search of workspace members matching query string.
        Returns list of {id, real_name, display_name} dicts.
        Filters out deleted users, bots, and USLACKBOT."""
        results: list[dict] = []
        cursor = ""
        q_lower = query.lower()
        while True:
            params: dict[str, Any] = {"limit": 200}
            if cursor:
                params["cursor"] = cursor
            resp = requests.get(
                f"{SLACK_API}/users.list",
                headers=self._bot_headers(),
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                raise self._slack_error("users.list", data.get("error", "unknown_error"))
            for member in data.get("members", []):
                if member.get("deleted") or member.get("is_bot") or member.get("id") == "USLACKBOT":
                    continue
                profile = member.get("profile", {})
                names = [
                    profile.get("real_name", ""),
                    profile.get("display_name", ""),
                    member.get("name", ""),
                ]
                if any(q_lower in n.lower() for n in names if n):
                    results.append({
                        "id": member["id"],
                        "real_name": profile.get("real_name", ""),
                        "display_name": profile.get("display_name", ""),
                    })
            cursor = data.get("response_metadata", {}).get("next_cursor", "")
            if not cursor:
                break
        return results

    def list_channels(self) -> list[dict]:
        """Return paginated list of channels bot can see. Each dict: {id, name}."""
        channels: list[dict] = []
        cursor = ""
        while True:
            params: dict[str, Any] = {"limit": 200, "types": "public_channel,private_channel"}
            if cursor:
                params["cursor"] = cursor
            resp = requests.get(
                f"{SLACK_API}/conversations.list",
                headers=self._bot_headers(),
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                raise self._slack_error("conversations.list", data.get("error", "unknown_error"))
            for ch in data.get("channels", []):
                channels.append({
                    "id": ch["id"],
                    "name": ch.get("name", ""),
                    "is_private": bool(ch.get("is_private", False)),
                })
            cursor = data.get("response_metadata", {}).get("next_cursor", "")
            if not cursor:
                break
        return channels


# ---------------------------------------------------------------------------
# Module-level helpers — used by pipeline_dashboard.py and bug_reporter.py
# ---------------------------------------------------------------------------

def slack_configured() -> bool:
    """True when at least one delivery mode is available."""
    webhook = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    token   = os.getenv("SLACK_BOT_TOKEN",   "").strip()
    channel = os.getenv("SLACK_CHANNEL",      "").strip()
    return bool(webhook or (token and channel))


def dm_token_configured() -> bool:
    """True when bot token is present (required for DM operations)."""
    return bool(os.getenv("SLACK_BOT_TOKEN", "").strip())


def _make_client() -> SlackClient:
    """Construct SlackClient from env. Raises ValueError if not configured."""
    return SlackClient()


def search_slack_users(query: str) -> tuple[list[dict], str]:
    """Search workspace members. Returns (results, error_msg). error_msg="" on success."""
    try:
        client = _make_client()
        return client.search_users(query), ""
    except Exception as exc:
        return [], str(exc)


def list_slack_channels() -> tuple[list[dict], str, str]:
    """List channels. Returns (channels, error_msg, note). note is informational."""
    try:
        client = _make_client()
        channels = client.list_channels()
        note = "Only channels the bot is invited to appear." if channels else ""
        return channels, "", note
    except Exception as exc:
        return [], str(exc), ""


def post_results(run_result: Any, release: str = "") -> dict:
    """Post release automation results to the configured Slack channel."""
    target_release = release or getattr(run_result, "release", "") or "Generate Automation Script"
    lines = [
        f"*MCSL Automation — {target_release}*",
        (
            f"Passed: {getattr(run_result, 'passed', 0)}/{getattr(run_result, 'total', 0)}"
            f" · Failed: {getattr(run_result, 'failed', 0)}"
            f" · Skipped: {getattr(run_result, 'skipped', 0)}"
            f" · Duration: {getattr(run_result, 'duration_ms', 0) / 1000:.1f}s"
        ),
    ]
    failed_specs = [
        f"{spec.file} — {spec.title}"
        for spec in getattr(run_result, "specs", []) or []
        if getattr(spec, "status", "") in ("failed", "timedOut")
    ]
    if failed_specs:
        lines.append("")
        lines.append("*Failed:*")
        lines.extend(f"• {item}" for item in failed_specs[:5])

    try:
        client = _make_client()
        response = client.post_to_channel("\n".join(lines))
        return {"ok": bool(response.get("ok", False)), "ts": response.get("ts", ""), "error": response.get("error", "")}
    except Exception as exc:
        return {"ok": False, "ts": "", "error": str(exc)}


def upload_file_to_slack_channel(
    channel_id: str,
    filename: str,
    file_bytes: bytes,
    title: str = "",
    initial_comment: str = "",
) -> dict:
    """Upload a file to a Slack channel using files.upload."""
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        return {"ok": False, "file_id": "", "error": "SLACK_BOT_TOKEN is not set"}
    if not channel_id:
        return {"ok": False, "file_id": "", "error": "No channel selected"}
    try:
        resp = requests.post(
            f"{SLACK_API}/files.upload",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "channels": channel_id,
                "filename": filename,
                "title": title or filename,
                "initial_comment": initial_comment,
            },
            files={"file": (filename, file_bytes)},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            return {"ok": False, "file_id": "", "error": data.get("error", "unknown_error")}
        return {"ok": True, "file_id": data.get("file", {}).get("id", ""), "error": ""}
    except Exception as exc:
        return {"ok": False, "file_id": "", "error": str(exc)}


def upload_file_to_slack_user(
    user_id: str,
    filename: str,
    file_bytes: bytes,
    title: str = "",
    initial_comment: str = "",
) -> dict:
    """Open a DM and upload a file into that Slack DM channel."""
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        return {"ok": False, "file_id": "", "channel": "", "error": "SLACK_BOT_TOKEN is not set"}
    if not user_id:
        return {"ok": False, "file_id": "", "channel": "", "error": "No user_id provided"}
    try:
        open_resp = requests.post(
            f"{SLACK_API}/conversations.open",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"users": user_id},
            timeout=15,
        )
        open_resp.raise_for_status()
        open_data = open_resp.json()
        if not open_data.get("ok"):
            return {"ok": False, "file_id": "", "channel": "", "error": f"conversations.open: {open_data.get('error')}"}
        dm_channel = open_data["channel"]["id"]
        upload_res = upload_file_to_slack_channel(
            channel_id=dm_channel,
            filename=filename,
            file_bytes=file_bytes,
            title=title,
            initial_comment=initial_comment,
        )
        return {
            "ok": upload_res.get("ok", False),
            "file_id": upload_res.get("file_id", ""),
            "channel": dm_channel,
            "error": upload_res.get("error", ""),
        }
    except Exception as exc:
        return {"ok": False, "file_id": "", "channel": "", "error": str(exc)}


def send_ac_dm(
    user_ids: list[str],
    card_name: str,
    ac_text: str,
    content_label: str = "AC",
) -> dict:
    """DM AC/TC content to a list of Slack user IDs.
    Returns {"ok": True, "sent_count": N} or {"ok": False, "error": msg}."""
    try:
        client = _make_client()
        text = f"*{card_name}* — {content_label}:\n\n{ac_text}"
        sent = 0
        for uid in user_ids:
            client.send_dm(uid, text)
            sent += 1
        return {"ok": True, "sent_count": sent}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def post_content_to_slack_channel(
    channel_id: str,
    card_name: str,
    content_text: str,
    content_label: str = "Content",
) -> dict:
    """Post content to a channel, splitting at 2900-char Slack block limit.
    Returns {"ok": True} or {"ok": False, "error": msg}."""
    _BLOCK_LIMIT = 2900
    try:
        client = _make_client()
        header = f"*{card_name}* — {content_label}:\n\n"
        full_text = header + content_text
        chunks = [full_text[i : i + _BLOCK_LIMIT] for i in range(0, len(full_text), _BLOCK_LIMIT)]
        for chunk in chunks:
            client.post_to_channel(chunk, channel=channel_id)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def detect_toggle_details(card_desc: str, card_name: str = "", card_comments: str = "") -> list[dict[str, str]]:
    """Detect likely feature toggles and preserve raw config keys when available."""
    text = f"{card_name}\n{card_desc}\n{card_comments}".strip()
    seen: set[str] = set()
    toggles: list[dict[str, str]] = []

    def _key_to_readable(value: str) -> str:
        return (
            re.sub(r"(?i)^[A-Za-z0-9_]*uuid\.", "", value)
            .replace(".enabled", "")
            .replace(".disabled", "")
            .replace(".flag", "")
            .replace(".toggle", "")
            .replace(".", " ")
            .replace("_", " ")
        )

    def _add(value: str, key_template: str = "") -> None:
        clean = re.sub(r"\s+", " ", value).strip(" -:.'\"")
        clean = re.split(r"[,;]\s*", clean, maxsplit=1)[0].strip()
        lower = clean.lower()
        words = re.findall(r"[a-z0-9]+", lower)
        generic_only = {
            "toggle",
            "flag",
            "feature",
            "feature flag",
            "rollout",
            "prerequisite",
        }
        if not clean:
            return
        if lower in generic_only:
            return
        if len(words) > 7:
            return
        if re.search(r"\b(?:enable|enables|enabled|disable|disables|disabled|turn on|turn off)\b", lower):
            return
        if re.search(r"\b(?:default state|default enabled state|before qa|after qa|prerequisite)\b", lower):
            return
        if lower in seen:
            if key_template:
                for item in toggles:
                    if item["label"].lower() == lower and not item.get("key_template"):
                        item["key_template"] = key_template
                        break
            return
        seen.add(lower)
        toggles.append({"label": clean, "key_template": key_template})

    patterns = [
        r"\btoggle\b[:\s-]*([A-Za-z0-9 _.-]{4,80})",
        r"\btoggle\s+to\s+(?:enable|disable|turn on|turn off)\b[:\s-]*([A-Za-z0-9 _.-]{4,80})",
        r"\brelated\s+toggle\b.*?[:\s-]+([A-Za-z0-9 _.-]{4,80})",
        r"\bfeature flag\b[:\s-]*([A-Za-z0-9 _.-]{4,80})",
        r"\bflag\b[:\s-]*([A-Za-z0-9 _.-]{4,80})",
        r"\bfeature\b[:\s-]*([A-Za-z0-9 _.-]{4,80})",
        r"\brollout\b[:\s-]*([A-Za-z0-9 _.-]{4,80})",
        r"\b(?:enable|activate|turn on|add)\s+['\"]?([A-Za-z0-9 _.-]{4,80})['\"]?\s+(?:toggle|flag|feature flag)\b",
        r"\bplease\s+(?:enable|activate|turn on)\s+['\"]?([A-Za-z0-9 _.-]{4,80})['\"]?\s+(?:for|on)\s+(?:the\s+)?store\b",
        r"\b(?:toggle|flag|feature flag|rollout)\s+(?:is|=)\s*['\"]?([A-Za-z0-9 _.-]{4,80})",
        r"\b(?:enable|activate|turn on|roll out)\s+['\"]?([A-Za-z0-9 _.-]{4,80})['\"]?\s+(?:on|for)\s+(?:the\s+)?store\b",
        r"\b(?:toggle name|flag name|feature name)\b[:\s-]*([A-Za-z0-9 _.-]{4,80})",
        r"\b(?:toggle key|flag key|feature key)\b[:\s-]*([A-Za-z0-9 _.-]{4,120})",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            _add(match)

    # Structured Shopify flag/webhook keys appear in copied payloads and comments.
    for match in re.findall(
        r'"((?:all\.myshopify\.com\.)?shopify\.(?:webhook|feature)[^"]{5,120})"',
        text,
    ):
        readable = (
            match.replace("all.myshopify.com.", "")
            .replace("shopify.webhook.", "")
            .replace("shopify.feature.", "")
            .replace(".", " ")
        )
        _add(readable)

    for match in re.findall(
        r"\b((?:all\.myshopify\.com\.)?shopify\.(?:webhook|feature)[A-Za-z0-9._-]{5,120})\b",
        text,
    ):
        readable = (
            match.replace("all.myshopify.com.", "")
            .replace("shopify.webhook.", "")
            .replace("shopify.feature.", "")
            .replace(".", " ")
        )
        _add(readable)

    # Generic copied config keys like "accountUUID.country.wise.customs.value.enabled": true
    for match in re.findall(
        r'"?([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+){2,}\.(?:enabled|disabled|flag|toggle))"?\s*:\s*(?:true|false|"[^"]+"|\d+)',
        text,
        flags=re.IGNORECASE,
    ):
        _add(_key_to_readable(match), key_template=match)

    # Fallback for Trello notes where the label is on one line and the key is on the next line.
    cue_re = re.compile(r"(?i)\b(toggle|feature flag|flag|feature name|flag name|toggle name|toggle key|flag key|feature key|rollout)\b")
    key_re = re.compile(r'"?([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+){2,}(?:\.(?:enabled|disabled|flag|toggle))?)"?')
    lines = [line.strip() for line in text.splitlines()]
    for idx, line in enumerate(lines[:-1]):
        if not cue_re.search(line):
            continue
        next_line = lines[idx + 1]
        key_match = key_re.search(next_line)
        if key_match:
            _add(_key_to_readable(key_match.group(1)), key_template=key_match.group(1))

    return toggles


def detect_toggles(card_desc: str, card_name: str = "", card_comments: str = "") -> list[str]:
    """Detect likely feature toggle names from card text."""
    return [item["label"] for item in detect_toggle_details(card_desc, card_name, card_comments)]


def _format_toggle_lines(toggles: list[Any], account_uuid: str = "") -> str:
    """Render toggle names and raw config keys; UUIDs are shown separately in the message."""
    lines: list[str] = []
    for item in toggles or []:
        if isinstance(item, dict):
            label = (item.get("label") or "").strip()
            key_template = (item.get("key_template") or "").strip()
        else:
            label = str(item).strip()
            key_template = ""
        if label:
            lines.append(f"  • `{label}`")
        if key_template:
            lines.append(f'    ↳ `"{key_template}": true`')
    return "\n".join(lines)


def notify_toggle_enablement(
    user_id: str,
    card_name: str,
    toggles: list[Any],
    store_name: str,
    store_url: str = "",
    store_uuid: str = "",
    account_uuid: str = "",
) -> dict:
    """DM a user asking them to enable toggles before QA starts."""
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        return {"ok": False, "error": "SLACK_BOT_TOKEN is not set"}
    if not user_id:
        return {"ok": False, "error": "No user_id provided"}

    toggle_lines = _format_toggle_lines(toggles, account_uuid=account_uuid)
    admin_url = store_url or (f"https://admin.shopify.com/store/{store_name}" if store_name else "")
    text = (
        f"🔧 *Toggle Enable Request - {card_name}*\n\n"
        f"QA is about to start on this card and needs the following toggle(s) enabled on *{store_name or 'target store'}*:\n\n"
        f"{toggle_lines}\n\n"
        f"Store UUID: `{store_uuid or 'not captured'}`\n"
        f"Account UUID: `{account_uuid or 'not captured'}`\n"
        f"🔗 Store admin: {admin_url or '(not provided)'}\n\n"
        f"Please enable them and reply `done` so QA can continue."
    )
    try:
        client = _make_client()
        open_resp = requests.post(
            f"{SLACK_API}/conversations.open",
            headers=client._bot_headers(),
            json={"users": user_id},
            timeout=15,
        )
        open_resp.raise_for_status()
        open_data = open_resp.json()
        if not open_data.get("ok"):
            return {"ok": False, "error": f"conversations.open: {open_data.get('error')}"}
        dm_channel = open_data["channel"]["id"]
        msg_resp = requests.post(
            f"{SLACK_API}/chat.postMessage",
            headers=client._bot_headers(),
            json={"channel": dm_channel, "text": text, "mrkdwn": True},
            timeout=15,
        )
        msg_resp.raise_for_status()
        msg_data = msg_resp.json()
        if not msg_data.get("ok"):
            return {"ok": False, "error": f"chat.postMessage: {msg_data.get('error')}"}
        return {"ok": True, "ts": msg_data.get("ts", ""), "channel": dm_channel}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_toggle_reply(channel_id: str, after_ts: str) -> dict:
    """Check if a DM channel has a confirmation reply after the sent message."""
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        return {"confirmed": False, "error": "SLACK_BOT_TOKEN is not set"}

    done_keywords = {"done", "yes", "enabled", "ok", "okay", "completed", "ready", "activated", "turned on", "✅", "👍"}
    try:
        resp = requests.get(
            f"{SLACK_API}/conversations.history",
            headers={"Authorization": f"Bearer {token}"},
            params={"channel": channel_id, "oldest": after_ts, "limit": 10},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            return {"confirmed": False, "error": data.get("error", "unknown")}
        for msg in data.get("messages", []):
            if msg.get("subtype") == "bot_message":
                continue
            text = (msg.get("text") or "").strip().lower()
            if any(keyword in text for keyword in done_keywords):
                return {"confirmed": True, "reply": msg.get("text", ""), "ts": msg.get("ts", "")}
        return {"confirmed": False, "reply": "", "ts": ""}
    except Exception as exc:
        return {"confirmed": False, "error": str(exc)}


def notify_dev_of_toggle(
    user_id: str,
    dev_name: str,
    card_name: str,
    toggles: list[Any],
    store_name: str,
    store_url: str = "",
    store_uuid: str = "",
    account_uuid: str = "",
) -> dict:
    """Escalate toggle enablement request to a developer via Slack DM."""
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        return {"ok": False, "error": "SLACK_BOT_TOKEN is not set"}
    if not user_id:
        return {"ok": False, "error": "No user_id provided"}

    admin_url = store_url or (f"https://admin.shopify.com/store/{store_name}" if store_name else "")
    toggle_lines = _format_toggle_lines(toggles, account_uuid=account_uuid)
    text = (
        f"🔧 *Toggle Enable Request - {card_name}*\n\n"
        f"Hi {dev_name}, QA is blocked until these toggle(s) are enabled on *{store_name or 'target store'}*:\n\n"
        f"{toggle_lines}\n\n"
        f"Store UUID: `{store_uuid or 'not captured'}`\n"
        f"Account UUID: `{account_uuid or 'not captured'}`\n"
        f"🔗 Store admin: {admin_url or '(not provided)'}\n\n"
        "Ashok has not replied yet. If you enable them, please reply `done` here."
    )
    try:
        client = _make_client()
        open_resp = requests.post(
            f"{SLACK_API}/conversations.open",
            headers=client._bot_headers(),
            json={"users": user_id},
            timeout=15,
        )
        open_resp.raise_for_status()
        open_data = open_resp.json()
        if not open_data.get("ok"):
            return {"ok": False, "error": f"conversations.open: {open_data.get('error')}"}
        dm_channel = open_data["channel"]["id"]
        msg_resp = requests.post(
            f"{SLACK_API}/chat.postMessage",
            headers=client._bot_headers(),
            json={"channel": dm_channel, "text": text, "mrkdwn": True},
            timeout=15,
        )
        msg_resp.raise_for_status()
        msg_data = msg_resp.json()
        if not msg_data.get("ok"):
            return {"ok": False, "error": f"chat.postMessage: {msg_data.get('error')}"}
        return {"ok": True, "ts": msg_data.get("ts", ""), "channel": dm_channel}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def send_dm_to_user(user_id: str, text: str) -> dict:
    """Send a plain Slack DM to a user id."""
    try:
        client = _make_client()
        ts = client.send_dm(user_id, text)
        return {"ok": True, "ts": ts}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def post_signoff(
    release: str,
    verified_cards: list[dict],
    backlog_cards: list[dict],
    mentions: list[str] | None = None,
    cc: str = "",
    qa_lead: str = "",
    backlog_links: list[dict] | None = None,
    channel: str | None = None,
) -> dict:
    """Format and post the standard MCSL sign-off message to Slack.

    Message format (Slack mrkdwn):
      @mention1 @mention2

      We've completed testing *RELEASE* and it's good for the release ✅

      *Cards Verified:*
      Card Name
      https://trello.com/c/xxx

      *Cards added to backlog (N):*
      Bug title 1

      *QA Signed off* :tada:

      CC: @manager
      _Signed by: QA Lead_
    """
    try:
        client = _make_client()
        mention_str = "  ".join(f"@{m}" for m in (mentions or []))
        cards_section = "\n".join(
            f"{c['name']}\n{c.get('url', '')}" for c in (verified_cards or [])
        )
        backlog_items = backlog_links or backlog_cards or []
        backlog_section = "\n".join(
            b.get("name", str(b)) for b in backlog_items
        )
        lines = []
        if mention_str:
            lines.append(mention_str)
        lines.append("")
        lines.append(f"We've completed testing  *{release}*  and it's good for the release ✅")
        lines.append("")
        lines.append("*Cards Verified:*")
        lines.append("")
        lines.append(cards_section)
        lines.append("")
        lines.append(f"*Cards added to backlog ({len(backlog_items)}):*")
        lines.append("")
        if backlog_section:
            lines.append(backlog_section)
        lines.append("")
        lines.append("*QA Signed off* :tada:")
        if cc:
            lines.append("")
            lines.append(f"CC: @{cc.lstrip('@')}")
        if qa_lead:
            lines.append(f"_Signed by: {qa_lead}_")

        message = "\n".join(lines)
        return client.post_signoff(message, channel=channel)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
