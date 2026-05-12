from __future__ import annotations

import subprocess
import sys
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_knowledge_maintainer_helper_imports_without_missing_feedback_module():
    result = subprocess.run(
        [
            sys.executable,
            "skills/mcsl-knowledge-maintainer/scripts/maintain_knowledge.py",
            "--help",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert "Update MCSL card-cycle knowledge" in result.stdout


def test_card_processor_uses_mcsl_code_source_types(monkeypatch):
    from pipeline import card_processor

    calls: list[str] = []

    def fake_stats():
        return {
            "total": 3,
            "automation": 1,
            "storepepsaas_server": 1,
            "storepepsaas_client": 1,
        }

    def fake_search_code(_query, k=4, source_type=None):
        calls.append(source_type)
        return []

    monkeypatch.setattr("rag.code_indexer.get_index_stats", fake_stats)
    monkeypatch.setattr("rag.code_indexer.search_code", fake_search_code)

    card_processor._build_code_context_section_cached.cache_clear()
    card_processor._build_code_context_section_cached("Carrier setting", "Generate rates")

    assert "automation" in calls
    assert "storepepsaas_server" in calls
    assert "storepepsaas_client" in calls
    assert "backend" not in calls
    assert "frontend" not in calls


def test_rag_sync_backend_alias_indexes_storepepsaas_server(monkeypatch):
    script = ROOT / "skills" / "mcsl-rag-sync" / "scripts" / "rag_sync.py"
    spec = importlib.util.spec_from_file_location("mcsl_rag_sync_script", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module._source_type_for_target("backend") == "storepepsaas_server"
    assert module._source_type_for_target("frontend") == "storepepsaas_client"
    assert module._source_type_for_target("automation") == "automation"
