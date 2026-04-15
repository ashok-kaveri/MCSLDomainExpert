import pytest


def test_missing_kb_dir_returns_empty(monkeypatch, tmp_path):
    """load_kb_articles() returns [] (not exception) when docs/kb_snapshots/ is missing."""
    monkeypatch.setattr("config.BASE_DIR", tmp_path)
    from importlib import reload
    import ingest.kb_loader as kb
    reload(kb)
    result = kb.load_kb_articles()
    assert result == []


def test_source_type_metadata(monkeypatch, tmp_path):
    """All returned documents have source_type='kb_articles'."""
    kb_dir = tmp_path / "docs" / "kb_snapshots"
    kb_dir.mkdir(parents=True)
    (kb_dir / "setup.md").write_text("# Setup\n" + "content " * 30)
    monkeypatch.setattr("config.BASE_DIR", tmp_path)
    from importlib import reload
    import ingest.kb_loader as kb
    reload(kb)
    docs = kb.load_kb_articles()
    assert len(docs) > 0
    assert all(d.metadata["source_type"] == "kb_articles" for d in docs)


def test_load_returns_documents(monkeypatch, tmp_path):
    """load_kb_articles() returns Documents when .md files exist."""
    kb_dir = tmp_path / "docs" / "kb_snapshots"
    kb_dir.mkdir(parents=True)
    (kb_dir / "test-article.md").write_text("# Test\n" + "MCSL content " * 20)
    monkeypatch.setattr("config.BASE_DIR", tmp_path)
    from importlib import reload
    import ingest.kb_loader as kb
    reload(kb)
    docs = kb.load_kb_articles()
    assert len(docs) > 0
    from langchain_core.documents import Document
    assert all(isinstance(d, Document) for d in docs)


def test_short_files_skipped(monkeypatch, tmp_path):
    """Files with fewer than 50 chars are skipped."""
    kb_dir = tmp_path / "docs" / "kb_snapshots"
    kb_dir.mkdir(parents=True)
    (kb_dir / "tiny.md").write_text("short")
    (kb_dir / "normal.md").write_text("# Normal\n" + "content " * 30)
    monkeypatch.setattr("config.BASE_DIR", tmp_path)
    from importlib import reload
    import ingest.kb_loader as kb
    reload(kb)
    docs = kb.load_kb_articles()
    sources = [d.metadata["source"] for d in docs]
    assert not any("tiny.md" in s for s in sources)
    assert any("normal.md" in s for s in sources)


def test_chunk_size_within_limit(monkeypatch, tmp_path):
    """Chunk content length does not exceed CHUNK_SIZE significantly."""
    kb_dir = tmp_path / "docs" / "kb_snapshots"
    kb_dir.mkdir(parents=True)
    (kb_dir / "big.md").write_text("# Big\n" + "content word " * 500)
    monkeypatch.setattr("config.BASE_DIR", tmp_path)
    from importlib import reload
    import ingest.kb_loader as kb
    reload(kb)
    docs = kb.load_kb_articles()
    import config as cfg
    assert all(len(d.page_content) <= cfg.CHUNK_SIZE * 2 for d in docs)
