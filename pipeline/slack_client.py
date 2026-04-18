"""Slack integration for MCSL QA Pipeline.

Dual delivery: webhook preferred, bot token fallback.
Uses raw requests — do NOT add slack_sdk dependency.
"""
from __future__ import annotations

import logging
import os
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
            params: dict[str, Any] = {
                "token": self.token,
                "limit": 200,
            }
            if cursor:
                params["cursor"] = cursor
            resp = requests.get(f"{SLACK_API}/users.list", params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                raise RuntimeError(f"users.list error: {data.get('error')}")
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
            params: dict[str, Any] = {
                "token": self.token,
                "limit": 200,
                "types": "public_channel,private_channel",
            }
            if cursor:
                params["cursor"] = cursor
            resp = requests.get(f"{SLACK_API}/conversations.list", params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                raise RuntimeError(f"conversations.list error: {data.get('error')}")
            for ch in data.get("channels", []):
                channels.append({"id": ch["id"], "name": ch.get("name", "")})
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
