"""Trigger targeted Playwright test runs from the Slack bot.

Matches a keyword to spec files in the automation repo, runs just those via
``pipeline.test_runner.run_release_tests`` (``npx playwright test``), and returns
a typed result the bot formats into a Slack message.

Targeted-only by design: a keyword must match a bounded set of specs. A keyword
that matches too many specs is refused (so nobody kicks off the whole suite by
accident).
"""
from __future__ import annotations

import logging
import re

import config  # noqa: F401 — loads .env (MCSL_AUTOMATION_REPO_PATH etc.)
from pipeline.test_runner import enumerate_specs, run_release_tests

logger = logging.getLogger(__name__)

# Cap to keep "targeted" actually targeted; broad keywords are refused.
MAX_SPECS = 15

# Playwright tags used in the repo (run via --grep @tag). Extend as the suite grows.
KNOWN_TAGS = {"smoke", "sanity", "regression", "onboarding", "packaging", "critical"}

_RUN_RE = re.compile(r"\b(?:run|trigger|execute|kick\s*off)\b", re.IGNORECASE)
_TEST_RE = re.compile(r"\b(?:tests?|specs?|automation|playwright)\b", re.IGNORECASE)
_STOPWORDS = {
    "run", "trigger", "execute", "kick", "off", "the", "tests", "test", "specs",
    "spec", "for", "please", "automation", "playwright", "mcslexpert", "mcslbot",
    "on", "in", "a", "of", "all", "case", "cases",
}


def parse_run_tests_request(text: str) -> dict | None:
    """Return {"keyword": "<target>"} if `text` asks to run tests, else None.

    Triggered by a run verb plus either a test/spec word OR a known tag
    (so "run regression" and "run smoke" work without the word "tests").
    """
    if not text:
        return None
    cleaned = re.sub(r"<@[A-Z0-9]+>", " ", text)
    if not _RUN_RE.search(cleaned):
        return None
    has_test_word = _TEST_RE.search(cleaned)
    has_tag = any(re.search(rf"\b{t}\b", cleaned, re.IGNORECASE) for t in KNOWN_TAGS)
    if not (has_test_word or has_tag):
        return None
    words = re.findall(r"[A-Za-z0-9_./-]+", cleaned)
    keyword = " ".join(w for w in words if w.lower() not in _STOPWORDS).strip()
    return {"keyword": keyword}


def detect_tag(keyword: str) -> str | None:
    """If the keyword names a Playwright tag, return the grep value '@tag', else None.

    Recognizes any explicit '@x', plus the known bare tag words (smoke, sanity, …).
    """
    for raw in re.findall(r"@?[A-Za-z0-9_]+", keyword or ""):
        word = raw.lstrip("@").lower()
        if raw.startswith("@") and word:
            return f"@{word}"
        if word in KNOWN_TAGS:
            return f"@{word}"
    return None


def run_by_tag(tag: str, repo_path: str | None = None, project: str = "Google Chrome"):
    """Run every test carrying `tag` (e.g. '@smoke') across the suite via --grep."""
    repo_path = repo_path or config.MCSL_AUTOMATION_REPO_PATH
    logger.info("Running tests by tag %r", tag)
    # Tag runs can span the whole suite → allow more time than a targeted spec run.
    return run_release_tests(repo_path, [], project=project, grep=tag, timeout=1800)


def find_specs(keyword: str, repo_path: str | None = None) -> tuple[str, list[str], list[str]]:
    """Return (repo_path, matched_spec_paths, all_folders).

    Matches `keyword` (spaces/case/slashes ignored) against folder names and spec
    paths. Empty keyword matches nothing.
    """
    repo_path = repo_path or config.MCSL_AUTOMATION_REPO_PATH
    grouped = enumerate_specs(repo_path)
    folders = list(grouped.keys())

    kw = re.sub(r"[\s/_-]+", "", keyword.lower())
    if not kw:
        return repo_path, [], folders

    matched: list[str] = []
    for folder, specs in grouped.items():
        folder_norm = re.sub(r"[\s/_-]+", "", folder.lower())
        for rel in specs:
            path_norm = re.sub(r"[\s/_-]+", "", rel.lower())
            if kw in folder_norm or kw in path_norm:
                matched.append(rel)
    return repo_path, sorted(set(matched)), folders


def run_specs(repo_path: str, spec_paths: list[str], project: str = "Google Chrome"):
    """Run the given spec files and return a TestRunResult (never raises)."""
    logger.info("Running %d spec(s) via playwright project %r", len(spec_paths), project)
    return run_release_tests(repo_path, spec_paths, project=project)
