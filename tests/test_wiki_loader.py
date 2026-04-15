import pytest


def test_category_map_mcsl_folders(monkeypatch, tmp_path):
    """Architecture folder maps to 'Architecture & Tech Stack' (MCSL category, not FedEx)."""
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "architecture").mkdir(parents=True)
    (wiki_dir / "architecture" / "overview.md").write_text("# Architecture\n" + "content " * 30)
    monkeypatch.setattr("config.WIKI_PATH", str(wiki_dir))
    from importlib import reload
    import ingest.wiki_loader as wl
    reload(wl)
    docs = wl.load_wiki_docs()
    assert any(d.metadata.get("category") == "Architecture & Tech Stack" for d in docs)


def test_missing_path_returns_empty(monkeypatch, tmp_path):
    """load_wiki_docs() returns [] (not exception) when WIKI_PATH does not exist."""
    monkeypatch.setattr("config.WIKI_PATH", str(tmp_path / "nonexistent"))
    from importlib import reload
    import ingest.wiki_loader as wl
    reload(wl)
    result = wl.load_wiki_docs()
    assert result == []


def test_load_returns_documents(monkeypatch, tmp_path):
    """load_wiki_docs() returns Documents with source_type='wiki'."""
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "modules").mkdir(parents=True)
    (wiki_dir / "modules" / "shipping.md").write_text("# Shipping\n" + "content " * 30)
    monkeypatch.setattr("config.WIKI_PATH", str(wiki_dir))
    from importlib import reload
    import ingest.wiki_loader as wl
    reload(wl)
    docs = wl.load_wiki_docs()
    assert len(docs) > 0
    assert all(d.metadata["source_type"] == "wiki" for d in docs)


def test_short_files_skipped(monkeypatch, tmp_path):
    """Files with fewer than 50 chars are skipped."""
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "architecture").mkdir(parents=True)
    (wiki_dir / "architecture" / "tiny.md").write_text("hi")
    (wiki_dir / "architecture" / "real.md").write_text("# Real doc\n" + "content " * 30)
    monkeypatch.setattr("config.WIKI_PATH", str(wiki_dir))
    from importlib import reload
    import ingest.wiki_loader as wl
    reload(wl)
    docs = wl.load_wiki_docs()
    # tiny.md should not appear
    sources = [d.metadata.get("file_name", "") for d in docs]
    assert "tiny.md" not in sources
    assert "real.md" in sources


def test_mcsl_specific_categories(monkeypatch, tmp_path):
    """All MCSL category folders map correctly."""
    wiki_dir = tmp_path / "wiki"
    category_map = {
        "modules": "Modules & Features",
        "patterns": "Patterns & Conventions",
        "product": "Product Stories & Requirements",
        "zendesk": "Zendesk Support Summaries",
        "support": "Support & Pain Points",
        "operations": "Operations",
    }
    for folder in category_map:
        (wiki_dir / folder).mkdir(parents=True)
        (wiki_dir / folder / "doc.md").write_text(f"# {folder}\n" + "content " * 30)
    monkeypatch.setattr("config.WIKI_PATH", str(wiki_dir))
    from importlib import reload
    import ingest.wiki_loader as wl
    reload(wl)
    docs = wl.load_wiki_docs()
    found_categories = {d.metadata.get("category") for d in docs}
    for expected_cat in category_map.values():
        assert expected_cat in found_categories, f"Missing category: {expected_cat}"
