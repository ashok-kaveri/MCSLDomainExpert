#!/usr/bin/env bash
# Launch the MCSL QA Slack bot (Socket Mode daemon).
#
# Usage:
#   scripts/run_slack_bot.sh           # verify tokens, then start the daemon
#   scripts/run_slack_bot.sh --check   # only verify tokens/config, don't start
#
# Requires in .env:
#   SLACK_BOT_TOKEN=xoxb-...   SLACK_APP_TOKEN=xapp-...
# Optional:
#   SLACK_QA_CHANNELS=qa_members_internal   # channels answered without @mention
set -euo pipefail

cd "$(dirname "$0")/.."

PY=".venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "No .venv found. Create it: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

if [[ "${1:-}" == "--check" ]]; then
  exec "$PY" -m pipeline.slack_qa_bot --check
fi

# Fail fast with a clear message if tokens aren't ready, before starting the loop.
if ! "$PY" -m pipeline.slack_qa_bot --check; then
  echo "Fix the above, then re-run. (Add SLACK_APP_TOKEN from Slack > Socket Mode.)" >&2
  exit 1
fi

echo "Starting MCSL QA Slack bot… (Ctrl-C to stop)"
exec "$PY" -m pipeline.slack_qa_bot
