#!/usr/bin/env python3
"""Safe RAG sync helper for MCSLDomainExpert."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: E402


def _run_git(args: list[str], cwd: str) -> str:
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_SSH_COMMAND": "ssh -o BatchMode=yes -o StrictHostKeyChecking=no",
    }
    res = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    if res.returncode != 0:
        raise RuntimeError((res.stderr or res.stdout or "").strip())
    return res.stdout.strip()


def _is_git_repo(path: str) -> bool:
    try:
        _run_git(["rev-parse", "--is-inside-work-tree"], path)
        return True
    except Exception:
        return False


def _dirty(path: str) -> str:
    if not _is_git_repo(path):
        return ""
    return _run_git(["status", "--porcelain"], path)


def _repo_status(path: str) -> dict[str, Any]:
    if not path:
        return {"path": path, "exists": False, "error": "path not configured"}
    p = Path(path)
    payload: dict[str, Any] = {"path": path, "exists": p.exists(), "is_git": False}
    if not p.exists():
        return payload
    if _is_git_repo(path):
        payload["is_git"] = True
        payload["branch"] = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], path)
        payload["commit"] = _run_git(["rev-parse", "--short", "HEAD"], path)
        payload["dirty"] = bool(_dirty(path))
        try:
            branches = _run_git(["branch", "--format=%(refname:short)"], path)
            payload["branches"] = [b.strip() for b in branches.splitlines() if b.strip()]
        except Exception:
            payload["branches"] = []
    return payload


def _path_for_target(target: str, explicit_path: str = "") -> str:
    if explicit_path:
        return explicit_path
    if target == "automation":
        return config.MCSL_AUTOMATION_REPO_PATH
    if target in ("backend", "storepepsaas_server"):
        return config.STOREPEPSAAS_SERVER_PATH
    if target in ("frontend", "storepepsaas_client"):
        return config.STOREPEPSAAS_CLIENT_PATH
    if target == "wiki":
        return config.WIKI_PATH
    raise ValueError(f"No path mapping for target: {target}")


def _code_extensions(target: str) -> list[str] | None:
    if target == "automation":
        return [".ts", ".tsx", ".js"]
    return None


def _source_type_for_target(target: str) -> str:
    if target == "backend":
        return "storepepsaas_server"
    if target == "frontend":
        return "storepepsaas_client"
    return target


def _sync_code(target: str, path: str, branch: str) -> dict[str, Any]:
    from rag.code_indexer import sync_from_git

    if _dirty(path):
        return {"target": target, "path": path, "branch": branch, "error": "Repo has uncommitted changes; ask QA before pulling."}
    result = sync_from_git(
        path,
        source_type=target,
        branch=branch,
        extensions=_code_extensions(target),
    )
    result.update({"target": target, "path": path, "branch": branch})
    return result


def _full_reindex_code(target: str, path: str, branch: str | None) -> dict[str, Any]:
    from rag.code_indexer import index_codebase

    if branch:
        if _dirty(path):
            return {"target": target, "path": path, "branch": branch, "error": "Repo has uncommitted changes; ask QA before checkout/pull."}
        _run_git(["checkout", branch], path)
        _run_git(["pull", "origin", branch], path)
    result = index_codebase(
        path,
        source_type=target,
        clear_existing=True,
        extensions=_code_extensions(target),
    )
    result.update({"target": target, "path": path, "branch": branch or "(current)", "full_reindex": True})
    return result


def _sync_wiki(path: str, branch: str | None, pull: bool) -> dict[str, Any]:
    from ingest.wiki_loader import load_wiki_docs
    from rag.vectorstore import add_documents, delete_by_source_type

    if not path:
        return {"target": "wiki", "error": "WIKI_PATH is not configured"}
    if pull and _is_git_repo(path):
        if _dirty(path):
            return {"target": "wiki", "path": path, "error": "Wiki repo has uncommitted changes; ask QA before pulling."}
        if branch:
            _run_git(["checkout", branch], path)
            pull_msg = _run_git(["pull", "origin", branch], path)
        else:
            pull_msg = _run_git(["pull"], path)
    else:
        pull_msg = "pull skipped"

    old_path = config.WIKI_PATH
    config.WIKI_PATH = path
    try:
        deleted = delete_by_source_type("wiki")
        docs = load_wiki_docs()
        if docs:
            add_documents(docs)
    finally:
        config.WIKI_PATH = old_path

    return {
        "target": "wiki",
        "path": path,
        "branch": branch or "(current)",
        "pull": pull_msg,
        "deleted_chunks": deleted,
        "chunks_indexed": len(docs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync MCSL RAG knowledge safely.")
    sub = parser.add_subparsers(dest="command", required=True)
    targets = ["automation", "storepepsaas_server", "storepepsaas_client", "backend", "frontend", "wiki"]

    status_p = sub.add_parser("status")
    status_p.add_argument("--target", choices=[*targets, "all"], default="all")
    status_p.add_argument("--path", default="")

    sync_p = sub.add_parser("sync")
    sync_p.add_argument("--target", choices=targets, required=True)
    sync_p.add_argument("--branch", default="")
    sync_p.add_argument("--path", default="")
    sync_p.add_argument("--pull", action="store_true", help="For wiki, pull git before source-only reindex.")
    sync_p.add_argument("--allow-current-automation", action="store_true", help="Use current automation branch when --branch is omitted.")

    reindex_p = sub.add_parser("full-reindex")
    reindex_p.add_argument("--target", choices=targets, required=True)
    reindex_p.add_argument("--branch", default="")
    reindex_p.add_argument("--path", default="")
    reindex_p.add_argument("--pull", action="store_true")
    reindex_p.add_argument("--allow-current-automation", action="store_true")

    args = parser.parse_args()

    if args.command == "status":
        status_targets = ["automation", "storepepsaas_server", "storepepsaas_client", "wiki"] if args.target == "all" else [args.target]
        payload = {target: _repo_status(_path_for_target(target, args.path if len(status_targets) == 1 else "")) for target in status_targets}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    target = args.target
    path = _path_for_target(target, args.path)

    if target == "automation":
        if args.branch:
            branch = args.branch
        elif args.allow_current_automation:
            branch = ""
        else:
            status = _repo_status(path)
            print(json.dumps({
                "target": "automation",
                "path": path,
                "needs_qa": "Which automation branch should I sync?",
                "current_branch": status.get("branch", ""),
                "branches": status.get("branches", []),
            }, indent=2, ensure_ascii=False))
            return 2
    else:
        branch = args.branch or ""

    if args.command == "sync":
        if target in ("backend", "frontend", "storepepsaas_server", "storepepsaas_client", "automation"):
            payload = _sync_code(_source_type_for_target(target), path, branch)
            payload["target"] = target
        elif target == "wiki":
            payload = _sync_wiki(path, branch, pull=True)
    else:
        if target in ("backend", "frontend", "storepepsaas_server", "storepepsaas_client", "automation"):
            payload = _full_reindex_code(_source_type_for_target(target), path, branch or None)
            payload["target"] = target
        elif target == "wiki":
            payload = _sync_wiki(path, branch, pull=args.pull)
            payload["full_reindex"] = True

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not payload.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
