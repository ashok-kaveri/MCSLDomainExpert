"""Serve env *sample/template* files from the automation repo to Slack — safely.

Hard safety rule: only files that are BOTH git-tracked AND named like a sample
(.env_sample / .env.example / *.template …) are ever returned. Real env files
(`.env`, `carrier-envs/*.env`) are untracked and contain live credentials, so
they can never match and are never sent.
"""
from __future__ import annotations

import logging
import re
import subprocess

import config  # noqa: F401 — loads .env (MCSL_AUTOMATION_REPO_PATH)

logger = logging.getLogger(__name__)

# Asks like: "env sample", "get the env sample file", "share env template/example".
_REQUEST_RE = re.compile(
    r"\benv(?:ironment)?\b.*\b(?:sample|example|template)\b"
    r"|\b(?:sample|example|template)\b.*\benv(?:ironment)?\b",
    re.IGNORECASE,
)

# A file is a shareable sample only if its name matches this (basename or path).
_SAMPLE_NAME_RE = re.compile(
    r"(?:^|/)\.?env[._-]?(?:sample|example|template)s?$"
    r"|\.env\.(?:sample|example|template)$",
    re.IGNORECASE,
)

MAX_BYTES = 64 * 1024


def parse_env_sample_request(text: str) -> bool:
    return bool(text and _REQUEST_RE.search(text))


def _git_tracked(repo_path: str) -> set[str]:
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=repo_path, capture_output=True, text=True, timeout=20
        )
        return set(line.strip() for line in out.stdout.splitlines() if line.strip())
    except Exception as exc:  # noqa: BLE001
        logger.warning("git ls-files failed: %s", exc)
        return set()


def get_env_samples(repo_path: str | None = None) -> list[tuple[str, str]]:
    """Return [(relpath, content), ...] for git-tracked sample/template env files only."""
    from pathlib import Path
    repo_path = repo_path or config.MCSL_AUTOMATION_REPO_PATH
    tracked = _git_tracked(repo_path)

    samples: list[tuple[str, str]] = []
    for rel in sorted(tracked):
        if rel.startswith(".git/"):
            continue
        if not _SAMPLE_NAME_RE.search(rel):
            continue
        # Belt-and-suspenders: never serve a path that looks like a real env file.
        base = rel.rsplit("/", 1)[-1].lower()
        if base in (".env",) or rel.startswith("carrier-envs/"):
            continue
        try:
            content = (Path(repo_path) / rel).read_text(encoding="utf-8", errors="replace")[:MAX_BYTES]
        except OSError as exc:
            logger.warning("could not read %s: %s", rel, exc)
            continue
        samples.append((rel, content))
    return samples
