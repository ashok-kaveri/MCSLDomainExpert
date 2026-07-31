"""Targeted re-index of server/client files changed in 36f42b56e..HEAD.

The standard sync_from_git path-matched against the indexed subdir root while
git diff returns repo-root-relative paths, so the 30 in-scope changed files were
skipped (0 chunks). This re-indexes exactly those files via the same internal
_index_single_file (which replaces old chunks per file -> idempotent).
"""
import subprocess
from pathlib import Path

import config
from rag.code_indexer import _get_code_vectorstore, _index_single_file

SINCE = "36f42b56e"
SERVER_ROOT = Path(config.STOREPEPSAAS_SERVER_PATH).resolve()
CLIENT_ROOT = Path(config.STOREPEPSAAS_CLIENT_PATH).resolve()
EXTS = tuple(config.CODE_FILE_EXTENSIONS)

git_root = subprocess.run(
    ["git", "-C", str(SERVER_ROOT), "rev-parse", "--show-toplevel"],
    capture_output=True, text=True, check=True,
).stdout.strip()
git_root = Path(git_root)

diff = subprocess.run(
    ["git", "-C", str(SERVER_ROOT), "diff", "--name-status", f"{SINCE}..HEAD"],
    capture_output=True, text=True, check=True,
).stdout.splitlines()

vs = _get_code_vectorstore()
totals = {"storepepsaas_server": 0, "storepepsaas_client": 0}
counts = {"storepepsaas_server": 0, "storepepsaas_client": 0}
skipped = []

for line in diff:
    if not line.strip():
        continue
    status, _, rel = line.partition("\t")
    rel = rel.strip()
    if status.strip().startswith("D"):
        continue  # none in this range
    if not rel.endswith(EXTS):
        continue
    abspath = (git_root / rel).resolve()
    if not abspath.exists():
        skipped.append((rel, "missing"))
        continue
    if str(abspath).startswith(str(SERVER_ROOT) + "/"):
        root, st = SERVER_ROOT, "storepepsaas_server"
    elif str(abspath).startswith(str(CLIENT_ROOT) + "/"):
        root, st = CLIENT_ROOT, "storepepsaas_client"
    else:
        skipped.append((rel, "out-of-scope"))
        continue
    n = _index_single_file(abspath, root, st, vs)
    totals[st] += n
    counts[st] += 1
    print(f"  [{st}] {abspath.relative_to(root)} -> {n} chunks")

print("\n=== summary ===")
for st in totals:
    print(f"{st}: {counts[st]} files re-indexed, {totals[st]} chunks")
print(f"skipped (non-code / out-of-scope): {len(skipped)}")
for rel, why in skipped:
    print(f"  - {why}: {rel}")
