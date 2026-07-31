"""QA metrics — deterministic answers about automation coverage and release runs.

These functions read directly from the automation repo (specs + Playwright
report JSON) and never call an LLM, so they are fast and exact. They back the
canned metric questions answered by the Slack QA bot
(``pipeline/qa_question_router.py``).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import config
from pipeline.test_runner import enumerate_specs

# Matches a top-level test invocation: test(, test.only(, test.skip(, test.fixme(
# but NOT test.describe( / test.beforeEach( etc.
_TEST_BLOCK_RE = re.compile(r"\btest(?:\.(?:only|skip|fixme))?\s*\(")


def count_automated_cases(repo_path: str | None = None) -> dict:
    """Count automated coverage in the automation repo.

    Returns a dict with:
        spec_files:   number of ``*.spec.ts`` files under ``tests/``
        test_blocks:  approximate number of ``test(...)`` cases across those files
        folders:      number of top-level folders under ``tests/``
        by_folder:    {folder: spec_file_count}
    """
    repo_path = repo_path or config.MCSL_AUTOMATION_REPO_PATH
    grouped = enumerate_specs(repo_path)

    by_folder = {folder: len(specs) for folder, specs in grouped.items()}
    spec_files = sum(by_folder.values())

    test_blocks = 0
    root = Path(repo_path)
    for specs in grouped.values():
        for rel in specs:
            try:
                text = (root / rel).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            test_blocks += len(_TEST_BLOCK_RE.findall(text))

    return {
        "spec_files": spec_files,
        "test_blocks": test_blocks,
        "folders": len(by_folder),
        "by_folder": dict(sorted(by_folder.items())),
    }


def count_regression_cases() -> dict:
    """Count test-case rows in the MCSL TC / regression Google Sheet (per tab).

    Reads the live sheet via the service account (config.GOOGLE_SHEETS_ID /
    GOOGLE_CREDENTIALS_PATH). A "case" is approximated as a non-empty data row
    (rows minus a header row) per worksheet.

    Returns:
        available:   bool
        total:       total data rows across all tabs
        tab_count:   number of tabs
        by_tab:      {tab_name: data_row_count}
        error:       set when the sheet can't be read
    """
    try:
        from google.oauth2.service_account import Credentials
        import gspread
        from ingest.sheets_loader import SCOPES
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": f"Google Sheets libs unavailable: {exc}"}

    creds_path = Path(config.GOOGLE_CREDENTIALS_PATH)
    if not creds_path.exists():
        return {"available": False, "error": f"No credentials at {creds_path}"}

    try:
        creds = Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
        client = gspread.Client(auth=creds)
        spreadsheet = client.open_by_key(config.GOOGLE_SHEETS_ID)
        by_tab: dict[str, int] = {}
        for ws in spreadsheet.worksheets():
            non_empty = sum(1 for row in ws.get_all_values() if any(c.strip() for c in row))
            by_tab[ws.title] = max(non_empty - 1, 0)  # minus header row
        return {
            "available": True,
            "total": sum(by_tab.values()),
            "tab_count": len(by_tab),
            "by_tab": by_tab,
        }
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": f"Could not read regression sheet: {exc}"}


def _reports_dir(repo_path: str) -> Path:
    return Path(repo_path) / "reports"


def latest_release_run(repo_path: str | None = None) -> dict:
    """Read the latest stored Playwright run summary from the automation repo.

    Reflects the most recent run written to ``reports/`` (the reports dir keeps
    only the latest run, not a per-release-tag history).

    Returns a dict with:
        available:   bool — whether a summary report was found
        total:       tests in the latest run
        failures:    failed tests
        passed:      total - failures
        failure_rate, risk_level, decision, reason: passthrough from ai-summary.json
        flaky:       list of test names flagged flaky in ai-trend.json (best effort)
        error:       set when no report is available
    """
    repo_path = repo_path or config.MCSL_AUTOMATION_REPO_PATH
    summary_path = _reports_dir(repo_path) / "ai-summary.json"

    if not summary_path.exists():
        return {
            "available": False,
            "error": f"No run summary found at {summary_path}. Run the suite first.",
        }

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"available": False, "error": f"Could not read run summary: {exc}"}

    total = int(summary.get("totalTests", 0))
    failures = int(summary.get("totalFailures", 0))

    flaky: list[str] = []
    trend_path = _reports_dir(repo_path) / "ai-trend.json"
    if trend_path.exists():
        try:
            trend = json.loads(trend_path.read_text(encoding="utf-8"))
            if isinstance(trend, list):
                flaky = [t for t in trend if isinstance(t, str) and "flaky" in t.lower()]
        except (OSError, json.JSONDecodeError):
            pass

    return {
        "available": True,
        "total": total,
        "failures": failures,
        "passed": max(total - failures, 0),
        "failure_rate": summary.get("failureRate", ""),
        "risk_level": summary.get("riskLevel", ""),
        "decision": summary.get("decision", ""),
        "reason": summary.get("reason", ""),
        "flaky": flaky,
    }
