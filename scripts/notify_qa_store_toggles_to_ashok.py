#!/usr/bin/env python3
"""Phase 7 of the new-carrier QA store pipeline:
  1. Capture the new store's accountUUID via the MCSL app (uses
     pipeline.toggle_state.capture_store_and_toggle_state which opens the app
     with stored auth and intercepts the orders API response).
  2. Substitute __ACCOUNT_UUID__ in templates/qa_store_toggles.json with the
     captured accountUUID.
  3. DM Ashok on Slack with the substituted JSON block and the message
     "please enable these toggles for my new store <slug>".

Prerequisites (must be true before running):
  - Store + QA app + plan + dev app + token done (phases 1-4.5).
  - Onboarding form completed + carrier registered in MCSL app (manual handoff).
  - Products seeded + dimensions set (phase 5).
  - At least ONE order placed on the store. The accountUUID is only present
    in /orders API responses, so capture fails on empty-orders stores.

Usage:
  PYTHONPATH=. .venv/bin/python scripts/notify_qa_store_toggles_to_ashok.py \\
      --store-slug madanindianpost \\
      --carrier-env-path "$MCSL_AUTOMATION_REPO_PATH/carrier-envs/<slug>.env"

The script will:
  - Auto-place one test order via pipeline.order_creator if --skip-order-create
    is NOT passed (uses the carrier env's product JSONs).
  - Capture accountUUID + storeUUID from the MCSL app.
  - Print the substituted toggle JSON.
  - Send to Ashok (or --dry-run to skip the Slack send).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def substitute_uuid(template_path: Path, account_uuid: str) -> dict:
    """Load the toggle template and substitute __ACCOUNT_UUID__ with the real UUID."""
    raw = template_path.read_text(encoding="utf-8")
    raw = raw.replace("__ACCOUNT_UUID__", account_uuid)
    data = json.loads(raw)
    return data.get("toggles", {})


def format_for_slack(toggles: dict) -> str:
    """Format the toggle dict as a copy-pasteable JSON block inside a Slack
    code fence. Preserves insertion order so the block reads the same as the
    template file."""
    lines = []
    for k, v in toggles.items():
        # Match the user's preferred indent / quoting (matches admin config dump)
        if isinstance(v, str):
            lines.append(f'  "{k}": "{v}",')
        elif isinstance(v, bool):
            lines.append(f'  "{k}": {str(v).lower()},')
        else:
            lines.append(f'  "{k}": {json.dumps(v)},')
    # Strip trailing comma on last line
    if lines:
        lines[-1] = lines[-1].rstrip(",")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("Usage:")[0])
    ap.add_argument("--store-slug", required=True, help="Realized Shopify store slug")
    ap.add_argument("--carrier-env-path", required=True, type=Path,
                    help="Path to the store's carrier-env file (needed for placing a test order)")
    ap.add_argument("--template", type=Path,
                    default=REPO_ROOT / "templates" / "qa_store_toggles.json",
                    help="Toggle template JSON (default: templates/qa_store_toggles.json)")
    ap.add_argument("--skip-order-create", action="store_true",
                    help="Skip placing a test order — only do this if the store already has ≥1 order")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the substituted toggle block without sending to Slack")
    args = ap.parse_args()

    app_url = f"https://admin.shopify.com/store/{args.store_slug}/apps/mcsl-qa"

    # ── Phase 7a: place a test order so accountUUID is in /orders response ───
    if not args.skip_order_create:
        print(f"[7a] placing one test order via carrier-env {args.carrier_env_path}…", flush=True)
        from pipeline.order_creator import create_order
        try:
            order_name = create_order(carrier_env_path=args.carrier_env_path)
            print(f"[7a] order created: {order_name}")
        except Exception as exc:
            print(f"[7a] ⚠️  order create failed: {exc}")
            print(f"[7a] proceeding to capture anyway (the store may have existing orders)")

    # ── Phase 7b: capture accountUUID via the MCSL app ───────────────────────
    print(f"\n[7b] capturing accountUUID from {app_url}…", flush=True)
    from pipeline.toggle_state import capture_store_and_toggle_state
    result = capture_store_and_toggle_state(app_url=app_url, timeout_ms=40000)

    print(f"[7b] store_uuid   = {result.store_uuid or '(not captured)'}")
    print(f"[7b] account_uuid = {result.account_uuid or '(not captured)'}")
    if result.error:
        print(f"[7b] error: {result.error}")
    if not result.account_uuid:
        print("\n❌ ABORT — accountUUID not captured. Likely causes:")
        print("   - No orders on the store (place one and re-run)")
        print("   - auth-chrome.json expired (re-login to MCSL app)")
        print("   - App's onboarding form not yet completed (do it manually first)")
        return 2

    # ── Phase 7c: substitute UUID into the template ──────────────────────────
    if not args.template.exists():
        print(f"❌ template not found: {args.template}", file=sys.stderr)
        return 3
    toggles = substitute_uuid(args.template, result.account_uuid)
    block = format_for_slack(toggles)

    print("\n" + "=" * 70)
    print(f"TOGGLE BLOCK for {args.store_slug} (accountUUID = {result.account_uuid})")
    print("=" * 70)
    print(block)
    print("=" * 70)

    if args.dry_run:
        print("\n--dry-run set; skipping Slack send.")
        return 0

    # ── Phase 7d: DM Ashok on Slack ──────────────────────────────────────────
    print("\n[7d] searching for Ashok Kumar in Slack…", flush=True)
    from pipeline.slack_client import search_slack_users, _make_client, SLACK_API
    import requests

    users, err = search_slack_users("Ashok Kumar")
    if not users:
        print(f"❌ could not find Ashok in Slack: {err or 'no match'}", file=sys.stderr)
        return 4
    ashok = users[0]
    print(f"[7d] recipient: {ashok.get('real_name')} ({ashok['id']})")

    text = (
        f"🆕 *New QA store ready — toggles request*\n\n"
        f"Hi Ashok, please enable these toggles for my new QA store *{args.store_slug}*.\n"
        f"Account UUID: `{result.account_uuid}`\n"
        f"Store URL: https://admin.shopify.com/store/{args.store_slug}\n\n"
        f"Toggle block (paste into admin config):\n"
        f"```\n{block}\n```\n\n"
        f"Thanks!"
    )

    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        print("❌ SLACK_BOT_TOKEN not set in env", file=sys.stderr)
        return 5

    client = _make_client()
    # Open DM channel
    open_resp = requests.post(
        f"{SLACK_API}/conversations.open",
        headers=client._bot_headers(),
        json={"users": ashok["id"]},
        timeout=15,
    )
    open_resp.raise_for_status()
    open_data = open_resp.json()
    if not open_data.get("ok"):
        print(f"❌ conversations.open failed: {open_data.get('error')}", file=sys.stderr)
        return 6
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
        print(f"❌ chat.postMessage failed: {msg_data.get('error')}", file=sys.stderr)
        return 7
    print(f"\n✅ Sent toggle request DM to Ashok (ts={msg_data.get('ts')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
