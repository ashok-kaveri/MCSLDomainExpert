"""Slack QA bot — answer questions from Slack via Socket Mode.

Answers questions three ways:
  • Direct messages to the bot.
  • @-mentions in any channel the bot is in.
  • Plain (un-mentioned) messages that *look like a query* in allowlisted
    channels (``SLACK_QA_CHANNELS``) — so a dedicated QA channel like
    ``qa_members_internal`` can be used by just typing a question.

Replies are posted in-thread.

Run as a long-lived daemon:

    .venv/bin/python -m pipeline.slack_qa_bot

Required env (in .env):
    SLACK_BOT_TOKEN   xoxb-...   (bot token — already used by the rest of the app)
    SLACK_APP_TOKEN   xapp-...   (app-level token with connections:write; enable Socket Mode)
Optional env:
    SLACK_QA_CHANNELS  comma-separated channel names or IDs the bot answers in
                       without a mention, e.g. "qa_members_internal".

Slack app setup (one time): see the README section / the steps printed by ``--check``.
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys

import config  # noqa: F401 — imported for its side effect: loads .env

from pipeline.qa_question_router import answer_question
from pipeline.support_guide_slack import parse_support_guide_request
from pipeline.test_trigger_slack import parse_run_tests_request
from pipeline.env_sample_slack import parse_env_sample_request

SLACK_API = "https://slack.com/api"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("slack_qa_bot")

_MENTION_RE = re.compile(r"<@[A-Z0-9]+>")


def _strip_mentions(text: str) -> str:
    return _MENTION_RE.sub("", text or "").strip()


def _parse_triggers() -> list[str]:
    """Text keywords that address THIS bot in a channel (case-insensitive).

    From SLACK_QA_TRIGGERS (comma-separated). A leading '@' is optional in both
    config and the user's message. Default: 'mcslbot'. This lets several domain
    experts share a channel — each only answers when its own keyword (or its real
    Slack @mention) is used.
    """
    raw = os.getenv("SLACK_QA_TRIGGERS", "mcslbot")
    return [t.strip().lstrip("@").lower() for t in raw.split(",") if t.strip()]


def _match_trigger(text: str, triggers: list[str]) -> tuple[bool, str]:
    """If `text` is addressed to this bot via a keyword, return (True, message-without-keyword).

    Matches an optional leading '@' + keyword, followed by ':'/whitespace/end.
    Real Slack @mentions are handled separately by the app_mention event.
    """
    stripped = (text or "").lstrip()
    for kw in triggers:
        m = re.match(rf"@?{re.escape(kw)}\b[:,]?\s*", stripped, re.IGNORECASE)
        if m:
            return True, stripped[m.end():].strip()
    return False, ""


def _parse_channel_allowlist() -> list[str]:
    raw = os.getenv("SLACK_QA_CHANNELS", "")
    return [c.strip().lstrip("#") for c in raw.split(",") if c.strip()]


def _resolve_channel_ids(names_or_ids: list[str]) -> set[str]:
    """Resolve channel names (and passthrough IDs) to channel IDs via Slack API.

    IDs (starting with C or G) are kept as-is. Names are looked up across public
    and private channels the bot can see. Unresolved names are logged and skipped.
    """
    if not names_or_ids:
        return set()
    ids: set[str] = set()
    pending = []
    for item in names_or_ids:
        if re.fullmatch(r"[CG][A-Z0-9]+", item):
            ids.add(item)
        else:
            pending.append(item.lower())
    if not pending:
        return ids

    import requests
    headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN','')}"}
    cursor = ""
    name_to_id: dict[str, str] = {}
    try:
        while True:
            resp = requests.get(
                "https://slack.com/api/conversations.list",
                headers=headers,
                params={
                    "types": "public_channel,private_channel",
                    "limit": 1000,
                    "exclude_archived": True,
                    "cursor": cursor,
                },
                timeout=15,
            ).json()
            for c in resp.get("channels", []):
                name_to_id[c.get("name", "").lower()] = c.get("id", "")
            cursor = resp.get("response_metadata", {}).get("next_cursor", "")
            if not cursor:
                break
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not resolve channel names (%s); use channel IDs in SLACK_QA_CHANNELS", exc)

    for name in pending:
        cid = name_to_id.get(name)
        if cid:
            ids.add(cid)
        else:
            logger.warning("Channel %r not found / bot not a member — skipping", name)
    return ids


def _check_env() -> tuple[bool, str]:
    bot = os.getenv("SLACK_BOT_TOKEN", "")
    app = os.getenv("SLACK_APP_TOKEN", "")
    problems = []
    if not bot.startswith("xoxb-"):
        problems.append("SLACK_BOT_TOKEN missing or not an xoxb- bot token")
    if not app.startswith("xapp-"):
        problems.append("SLACK_APP_TOKEN missing or not an xapp- app-level token "
                         "(enable Socket Mode in your Slack app and generate one)")
    if problems:
        return False, "; ".join(problems)
    return True, "Slack tokens look valid."


def _slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", (text or "").strip()).strip("_")[:80] or "support_guide"


def _upload_bytes(channel: str, thread_ts: str, filename: str, title: str,
                  data: bytes, initial_comment: str = "") -> tuple[bool, str]:
    """Upload file bytes into a thread via Slack's modern external-upload API.

    Returns (ok, error). Used in preference to the deprecated files.upload.
    Requires the bot to have the ``files:write`` scope.
    """
    import requests
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{SLACK_API}/files.getUploadURLExternal", headers=headers,
                         params={"filename": filename, "length": len(data)}, timeout=20).json()
        if not r.get("ok"):
            return False, r.get("error", "getUploadURLExternal failed")
        up = requests.post(r["upload_url"], files={"file": (filename, data)}, timeout=60)
        if up.status_code != 200:
            return False, f"upload POST status {up.status_code}"
        comp = requests.post(
            f"{SLACK_API}/files.completeUploadExternal", headers=headers,
            data={
                "files": json.dumps([{"id": r["file_id"], "title": title}]),
                "channel_id": channel,
                "thread_ts": thread_ts,
                "initial_comment": initial_comment,
            }, timeout=20).json()
        if not comp.get("ok"):
            return False, comp.get("error", "completeUploadExternal failed")
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _post_long_text(say, thread_ts: str, header: str, text: str) -> None:
    """Fallback delivery: post a header then the body chunked under Slack's limit."""
    say(text=header, thread_ts=thread_ts)
    limit = 3500
    buf = ""
    for line in (text or "").splitlines(keepends=True):
        if len(buf) + len(line) > limit:
            say(text=buf or line, thread_ts=thread_ts)
            buf = ""
        buf += line
    if buf.strip():
        say(text=buf, thread_ts=thread_ts)


def _deliver_guides(channel: str, thread_ts: str, say, items: list[tuple[str, str]]) -> None:
    """Render each (title, markdown) guide to PDF and upload it, falling back to text.

    PDF matches the dashboard handoff format via ``handoff_docs.render_pdf_bytes``.
    Falls back to a .md file, then to chunked text, if PDF render or upload fails.
    """
    for title, md in items:
        slug = _slugify(title)
        pdf_bytes = b""
        try:
            from pipeline.handoff_docs import render_pdf_bytes
            pdf_bytes = render_pdf_bytes(title, md)
        except Exception as exc:  # noqa: BLE001
            logger.warning("PDF render failed for %r (%s); will try markdown/text", title, exc)

        if pdf_bytes:
            ok, err = _upload_bytes(channel, thread_ts, f"{slug}.pdf", title, pdf_bytes,
                                    initial_comment=f":page_facing_up: {title}")
            if ok:
                continue
            logger.warning("PDF upload failed (%s); trying markdown file", err)

        ok, err = _upload_bytes(channel, thread_ts, f"{slug}.md", title,
                                (md or "").encode("utf-8"),
                                initial_comment=f":blue_book: {title}")
        if not ok:
            logger.warning("file upload failed (%s); posting as text", err)
            _post_long_text(say, thread_ts, f"*:blue_book: {title}*", md)


def _handle_support_guide(req: dict, say, event: dict, thread_ts: str) -> None:
    """Generate and deliver a support guide for a card / lane request."""
    from pipeline import support_guide_slack as sg
    channel = event.get("channel")
    kind = req.get("kind")

    if kind == "unknown":
        say(text=("I can generate a support guide — give me a Trello card URL/ID, or a lane name. "
                  "e.g. `generate support guide for lane \"MCSL 381\"` "
                  "or `generate per-card support guides for lane \"MCSL 381\"`."),
            thread_ts=thread_ts)
        return

    try:
        if kind == "card":
            say(text=f":hourglass_flowing_sand: Generating support guide for card `{req['card_ref']}`…",
                thread_ts=thread_ts)
            title, md = sg.generate_card_guide(req["card_ref"])
            _deliver_guides(channel, thread_ts, say, [(f"Support Guide — {title}", md)])

        elif kind == "lane":
            say(text=f":hourglass_flowing_sand: Generating combined support guide for lane “{req['lane_name']}”…",
                thread_ts=thread_ts)
            title, md, n = sg.generate_lane_combined(req["lane_name"])
            _deliver_guides(channel, thread_ts, say, [(f"Combined Support Guide — {title} ({n} cards)", md)])

        elif kind == "lane_per_card":
            say(text=f":hourglass_flowing_sand: Generating per-card support guides for lane “{req['lane_name']}”…",
                thread_ts=thread_ts)
            lane, guides = sg.generate_lane_per_card(req["lane_name"])
            say(text=f"Generated {len(guides)} guide(s) for “{lane}” — uploading…", thread_ts=thread_ts)
            _deliver_guides(channel, thread_ts, say, [(f"{lane} — {name}", md) for name, md in guides])

    except ValueError as exc:
        say(text=f":warning: {exc}", thread_ts=thread_ts)
    except Exception as exc:  # noqa: BLE001
        logger.exception("support guide generation failed")
        say(text=f":warning: Failed to generate support guide: {exc}", thread_ts=thread_ts)


def _format_test_result(keyword: str, n_specs: int, result) -> str:
    if getattr(result, "error", ""):
        return f":warning: Test run for `{keyword}` failed to execute: {result.error}"
    dur = f"{result.duration_ms/1000:.0f}s" if result.duration_ms else "n/a"
    head = (f"*Test run — `{keyword}`*: "
            f":white_check_mark: {result.passed} passed · "
            f":x: {result.failed} failed · :fast_forward: {result.skipped} skipped "
            f"(of {result.total} tests, {dur})")
    lines = [head]
    fails = [s for s in result.specs if s.status not in ("passed", "skipped")]
    if fails:
        lines.append("Failures:")
        for s in fails[:15]:
            lines.append(f"  • {s.status}: {s.title or s.file}")
        if len(fails) > 15:
            lines.append(f"  …and {len(fails) - 15} more")
    return "\n".join(lines)


def _handle_run_tests(req: dict, say, event: dict, thread_ts: str) -> None:
    """Run targeted Playwright specs matching the keyword and post the result."""
    from pipeline import test_trigger_slack as tt
    keyword = req.get("keyword", "")

    # Tag run (smoke/sanity/regression/onboarding/...) → run by --grep across the suite.
    tag = tt.detect_tag(keyword)
    if tag:
        say(text=(f":test_tube: Running *{tag}* tests across the suite "
                  f"(real browser vs the live store — this can take a while)…"),
            thread_ts=thread_ts)
        try:
            result = tt.run_by_tag(tag)
        except Exception as exc:  # noqa: BLE001
            logger.exception("tag test run failed")
            say(text=f":warning: Test run errored: {exc}", thread_ts=thread_ts)
            return
        say(text=_format_test_result(tag, result.total, result), thread_ts=thread_ts)
        return

    repo, specs, folders = tt.find_specs(keyword)
    if not specs:
        say(text=(f":mag: No specs matched `{keyword or '(empty)'}`. "
                  f"Try a feature area: {', '.join(folders)}."),
            thread_ts=thread_ts)
        return
    if len(specs) > tt.MAX_SPECS:
        say(text=(f":warning: `{keyword}` matches {len(specs)} specs — too broad for a targeted run "
                  f"(max {tt.MAX_SPECS}). Narrow it to a folder or spec name. "
                  f"Areas: {', '.join(folders)}."),
            thread_ts=thread_ts)
        return

    say(text=(f":test_tube: Running {len(specs)} spec(s) matching `{keyword}` "
              f"(real browser vs the live store — this can take a few minutes)…"),
        thread_ts=thread_ts)
    try:
        result = tt.run_specs(repo, specs)
    except Exception as exc:  # noqa: BLE001
        logger.exception("test run failed")
        say(text=f":warning: Test run errored: {exc}", thread_ts=thread_ts)
        return
    say(text=_format_test_result(keyword, len(specs), result), thread_ts=thread_ts)


def _handle_env_sample(say, event: dict, thread_ts: str) -> None:
    """Post git-tracked env sample/template files. Never serves real env files."""
    from pipeline import env_sample_slack as es
    samples = es.get_env_samples()
    if not samples:
        say(text=(":mag: No git-tracked env *sample* file found in the automation repo. "
                  "(Real `.env` / `carrier-envs/*.env` are never shared — they hold live secrets.)"),
            thread_ts=thread_ts)
        return
    for rel, content in samples:
        fname = rel.rsplit("/", 1)[-1]
        ok, err = _upload_bytes(event.get("channel"), thread_ts, fname, rel,
                                content.encode("utf-8"),
                                initial_comment=f":page_facing_up: `{rel}` (template — no secrets)")
        if not ok:
            logger.warning("env sample upload failed (%s); posting as text", err)
            body = content if len(content) < 3500 else content[:3500] + "\n…(truncated)"
            say(text=f"*`{rel}`* (template — no secrets):\n```{body}```", thread_ts=thread_ts)


def build_app(allowed_channels: set[str] | None = None, triggers: list[str] | None = None):
    """Build the Bolt app with handlers wired. Imported lazily so tests don't need slack_bolt.

    Args:
        allowed_channels: channel IDs where the bot listens. If None, resolved
            from the SLACK_QA_CHANNELS env var.
        triggers: text keywords that address this bot (e.g. ["mcslbot"]). If None,
            resolved from SLACK_QA_TRIGGERS. In a channel the bot answers ONLY when
            explicitly addressed — by a real Slack @mention OR a trigger keyword —
            so multiple domain-expert bots can coexist in one channel.
    """
    from slack_bolt import App

    if allowed_channels is None:
        allowed_channels = _resolve_channel_ids(_parse_channel_allowlist())
    if triggers is None:
        triggers = _parse_triggers()

    app = App(token=os.getenv("SLACK_BOT_TOKEN"))

    def _handle(text: str, say, event: dict) -> None:
        question = _strip_mentions(text)
        logger.info("Q (%s): %r", event.get("channel", "?"), question)
        thread_ts = event.get("thread_ts") or event.get("ts")

        # Action intent: send env sample/template file(s).
        if parse_env_sample_request(question):
            _handle_env_sample(say, event, thread_ts)
            return

        # Action intent: run targeted Playwright tests.
        run_req = parse_run_tests_request(question)
        if run_req:
            _handle_run_tests(run_req, say, event, thread_ts)
            return

        # Action intent: support-guide generation (Trello card / lane) → file reply.
        guide_req = parse_support_guide_request(question)
        if guide_req:
            _handle_support_guide(guide_req, say, event, thread_ts)
            return

        try:
            answer = answer_question(question)
        except Exception as exc:  # noqa: BLE001 — never let one bad question kill the daemon
            logger.exception("answer failed")
            answer = f":warning: Sorry, I hit an error answering that: {exc}"
        say(text=answer, thread_ts=thread_ts)

    @app.event("app_mention")
    def on_mention(event, say):  # noqa: ANN001
        _handle(event.get("text", ""), say, event)

    @app.event("message")
    def on_message(event, say):  # noqa: ANN001
        # Ignore bot echoes, edits/joins, and anything the bot itself posted.
        if event.get("bot_id") or event.get("subtype"):
            return
        channel_type = event.get("channel_type")
        text = event.get("text", "")

        # Direct messages: always answer (the DM is already addressed to this bot).
        if channel_type == "im":
            _handle(text, say, event)
            return

        # Allowlisted channels: answer ONLY when explicitly addressed by a trigger
        # keyword (e.g. "@mcslbot …"). Real Slack @mentions are handled by
        # on_mention above. This keeps the bot quiet unless called — so FedEx/AUPost
        # experts can share the channel without all of them answering.
        if event.get("channel") in allowed_channels:
            matched, cleaned = _match_trigger(text, triggers)
            if matched:
                _handle(cleaned, say, event)

    return app


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    ok, msg = _check_env()
    if "--check" in argv:
        print(("OK: " if ok else "NOT READY: ") + msg)
        return 0 if ok else 1
    if not ok:
        logger.error("Cannot start: %s", msg)
        return 1

    from slack_bolt.adapter.socket_mode import SocketModeHandler

    names = _parse_channel_allowlist()
    allowed = _resolve_channel_ids(names)
    triggers = _parse_triggers()
    if names:
        logger.info("Listening in channels: %s -> %s",
                    ", ".join(names), ", ".join(sorted(allowed)) or "(none resolved)")
    logger.info("Channel trigger keywords: %s (or a real @mention of this app)",
                ", ".join(f"@{t}" for t in triggers) or "(none)")

    app = build_app(allowed_channels=allowed, triggers=triggers)
    logger.info("Starting MCSL QA Slack bot (Socket Mode)… DM me, @mention me, or use a trigger keyword in a channel.")
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
