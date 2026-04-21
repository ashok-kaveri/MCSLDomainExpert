"""
pipeline/automation_writer.py — Playwright POM + spec code generation for MCSL automation.

Exports: write_automation, AutomationResult
"""
from __future__ import annotations

import os
import subprocess
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import config
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from pipeline.locator_knowledge import build_locator_context

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

NEW_POM_WRITER_PROMPT = """\
You are a senior QA automation engineer for the MCSL multi-carrier Shopify app.
Generate a TypeScript Playwright Page Object Model (POM) class and a spec file for the
feature described below.

Feature name: {feature_name}
Feature snake_case: {feature_snake}
Feature CamelCase class name: {ClassName}

Test cases (Markdown):
{test_cases}

MCSL app context (exploration data):
{exploration_data}

AI QA verification evidence (live browser findings, validated locators, request/log clues):
{ai_qa_context}

Additional POM context / existing patterns:
{pom_context}

Locator knowledge (automation repo + runtime memory):
{locator_context}

=== STRICT RULES FOR THE POM FILE ===
1. The POM class MUST extend BasePage: `class {ClassName}Page extends BasePage`
2. ALL locators for MCSL app elements MUST use `this.appFrame`, NOT `this.page`.
   Only Shopify admin elements outside the iframe (e.g. top-nav, billing modals) may use `this.page`.
3. Import BasePage: `import BasePage from '@pages/basePage';`
4. The file MUST end with: `export default {ClassName}Page;`
5. Constructor signature: `constructor(page: Page) {{ super(page); ... }}`

=== STRICT RULES FOR THE SPEC FILE ===
1. First import: `import {{ test, expect }} from '@setup/fixtures';`
2. Second line: `test.describe.configure({{ mode: "serial" }});`
3. Wrap all tests in: `test.describe("{feature_name}", {{ tag: "@regression" }}, () => {{ ... }});`
4. FIRST statement inside test.describe MUST be:
   `test.skip(!["mcsl-automation"].includes(process.env.SHOPIFY_STORE_NAME ?? ""), "Tests only run against mcsl-automation store");`
5. Each test case becomes a `test("Verify ...", async ({{ pages }}) => {{ ... }});` block.

=== OUTPUT FORMAT (REQUIRED — DO NOT DEVIATE) ===
Respond with EXACTLY two sections separated by these delimiters:

=== POM FILE: {pom_path} ===
<full TypeScript POM class here>

=== SPEC FILE: {spec_path} ===
<full TypeScript spec file here>

Do NOT include any explanation, markdown code fences, or extra text outside those two sections.
"""


EXISTING_POM_WRITER_PROMPT = """\
You are a senior QA automation engineer for the MCSL multi-carrier Shopify app.
Update the EXISTING Playwright automation files for the feature described below.

Feature name: {feature_name}

Test cases (Markdown):
{test_cases}

MCSL app context (exploration data):
{exploration_data}

AI QA verification evidence (live browser findings, validated locators, request/log clues):
{ai_qa_context}

Additional POM context / existing patterns:
{pom_context}

Locator knowledge (automation repo + runtime memory):
{locator_context}

Existing POM file: {pom_path}
Current POM contents:
{existing_pom}

Existing spec file: {spec_path}
Current spec contents:
{existing_spec}

Rules:
1. Update these existing files in place instead of creating new ones.
2. Preserve the existing class name/export style unless a change is required for correctness.
3. Reuse existing methods and locators where possible; extend them only when necessary.
4. Keep MCSL locators on `this.appFrame` unless the element is outside the iframe.
5. Keep Playwright structure compatible with the current automation repo conventions.

=== OUTPUT FORMAT (REQUIRED — DO NOT DEVIATE) ===
Respond with EXACTLY two sections separated by these delimiters:

=== POM FILE: {pom_path} ===
<full updated TypeScript POM file here>

=== SPEC FILE: {spec_path} ===
<full updated TypeScript spec file here>

Do NOT include any explanation, markdown code fences, or extra text outside those two sections.
"""

# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class AutomationResult:
    kind: str
    feature_name: str
    pom_path: str
    spec_path: str
    pom_code: str
    spec_code: str
    files_written: list[str] = field(default_factory=list)
    git_branch: str = ""
    git_pushed: bool = False
    push_error: str = ""
    skipped: bool = False
    detection_reason: str = ""
    tc_filter_summary: dict[str, int] = field(default_factory=dict)
    fix_passed: bool | None = None
    fix_iterations: int = 0
    fix_history: list[dict] = field(default_factory=list)
    error: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_snake_case(name: str) -> str:
    """Convert feature name to snake_case (spaces/hyphens to underscores, lowercase)."""
    return re.sub(r"[\s\-]+", "_", name).lower()


def _to_camel_case(name: str) -> str:
    """Convert feature name to CamelCase (e.g. 'order summary' -> 'OrderSummary')."""
    return "".join(word.title() for word in re.split(r"[\s\-_]+", name))


def _parse_automation_response(response_text: str) -> tuple[str, str]:
    """
    Parse Claude's response into (pom_code, spec_code).

    Expects:
        === POM FILE: ... ===
        <pom code>
        === SPEC FILE: ... ===
        <spec code>

    Returns ("", "") if the delimiters are not found.
    """
    pom_match = re.search(
        r"=== POM FILE:.*?===\n(.*?)(?==== SPEC FILE:|$)",
        response_text,
        re.DOTALL,
    )
    spec_match = re.search(
        r"=== SPEC FILE:.*?===\n(.*?)$",
        response_text,
        re.DOTALL,
    )

    pom_code = pom_match.group(1).strip() if pom_match else ""
    spec_code = spec_match.group(1).strip() if spec_match else ""
    return pom_code, spec_code


def _parse_block(raw: str, marker: str) -> str:
    match = re.search(rf"=== {marker}:.+?===\n([\s\S]+?)(?=\n===\s|\Z)", raw)
    if not match:
        return ""
    body = match.group(1).strip()
    body = re.sub(r"^```(?:typescript|ts)?\n?", "", body)
    body = re.sub(r"\n?```\s*$", "", body)
    return body


def _write_repo_file(repo_path: str, rel_path: str, content: str) -> None:
    abs_path = Path(repo_path) / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(content, encoding="utf-8")


def _read_repo_file(repo_path: str, rel_path: str) -> str:
    abs_path = Path(repo_path) / rel_path
    if not abs_path.exists():
        return ""
    return abs_path.read_text(encoding="utf-8")


def _get_automation_repo_path(repo_path: str = "") -> str:
    return repo_path or getattr(config, "MCSL_AUTOMATION_REPO_PATH", "")


def _normalize_words(text: str) -> set[str]:
    base = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text or "")
    base = base.replace("/", " ").replace("\\", " ").replace("_", " ").replace("-", " ")
    return set(re.findall(r"[a-z0-9]+", base.lower()))


def _infer_nav_hint_from_path(rel_path: str) -> str:
    lower = rel_path.lower()
    if "/orders/" in lower or lower.startswith("support/pages/orders/") or "pickup" in lower:
        return "orders"
    if "carrier" in lower:
        return "carriers"
    if "/products/" in lower:
        return "products"
    if "automationrules" in lower or "onlinestore" in lower or "createstore" in lower:
        return "settings"
    return ""


def _score_candidate(query: str, rel_path: str) -> float:
    qwords = _normalize_words(query)
    path_words = _normalize_words(Path(rel_path).stem.replace("page", ""))
    path_words |= _normalize_words(rel_path)
    if not qwords or not path_words:
        return 0.0
    overlap = len(qwords & path_words)
    if overlap == 0:
        return 0.0
    exact_phrase_bonus = 0.3 if Path(rel_path).stem.lower().replace("page", "") in query.lower().replace(" ", "") else 0.0
    return overlap / max(len(qwords), 1) + exact_phrase_bonus


def _find_related_spec(repo_root: Path, rel_path: str, query: str) -> str:
    tests_root = repo_root / "tests"
    if not tests_root.exists():
        return ""
    candidates = [
        str(path.relative_to(repo_root))
        for path in tests_root.rglob("*.spec.ts")
        if path.is_file()
    ]
    if not candidates:
        return ""
    parent_name = Path(rel_path).parent.name
    stem = Path(rel_path).stem.lower().replace("page", "")

    query_words = _normalize_words(query)
    collapsed_query = "".join(re.findall(r"[a-z0-9]+", query.lower()))

    def _spec_score(spec_rel: str) -> float:
        spec_words = _normalize_words(spec_rel)
        score = _score_candidate(f"{query} {parent_name} {stem}", spec_rel)
        lower = spec_rel.lower()
        if parent_name and parent_name.lower() in lower:
            score += 0.35
        if stem and stem in lower:
            score += 0.35
        exact_overlap = len(query_words & spec_words)
        score += exact_overlap * 0.12
        compact_spec = "".join(re.findall(r"[a-z0-9]+", lower))
        if compact_spec and compact_spec in collapsed_query:
            score += 0.9
        for special in ("adultsignature", "dangerousgoods", "insurance", "pickupdetails"):
            if special in compact_spec and special in collapsed_query:
                score += 1.2
        if "specialservices" in lower and any(word in spec_words for word in ("adultsignature", "dangerousgoods", "insurance")):
            score += 0.15
        return score

    best = max(candidates, key=_spec_score, default="")
    return best if _spec_score(best) > 0 else ""


def find_pom(card_name: str, acceptance_criteria: str = "", repo_path: str = "") -> dict | None:
    """Best-effort match from card text to an existing automation POM/spec pair."""
    repo_root_str = _get_automation_repo_path(repo_path)
    if not repo_root_str:
        return None
    repo_root = Path(repo_root_str)
    pages_root = repo_root / "support" / "pages"
    if not pages_root.exists():
        return None

    query = " ".join(part for part in [card_name.strip(), acceptance_criteria[:500].strip()] if part).strip()
    if not query:
        return None

    page_candidates = [
        path for path in pages_root.rglob("*.ts")
        if path.is_file() and path.name != "basePage.ts" and not path.name.startswith(".")
    ]
    if not page_candidates:
        return None

    scored: list[tuple[float, Path]] = []
    for path in page_candidates:
        rel = str(path.relative_to(repo_root))
        score = _score_candidate(query, rel)
        if score > 0:
            scored.append((score, path))

    if not scored:
        return None

    score, best_path = max(scored, key=lambda item: item[0])
    if score < 0.2:
        return None

    rel_path = str(best_path.relative_to(repo_root))
    spec_file = _find_related_spec(repo_root, rel_path, query)
    return {
        "file": rel_path,
        "spec_file": spec_file,
        "app_path": _infer_nav_hint_from_path(rel_path),
        "nav": _infer_nav_hint_from_path(rel_path),
        "score": round(score, 3),
    }


def _run_playwright_spec(repo_path: str, spec_path: str, project: str = "Google Chrome", timeout: int = 600) -> tuple[bool, str]:
    cmd = [
        "npx",
        "playwright",
        "test",
        spec_path,
        "--project",
        project,
        "--reporter=line",
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, output
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


FIX_PROMPT = """\
You are a senior Playwright TypeScript automation engineer.
A generated MCSL Playwright test is failing. Fix ONLY the spec and optionally the POM so the test can pass.

## Playwright Error Output
{error_output}

## Current Spec ({spec_path})
{spec_content}

## Current POM ({pom_path})
{pom_content}

Rules:
- Only return complete TypeScript files
- Do not invent new external helpers
- If selector/action is wrong, fix locator or method in the POM
- If assertion is weak/wrong, fix the spec
- Do not add test.only()

Output ONLY these blocks:

=== FIXED SPEC: {spec_path} ===
<full fixed spec>

If needed:
=== FIXED POM: {pom_path} ===
<full fixed pom>
"""


def _run_and_fix_loop(
    *,
    repo_path: str,
    spec_path: str,
    pom_path: str,
    claude: ChatAnthropic,
    max_iterations: int = 3,
    on_progress=None,
) -> dict:
    history: list[dict] = []
    final_output = ""

    for iteration in range(1, max_iterations + 1):
        passed, output = _run_playwright_spec(repo_path, spec_path)
        final_output = output
        history.append({
            "iteration": iteration,
            "passed": passed,
            "output": output[-4000:],
            "fixed_files": [],
        })
        if on_progress:
            on_progress(iteration, "tests passed" if passed else "tests failed", output[-2000:])
        if passed:
            return {
                "passed": True,
                "iterations": iteration,
                "history": history,
                "final_output": final_output,
            }
        if iteration == max_iterations:
            break

        spec_content = _read_repo_file(repo_path, spec_path)
        pom_content = _read_repo_file(repo_path, pom_path)
        resp = claude.invoke([HumanMessage(content=FIX_PROMPT.format(
            error_output=output[-4000:],
            spec_path=spec_path,
            spec_content=spec_content[:5000],
            pom_path=pom_path,
            pom_content=pom_content[:5000],
        ))])
        raw = resp.content if isinstance(resp.content, str) else str(resp.content)
        fixed_spec = _parse_block(raw, "FIXED SPEC")
        fixed_pom = _parse_block(raw, "FIXED POM")
        fixed_files: list[str] = []
        if fixed_spec and fixed_spec != spec_content:
            _write_repo_file(repo_path, spec_path, fixed_spec)
            fixed_files.append(spec_path)
        if fixed_pom and fixed_pom != pom_content:
            _write_repo_file(repo_path, pom_path, fixed_pom)
            fixed_files.append(pom_path)
        history[-1]["fixed_files"] = fixed_files

    return {
        "passed": False,
        "iterations": max_iterations,
        "history": history,
        "final_output": final_output,
    }


def _filter_automatable_cases(test_cases_markdown: str) -> tuple[str, dict[str, int]]:
    """Keep positive and edge cases; negative cases remain manual by default."""
    text = (test_cases_markdown or "").strip()
    empty = {
        "total": 0,
        "kept": 0,
        "positive": 0,
        "edge": 0,
        "negative": 0,
    }
    if not text:
        return "", empty

    blocks = re.split(r"(?=^###\s+TC-)", text, flags=re.MULTILINE)
    if len(blocks) <= 1:
        # Fallback: no explicit TC headings, keep the input
        counts = {**empty, "total": 1, "kept": 1, "positive": 1}
        return text, counts

    kept_blocks: list[str] = []
    counts = empty.copy()
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        counts["total"] += 1
        _type_match = re.search(r"^\*\*Type:\*\*\s*(.+)$", block, flags=re.MULTILINE)
        tc_type = (_type_match.group(1).strip().lower() if _type_match else "positive")
        if "negative" in tc_type:
            counts["negative"] += 1
            continue
        if "edge" in tc_type:
            counts["edge"] += 1
        else:
            counts["positive"] += 1
        counts["kept"] += 1
        kept_blocks.append(block)

    return "\n\n".join(kept_blocks).strip(), counts


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def write_automation(
    feature_name: str = "",
    test_cases_markdown: str = "",
    exploration_data: str = "",
    ai_qa_context: str = "",
    card_name: str = "",
    acceptance_criteria: str = "",
    branch_name: str = "",
    dry_run: bool = False,
    push: bool = False,
    chrome_trace_context: str = "",
    qa_context: str = "",
    auto_fix: bool = False,
    fix_iterations: int = 3,
    on_fix_progress=None,
    repo_path: str = "",
    model: str | None = None,
) -> AutomationResult:
    """
    Generate a TypeScript Playwright POM class and spec file from feature_name
    and test_cases_markdown using Claude.

    Returns AutomationResult.  Never raises — errors are captured in .error field.
    """
    resolved_name = (feature_name or card_name).strip()
    feature_snake = _to_snake_case(resolved_name)
    feature_camel = _to_camel_case(resolved_name)
    repo_root = _get_automation_repo_path(repo_path)
    matched_pom = find_pom(resolved_name, acceptance_criteria=acceptance_criteria, repo_path=repo_root)
    pom_path = matched_pom.get("file", "") if matched_pom else f"support/pages/{feature_snake}/{feature_camel}Page.ts"
    spec_path = matched_pom.get("spec_file", "") if matched_pom else ""
    if not spec_path:
        spec_path = f"tests/{feature_snake}/{feature_snake}.spec.ts"
    target_branch = branch_name.strip() or f"automation/{re.sub(r'[^a-z0-9]+', '-', resolved_name.lower()).strip('-')[:40]}"

    _empty = AutomationResult(
        kind=("existing_pom" if matched_pom else "new_pom"),
        feature_name=resolved_name,
        pom_path="",
        spec_path="",
        pom_code="",
        spec_code="",
        git_branch=("" if dry_run else target_branch),
        skipped=dry_run,
    )

    if not resolved_name:
        _empty.error = "feature_name or card_name is required"
        return _empty

    if not config.ANTHROPIC_API_KEY:
        _empty.error = "ANTHROPIC_API_KEY not set"
        return _empty

    try:
        filtered_cases, tc_counts = _filter_automatable_cases(test_cases_markdown)
        if not filtered_cases:
            _empty.error = (
                f"No automatable test cases found. "
                f"All {tc_counts['total']} cases were negative/manual only."
            )
            _empty.tc_filter_summary = tc_counts
            return _empty

        _context_parts = [
            exploration_data.strip(),
            chrome_trace_context.strip(),
        ]
        merged_exploration = "\n\n".join(part for part in _context_parts if part)
        merged_ai_qa_context = "\n\n".join(
            part for part in [
                ai_qa_context.strip(),
                qa_context.strip(),
                acceptance_criteria.strip(),
            ]
            if part
        )
        locator_context = build_locator_context(f"{resolved_name} {filtered_cases[:800]}")
        if matched_pom:
            existing_pom = _read_repo_file(repo_root, pom_path) if repo_root else ""
            existing_spec = _read_repo_file(repo_root, spec_path) if repo_root else ""
            prompt = EXISTING_POM_WRITER_PROMPT.format(
                feature_name=resolved_name,
                test_cases=filtered_cases,
                exploration_data=merged_exploration or "(none)",
                ai_qa_context=merged_ai_qa_context or "(none)",
                pom_context=(
                    "Existing MCSL automation matched this feature. Update the current POM/spec pair "
                    "instead of creating duplicate files."
                ),
                locator_context=locator_context or "(none)",
                pom_path=pom_path,
                spec_path=spec_path,
                existing_pom=existing_pom or "// No existing POM contents found.",
                existing_spec=existing_spec or "// No existing spec contents found.",
            )
        else:
            prompt = NEW_POM_WRITER_PROMPT.format(
                feature_name=resolved_name,
                feature_snake=feature_snake,
                feature_camel=feature_camel,
                ClassName=feature_camel,
                test_cases=filtered_cases,
                exploration_data=merged_exploration or "(none)",
                ai_qa_context=merged_ai_qa_context or "(none)",
                pom_context="Existing MCSL POMs extend BasePage; all MCSL locators use this.appFrame.",
                locator_context=locator_context or "(none)",
                pom_path=pom_path,
                spec_path=spec_path,
            )

        llm = ChatAnthropic(
            model=model or config.CLAUDE_SONNET_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            max_tokens=4096,
        )
        response = llm.invoke([HumanMessage(content=[{"type": "text", "text": prompt}])])
        _raw = response.content
        if not isinstance(_raw, str):
            # langchain_anthropic may return a list of content blocks
            _raw = " ".join(
                block["text"] if isinstance(block, dict) else str(block)
                for block in _raw
                if not isinstance(block, dict) or block.get("type") == "text"
            )
        response_text: str = _raw

        pom_code, spec_code = _parse_automation_response(response_text)

        if not pom_code or not spec_code:
            _empty.error = "Failed to parse Claude response — check delimiter format"
            _empty.tc_filter_summary = tc_counts
            return _empty

        fix_passed = None
        fix_count = 0
        fix_history: list[dict] = []
        push_error = "" if not push else "Push is handled by the dashboard after files are written."

        if auto_fix and not dry_run:
            if not repo_path:
                push_error = "Auto-fix skipped: automation repo path is not configured."
            else:
                _write_repo_file(repo_path, pom_path, pom_code)
                _write_repo_file(repo_path, spec_path, spec_code)
                fix_result = _run_and_fix_loop(
                    repo_path=repo_path,
                    spec_path=spec_path,
                    pom_path=pom_path,
                    claude=llm,
                    max_iterations=fix_iterations,
                    on_progress=on_fix_progress,
                )
                fix_passed = fix_result.get("passed")
                fix_count = int(fix_result.get("iterations", 0) or 0)
                fix_history = fix_result.get("history", []) or []
                pom_code = _read_repo_file(repo_path, pom_path) or pom_code
                spec_code = _read_repo_file(repo_path, spec_path) or spec_code
                if fix_passed is False:
                    push_error = (
                        f"Push skipped — tests still failing after {fix_count} auto-fix attempt(s). "
                        "Fix locally and push manually."
                    )

        return AutomationResult(
            kind=("existing_pom" if matched_pom else "new_pom"),
            feature_name=resolved_name,
            pom_path=pom_path,
            spec_path=spec_path,
            pom_code=pom_code,
            spec_code=spec_code,
            files_written=([] if dry_run else [pom_path, spec_path]),
            git_branch=("" if dry_run else target_branch),
            git_pushed=False,
            push_error=push_error,
            skipped=dry_run,
            detection_reason=(
                f"Matched existing automation at `{pom_path}` and updated the current POM/spec pair"
                if matched_pom
                else "Generated new MCSL Playwright files from reviewed test cases and AI QA context"
            ),
            tc_filter_summary=tc_counts,
            fix_passed=fix_passed,
            fix_iterations=fix_count,
            fix_history=fix_history,
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("write_automation failed for feature '%s'", resolved_name)
        _empty.error = str(exc)
        return _empty


def push_to_branch(
    repo_path: str,
    feature_name: str,
    files: list[str],
    branch_name: str = "",
) -> tuple[bool, str]:
    """Stage generated files and push to a feature branch.

    Branch: automation/{feature_snake} (special chars -> hyphens, lowercased)
    Uses cwd=repo_path on all subprocess calls — never os.chdir().
    Returns (True, branch_name) on success, (False, error_message) on failure.
    """
    import subprocess

    branch = branch_name.strip() or ("automation/" + re.sub(r"[^a-z0-9]+", "-", feature_name.lower()).strip("-"))
    try:
        subprocess.run(
            ["git", "checkout", "-B", branch],
            cwd=repo_path, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "add"] + files,
            cwd=repo_path, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"feat(automation): add {feature_name} POM + spec"],
            cwd=repo_path, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            cwd=repo_path, check=True, capture_output=True, text=True,
        )
        return True, branch
    except subprocess.CalledProcessError as exc:
        return False, exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or str(exc))
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
