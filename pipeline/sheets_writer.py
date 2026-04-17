"""
pipeline/sheets_writer.py — Google Sheets writer for MCSL test case data.
Phase 07 Plan 02 — RQA-04

Exports: append_to_sheet, detect_tab, check_duplicates, TestCaseRow, DuplicateMatch, SHEET_TABS, TAB_KEYWORDS

NOTE: gspread is imported INSIDE append_to_sheet() and check_duplicates() — NOT at module top —
so this module can be imported without gspread installed.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

import config


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SHEET_TABS = [
    "Shipping Labels",
    "Rate Calculation",
    "Tracking",
    "Returns",
    "Additional Services",
    "Settings & Config",
    "Order Management",
    "Draft Plan",
]

TAB_KEYWORDS = {
    "Shipping Labels": ["label", "generate label", "print label", "bulk label"],
    "Rate Calculation": ["rate", "quote", "pricing", "shipping cost"],
    "Tracking": ["track", "tracking", "shipment status"],
    "Returns": ["return", "return label", "rma"],
    "Additional Services": ["signature", "dry ice", "alcohol", "battery", "hal", "insurance"],
    "Settings & Config": ["setting", "config", "carrier account", "api key", "credential"],
    "Order Management": ["order", "fulfillment", "sync"],
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class TestCaseRow:
    si_no: int = 0
    epic: str = ""
    scenario: str = ""
    description: str = ""
    comments: str = ""
    priority: str = "Medium"
    details: str = ""
    pass_fail: str = ""
    release: str = ""


@dataclass
class DuplicateMatch:
    existing_scenario: str
    new_scenario: str
    similarity: float


# ---------------------------------------------------------------------------
# detect_tab
# ---------------------------------------------------------------------------

def detect_tab(card_name: str, test_cases_markdown: str) -> str:
    """Match card/TC text to SHEET_TABS using keyword lookup. Falls back to 'Draft Plan'."""
    combined = f"{card_name} {test_cases_markdown}".lower()
    for tab, keywords in TAB_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                return tab
    return "Draft Plan"


# ---------------------------------------------------------------------------
# parse_test_cases_to_rows (local implementation — parallel with card_processor.py)
# ---------------------------------------------------------------------------

def parse_test_cases_to_rows(
    card_name: str,
    test_cases_markdown: str,
    epic: str = "",
    positive_only: bool = False,
) -> list[TestCaseRow]:
    rows = []
    tc_blocks = re.split(r"(?=^## TC-\d+)", test_cases_markdown, flags=re.MULTILINE)
    si = 1
    for block in tc_blocks:
        block = block.strip()
        if not block or not block.startswith("## TC-"):
            continue
        title_match = re.match(r"## TC-\d+[:\s]+(.+)", block)
        scenario = title_match.group(1).strip() if title_match else card_name
        tc_type = "Positive"
        priority = "Medium"
        type_match = re.search(r"\*\*Type:\*\*\s*(.+)", block)
        if type_match:
            tc_type = type_match.group(1).strip()
        priority_match = re.search(r"\*\*Priority:\*\*\s*(.+)", block)
        if priority_match:
            priority = priority_match.group(1).strip()
        if positive_only and "negative" in tc_type.lower():
            continue
        gwt_parts = []
        for keyword in ("Given", "When", "Then"):
            m = re.search(
                rf"{keyword}\s+(.+?)(?=\n(?:Given|When|Then|##)|$)",
                block,
                re.DOTALL | re.IGNORECASE,
            )
            if m:
                gwt_parts.append(f"{keyword} {m.group(1).strip()}")
        description = "\n".join(gwt_parts) if gwt_parts else block[:200]
        rows.append(
            TestCaseRow(
                si_no=si,
                epic=epic or card_name,
                scenario=scenario,
                description=description,
                priority=priority,
            )
        )
        si += 1
    return rows


# ---------------------------------------------------------------------------
# check_duplicates
# ---------------------------------------------------------------------------

def check_duplicates(
    new_rows: list[TestCaseRow],
    tab_name: str,
    similarity_threshold: float = 0.75,
) -> list[DuplicateMatch]:
    """Check new rows against existing sheet rows for near-duplicates using SequenceMatcher."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_PATH, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(config.GOOGLE_SHEETS_ID)
        # Find matching tab (partial match)
        ws = None
        for worksheet in sh.worksheets():
            if tab_name.lower() in worksheet.title.lower():
                ws = worksheet
                break
        if ws is None:
            return []
        existing_values = ws.get_all_values()
        existing_scenarios = [row[2] for row in existing_values[1:] if len(row) > 2 and row[2]]
    except Exception as exc:
        logging.warning("check_duplicates failed to fetch sheet: %s", exc)
        return []

    duplicates = []
    for new_row in new_rows:
        for existing_scenario in existing_scenarios:
            ratio = SequenceMatcher(None, new_row.scenario.lower(), existing_scenario.lower()).ratio()
            if ratio >= similarity_threshold:
                duplicates.append(
                    DuplicateMatch(
                        existing_scenario=existing_scenario,
                        new_scenario=new_row.scenario,
                        similarity=ratio,
                    )
                )
    return duplicates


# ---------------------------------------------------------------------------
# append_to_sheet
# ---------------------------------------------------------------------------

def append_to_sheet(
    card_name: str,
    test_cases_markdown: str,
    epic: str = "",
    tab_name: str | None = None,
    release: str = "",
) -> dict:
    """Parse TCs and append to the correct MCSL master sheet tab. Returns metadata dict.

    gspread is imported INSIDE this function so callers can import sheets_writer
    without gspread installed.
    """
    import gspread
    from google.oauth2.service_account import Credentials

    target_tab = tab_name or detect_tab(card_name, test_cases_markdown)
    rows = parse_test_cases_to_rows(card_name, test_cases_markdown, epic=epic, positive_only=False)
    if not rows:
        return {"tab": target_tab, "rows_added": 0, "sheet_url": "", "release": release, "duplicates": []}

    # Add release to each row
    for row in rows:
        row.release = release

    # Connect to Google Sheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_PATH, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(config.GOOGLE_SHEETS_ID)

    # Find target worksheet (partial match for robustness)
    ws = None
    ws_titles = [w.title for w in sh.worksheets()]
    for title in ws_titles:
        if target_tab.lower() in title.lower() or title.lower() in target_tab.lower():
            ws = sh.worksheet(title)
            target_tab = title
            break
    if ws is None:
        # Fallback to Draft Plan
        for title in ws_titles:
            if "draft" in title.lower():
                ws = sh.worksheet(title)
                target_tab = title
                break
    if ws is None:
        raise ValueError(f"Sheet tab '{target_tab}' not found in {ws_titles}")

    # Find next SI No
    existing = ws.get_all_values()
    next_si = len(existing)  # header row counts as row 0

    # Check duplicates before writing
    duplicates = check_duplicates(rows, target_tab)

    # Append rows
    for row in rows:
        row.si_no = next_si
        ws.append_row([
            row.si_no,
            row.epic,
            row.scenario,
            row.description,
            row.comments,
            row.priority,
            row.details,
            row.pass_fail,
            row.release,
        ])
        next_si += 1

    sheet_url = f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEETS_ID}"
    return {
        "tab": target_tab,
        "rows_added": len(rows),
        "sheet_url": sheet_url,
        "release": release,
        "duplicates": duplicates,
    }
