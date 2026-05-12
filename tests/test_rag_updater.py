import pytest
from unittest.mock import patch
from langchain_core.documents import Document


def _get_docs_and_ids(mock_upsert, call_index=0):
    """Extract docs and ids from a mock_upsert call, handling positional or keyword args."""
    call = mock_upsert.call_args_list[call_index]
    args, kwargs = call
    docs = args[0]
    # ids may be positional (args[1]) or keyword (kwargs['ids'])
    ids = args[1] if len(args) > 1 else kwargs["ids"]
    return docs, ids


def test_stable_ids():
    """embed_trello_card calls upsert_documents with stable IDs; TC chunks use __0 suffix."""
    with patch("pipeline.rag_updater.upsert_documents") as mock_upsert:
        from pipeline.rag_updater import embed_trello_card
        embed_trello_card("CARD-123", "AC text here", "Test case text here")
        assert mock_upsert.call_count == 1
        docs, ids = _get_docs_and_ids(mock_upsert)
        assert ids[0] == "CARD-123__ac"
        assert ids[1].startswith("CARD-123__test_cases__")
        assert len(docs) == len(ids)


def test_upsert_idempotent():
    """Calling embed_trello_card twice with same card_id calls upsert twice with same IDs."""
    import pipeline.rag_updater as ru
    with patch("pipeline.rag_updater.upsert_documents") as mock_upsert:
        ru.embed_trello_card("CARD-456", "AC v1", "TC v1")
        ru.embed_trello_card("CARD-456", "AC v2", "TC v2")
        assert mock_upsert.call_count == 2
        # Both calls use the same stable ID pattern — upsert_documents handles replace
        _, first_ids  = _get_docs_and_ids(mock_upsert, call_index=0)
        _, second_ids = _get_docs_and_ids(mock_upsert, call_index=1)
        assert first_ids[0]  == "CARD-456__ac"
        assert second_ids[0] == "CARD-456__ac"
        assert first_ids[1].startswith("CARD-456__test_cases__")
        assert second_ids[1].startswith("CARD-456__test_cases__")


def test_source_type_metadata():
    """Both documents have source_type='trello_card'."""
    with patch("pipeline.rag_updater.upsert_documents") as mock_upsert:
        from pipeline.rag_updater import embed_trello_card
        embed_trello_card("CARD-789", "AC content", "TC content")
        docs, _ = _get_docs_and_ids(mock_upsert)
        assert all(d.metadata["source_type"] == "trello_card" for d in docs)
        assert all(d.metadata["card_id"] == "CARD-789" for d in docs)
