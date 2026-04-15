import pytest
from pathlib import Path


def test_skip_dirs(tmp_path):
    # Create a node_modules dir with a .js file inside — should be excluded
    node_mod = tmp_path / "node_modules"
    node_mod.mkdir()
    (node_mod / "some_lib.js").write_text("module.exports = {};")
    # Create a real .js file at root level
    (tmp_path / "carrier.js").write_text("const CARRIER = 'FedEx';")
    from rag.code_indexer import _walk_code_files
    files = _walk_code_files(tmp_path, [".js"])
    paths = [str(f) for f in files]
    assert not any("node_modules" in p for p in paths)
    assert any("carrier.js" in p for p in paths)


def test_index_nonexistent_path():
    from rag.code_indexer import index_codebase
    result = index_codebase("/nonexistent/path", "storepepsaas", extensions=[".js"])
    assert result["files_indexed"] == 0
    assert result["error"] != ""


def test_search_returns_empty_on_empty_collection(tmp_chroma_path, monkeypatch):
    monkeypatch.setattr("config.CHROMA_PATH", tmp_chroma_path)
    import rag.code_indexer as ci
    from importlib import reload
    reload(ci)
    ci._reset_code_vectorstore()
    result = ci.search_code("carrier adaptor config")
    assert isinstance(result, list)


def test_storepepsaas():
    pytest.skip("Integration: requires storepepSAAS path — run manually")


def test_automation():
    pytest.skip("Integration: requires mcsl-test-automation path — run manually")
