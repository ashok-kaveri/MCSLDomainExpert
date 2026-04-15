import pytest
import sys


def test_sources_argparse():
    """Verify argparse --help shows all 6 MCSL source names."""
    import subprocess
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = "/Users/madan/Documents/MCSLDomainExpert"
    result = subprocess.run(
        [sys.executable, "ingest/run_ingest.py", "--help"],
        cwd="/Users/madan/Documents/MCSLDomainExpert",
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "kb_articles" in result.stdout
    assert "sheets" in result.stdout
    assert "wiki" in result.stdout
    assert "storepepsaas_server" in result.stdout
    assert "storepepsaas_client" in result.stdout
    assert "automation" in result.stdout


def test_partial_reingest_deletes_before_add():
    """Verify partial re-ingest calls delete_by_source_type before add_documents."""
    from unittest.mock import patch, MagicMock
    with patch("rag.vectorstore.delete_by_source_type") as mock_del, \
         patch("rag.vectorstore.add_documents") as mock_add, \
         patch("ingest.kb_loader.load_kb_articles", return_value=[MagicMock()]) as mock_load:
        from importlib import reload
        import ingest.run_ingest as ri
        reload(ri)
        ri.run_ingest(sources=["kb_articles"])
        mock_del.assert_called_once_with("kb_articles")
        mock_add.assert_called_once()


def test_run_ingest_all_sources_when_none():
    """run_ingest(sources=None) runs all 6 sources."""
    from unittest.mock import patch, MagicMock, call
    with patch("rag.vectorstore.delete_by_source_type") as mock_del, \
         patch("rag.vectorstore.add_documents") as mock_add, \
         patch("ingest.kb_loader.load_kb_articles", return_value=[]) as mock_kb, \
         patch("ingest.sheets_loader.load_test_cases", return_value=[]) as mock_sh, \
         patch("ingest.wiki_loader.load_wiki_docs", return_value=[]) as mock_wiki, \
         patch("rag.code_indexer.index_codebase", return_value={"files_indexed": 0, "chunks_added": 0, "skipped": 0, "error": ""}) as mock_code:
        from importlib import reload
        import ingest.run_ingest as ri
        reload(ri)
        ri.run_ingest(sources=None)
        # All doc sources called
        mock_kb.assert_called_once()
        mock_sh.assert_called_once()
        mock_wiki.assert_called_once()
        # Code sources called (storepepsaas_server, storepepsaas_client, automation)
        assert mock_code.call_count == 3


def test_storepepsaas_server_source_type():
    """storepepsaas_server source calls index_codebase with correct source_type."""
    from unittest.mock import patch, MagicMock
    with patch("rag.code_indexer.index_codebase") as mock_code:
        mock_code.return_value = {"files_indexed": 0, "chunks_added": 0, "skipped": 0, "error": ""}
        from importlib import reload
        import ingest.run_ingest as ri
        reload(ri)
        ri.run_ingest(sources=["storepepsaas_server"])
        call_kwargs = mock_code.call_args
        assert call_kwargs[1].get("source_type") == "storepepsaas_server" or \
               (len(call_kwargs[0]) > 1 and call_kwargs[0][1] == "storepepsaas_server")


def test_automation_source_type():
    """automation source calls index_codebase with source_type='automation'."""
    from unittest.mock import patch
    with patch("rag.code_indexer.index_codebase") as mock_code:
        mock_code.return_value = {"files_indexed": 0, "chunks_added": 0, "skipped": 0, "error": ""}
        from importlib import reload
        import ingest.run_ingest as ri
        reload(ri)
        ri.run_ingest(sources=["automation"])
        call_kwargs = mock_code.call_args
        assert call_kwargs[1].get("source_type") == "automation" or \
               (len(call_kwargs[0]) > 1 and call_kwargs[0][1] == "automation")
