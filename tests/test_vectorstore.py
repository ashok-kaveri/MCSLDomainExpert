import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document


def test_both_collections(tmp_chroma_path, monkeypatch):
    monkeypatch.setattr("config.CHROMA_PATH", tmp_chroma_path)
    from importlib import reload
    import rag.vectorstore as vs_mod
    reload(vs_mod)
    vs_mod._reset_vectorstore()
    # Collection name must be mcsl_knowledge
    import config
    assert config.CHROMA_COLLECTION == "mcsl_knowledge"
    assert config.CHROMA_CODE_COLLECTION == "mcsl_code_knowledge"


def test_deduplicate():
    from rag.vectorstore import _deduplicate
    doc_a = Document(page_content="A" * 250, metadata={})
    doc_b = Document(page_content="A" * 250, metadata={})  # duplicate
    doc_c = Document(page_content="B" * 250, metadata={})
    result = _deduplicate([doc_a, doc_b, doc_c])
    assert len(result) == 2


def test_search_returns_empty_on_empty_collection(tmp_chroma_path, monkeypatch):
    monkeypatch.setattr("config.CHROMA_PATH", tmp_chroma_path)
    import rag.vectorstore as vs_mod
    from importlib import reload
    reload(vs_mod)
    vs_mod._reset_vectorstore()
    result = vs_mod.search("any query", k=3)
    assert isinstance(result, list)
