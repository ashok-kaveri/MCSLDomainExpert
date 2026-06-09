#!/bin/bash
# Phase 8 of the new-carrier QA store pipeline. Run after Ashok confirms in
# Slack that the requested toggles are enabled.
#
#   - Backs up mcsl-test-automation/.env (so we restore it on exit)
#   - Copies the carrier-env file to .env so playwright/dotenv picks it up
#   - Runs npx playwright test --grep @smoke  --project="Google Chrome"
#   - Runs npx playwright test --grep @sanity --project="Google Chrome"
#   (Chrome-only: Firefox/Safari projects are skipped — keeps setup-firefox/setup-safari
#    auth-state failures out of the report and matches how the team runs day-to-day.)
#   - Restores the original .env regardless of pass/fail
#
# Usage:
#   bash scripts/run_smoke_sanity_for_carrier.sh \\
#        "$MCSL_AUTOMATION_REPO_PATH/carrier-envs/<slug>.env"
#
# Repo path resolution (in order of precedence):
#   1. $MCSL_AUTOMATION_REPO_PATH env var
#   2. config.MCSL_AUTOMATION_REPO_PATH from this repo's config.py
#   3. fallback: ~/Documents/mcsl-test-automation
set -u

CARRIER_ENV="${1:-}"
if [[ -z "$CARRIER_ENV" || ! -f "$CARRIER_ENV" ]]; then
  echo "Usage: $0 <path-to-carrier-env-file>"
  echo "Example: $0 \"\$MCSL_AUTOMATION_REPO_PATH/carrier-envs/<slug>.env\""
  exit 2
fi

# Resolve REPO path portably across team members' machines.
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="${MCSL_AUTOMATION_REPO_PATH:-}"
if [[ -z "$REPO" ]]; then
  # Fallback to config.py default (which itself falls back to ~/Documents/mcsl-test-automation)
  REPO="$(python3 -c "import sys; sys.path.insert(0, '$HERE/..'); import config; print(config.MCSL_AUTOMATION_REPO_PATH)" 2>/dev/null \
         || echo "$HOME/Documents/mcsl-test-automation")"
fi
if [[ ! -d "$REPO" ]]; then
  echo "ERROR: mcsl-test-automation repo not found at: $REPO"
  echo "  Set MCSL_AUTOMATION_REPO_PATH in your env or .env file."
  exit 2
fi
echo "[setup] using automation repo: $REPO"
DOTENV="$REPO/.env"
BACKUP="$REPO/.env.smoke-sanity-backup.$$"

# Restore original .env on ANY exit path (success, failure, signal)
restore_env() {
  if [[ -f "$BACKUP" ]]; then
    mv "$BACKUP" "$DOTENV"
    echo "[cleanup] restored original .env from $BACKUP"
  fi
}
trap restore_env EXIT INT TERM

# ── Backup + swap .env ──────────────────────────────────────────────────────
if [[ -f "$DOTENV" ]]; then
  cp "$DOTENV" "$BACKUP"
  echo "[setup] backed up original .env → $BACKUP"
fi
cp "$CARRIER_ENV" "$DOTENV"
SLUG=$(grep "^SHOPIFY_STORE_NAME=" "$CARRIER_ENV" | cut -d= -f2)
CARRIER_NAME=$(grep "^CARRIER=" "$CARRIER_ENV" | cut -d= -f2)
echo "[setup] using carrier-env: $CARRIER_ENV"
echo "[setup] target store     : $SLUG"
echo "[setup] CARRIER          : $CARRIER_NAME"
echo ""

cd "$REPO"

# ── Smoke ──────────────────────────────────────────────────────────────────
echo "================================================================"
echo "SMOKE  — npx playwright test --grep @smoke --project=\"Google Chrome\""
echo "================================================================"
SMOKE_LOG="/tmp/smoke_${CARRIER_NAME}.log"
set +e
npx playwright test --grep @smoke --project="Google Chrome" 2>&1 | tee "$SMOKE_LOG"
SMOKE_EXIT=$?
set -e
echo "[smoke] exit code: $SMOKE_EXIT"
echo "[smoke] log saved to $SMOKE_LOG"
echo ""

# ── Sanity ─────────────────────────────────────────────────────────────────
echo "================================================================"
echo "SANITY — npx playwright test --grep @sanity --project=\"Google Chrome\""
echo "================================================================"
SANITY_LOG="/tmp/sanity_${CARRIER_NAME}.log"
set +e
npx playwright test --grep @sanity --project="Google Chrome" 2>&1 | tee "$SANITY_LOG"
SANITY_EXIT=$?
set -e
echo "[sanity] exit code: $SANITY_EXIT"
echo "[sanity] log saved to $SANITY_LOG"
echo ""

# ── Summary ────────────────────────────────────────────────────────────────
echo "================================================================"
echo "SUMMARY for $CARRIER_NAME ($SLUG)"
echo "================================================================"
echo "smoke  : $([ $SMOKE_EXIT -eq 0 ] && echo PASS || echo "FAIL (exit $SMOKE_EXIT)")"
echo "sanity : $([ $SANITY_EXIT -eq 0 ] && echo PASS || echo "FAIL (exit $SANITY_EXIT)")"
echo ""
echo "Logs:"
echo "  $SMOKE_LOG"
echo "  $SANITY_LOG"

# Overall exit = worst of the two
if [[ $SMOKE_EXIT -ne 0 || $SANITY_EXIT -ne 0 ]]; then
  exit 1
fi
exit 0
