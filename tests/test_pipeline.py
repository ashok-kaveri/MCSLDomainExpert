"""
tests/test_pipeline.py — Unit tests for pipeline/user_story_writer.py, pipeline/trello_client.py
Phase 06 Plan 01 — TDD RED phase
"""
from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch, call

import pytest


# ---------------------------------------------------------------------------
# US-01: generate_user_story
# ---------------------------------------------------------------------------

def test_us01_generate_returns_markdown():
    """generate_user_story() returns non-empty string with User Story or Acceptance Criteria."""
    fake_response = MagicMock()
    fake_response.content = "### User Story\nAs a merchant...\n### Acceptance Criteria\n- AC1: signature"

    with patch("pipeline.user_story_writer._get_claude") as mock_get_claude, \
         patch("rag.vectorstore.search", return_value=[]), \
         patch("rag.code_indexer.search_code", return_value=[]):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = fake_response
        mock_get_claude.return_value = mock_llm

        from pipeline.user_story_writer import generate_user_story
        result = generate_user_story("Add FedEx signature option")

    assert isinstance(result, str)
    assert len(result) > 0
    assert "User Story" in result or "Acceptance Criteria" in result


def test_us01_generate_no_rag():
    """generate_user_story() handles RAG exceptions gracefully — no crash."""
    fake_response = MagicMock()
    fake_response.content = "### User Story\nAs a merchant, I want FedEx signature so that deliveries are confirmed."

    with patch("pipeline.user_story_writer._get_claude") as mock_get_claude, \
         patch("rag.vectorstore.search", side_effect=Exception("Collection empty")), \
         patch("rag.code_indexer.search_code", side_effect=Exception("Collection empty")):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = fake_response
        mock_get_claude.return_value = mock_llm

        from pipeline.user_story_writer import generate_user_story
        result = generate_user_story("some feature")

    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# US-02: refine_user_story
# ---------------------------------------------------------------------------

def test_us02_refine_returns_updated():
    """refine_user_story() returns non-empty updated markdown."""
    fake_response = MagicMock()
    fake_response.content = "### User Story\nUpdated story with concise ACs."

    with patch("pipeline.user_story_writer._get_claude") as mock_get_claude:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = fake_response
        mock_get_claude.return_value = mock_llm

        from pipeline.user_story_writer import refine_user_story
        result = refine_user_story("### User Story\nOriginal", "Make it more concise")

    assert isinstance(result, str)
    assert len(result) > 0


def test_us02_refine_prompt_contains_both():
    """refine_user_story() passes both previous_us and change_request into the LLM prompt."""
    captured_messages = []

    fake_response = MagicMock()
    fake_response.content = "### User Story\nRefined output."

    def fake_invoke(messages):
        captured_messages.extend(messages)
        return fake_response

    with patch("pipeline.user_story_writer._get_claude") as mock_get_claude:
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = fake_invoke
        mock_get_claude.return_value = mock_llm

        from pipeline.user_story_writer import refine_user_story
        refine_user_story("PREVIOUS_CONTENT", "CHANGE_REQUEST_TEXT")

    # The prompt content should include both strings
    all_content = " ".join(str(m) for m in captured_messages)
    assert "PREVIOUS_CONTENT" in all_content
    assert "CHANGE_REQUEST_TEXT" in all_content


# ---------------------------------------------------------------------------
# US-03: TrelloClient — create card and missing credentials
# ---------------------------------------------------------------------------

def test_us03_trello_card_created():
    """create_card_in_list() returns TrelloCard with id from API response."""
    fake_json = {"id": "card123", "name": "My Feature", "desc": "AC here",
                 "url": "https://trello.com/c/card123", "idList": "list1", "idMembers": []}
    mock_response = MagicMock()
    mock_response.json.return_value = fake_json
    mock_response.raise_for_status = MagicMock()

    with patch("requests.post", return_value=mock_response):
        from pipeline.trello_client import TrelloClient
        client = TrelloClient(api_key="k", token="t", board_id="b")
        card = client.create_card_in_list(list_id="list1", name="My Feature", desc="AC here")

    assert card.id == "card123"


def test_us03_trello_missing_creds():
    """TrelloClient() raises ValueError when Trello env vars are missing."""
    env_backup = {}
    for key in ("TRELLO_API_KEY", "TRELLO_TOKEN", "TRELLO_BOARD_ID"):
        env_backup[key] = os.environ.pop(key, None)

    try:
        from pipeline.trello_client import TrelloClient
        with pytest.raises(ValueError):
            TrelloClient()
    finally:
        for key, val in env_backup.items():
            if val is not None:
                os.environ[key] = val


# ---------------------------------------------------------------------------
# MC-01: move_card_to_list_by_id and add_comment
# ---------------------------------------------------------------------------

def test_mc01_move_card_by_id():
    """move_card_to_list_by_id() calls PUT /cards/{card_id} with idList=list_id."""
    fake_json = {"id": "card123"}
    mock_response = MagicMock()
    mock_response.json.return_value = fake_json
    mock_response.raise_for_status = MagicMock()
    mock_response.status_code = 200

    with patch("requests.put", return_value=mock_response) as mock_put:
        from pipeline.trello_client import TrelloClient
        client = TrelloClient(api_key="k", token="t", board_id="b")
        client.move_card_to_list_by_id("card123", "list456")

    mock_put.assert_called_once()
    call_args = mock_put.call_args
    url = call_args[0][0]
    assert "card123" in url

    # idList must be in the json body
    json_body = call_args.kwargs.get("json") or (call_args[1].get("json") if len(call_args) > 1 else None)
    assert json_body is not None, "Expected json keyword arg in requests.put call"
    assert json_body.get("idList") == "list456"


def test_mc01_audit_comment():
    """add_comment() calls POST to cards/{card_id}/actions/comments."""
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = MagicMock()

    with patch("requests.post", return_value=mock_response) as mock_post:
        from pipeline.trello_client import TrelloClient
        client = TrelloClient(api_key="k", token="t", board_id="b")
        client.add_comment("card123", "Moved by MCSL QA Pipeline")

    mock_post.assert_called_once()
    call_url = mock_post.call_args[0][0]
    assert "card123" in call_url
    assert "actions/comments" in call_url


# ---------------------------------------------------------------------------
# HIST-01: history persistence (skips gracefully if 06-03 not yet done)
# ---------------------------------------------------------------------------

def test_hist01_save_history(tmp_path):
    """_save_history() writes valid JSON; _load_history() reads it back."""
    pd = pytest.importorskip("pipeline_dashboard")
    if not hasattr(pd, "_save_history"):
        pytest.skip("_save_history not yet implemented (06-03)")

    hist_file = tmp_path / "pipeline_history.json"
    data = {"card1": {"card_name": "X", "approved_at": "2026-01-01"}}

    with patch.object(pd, "_HISTORY_FILE", hist_file):
        pd._save_history(data)
        assert hist_file.exists()
        assert json.loads(hist_file.read_text()) == data


def test_hist01_load_empty(tmp_path):
    """_load_history() returns {} when file does not exist."""
    pd = pytest.importorskip("pipeline_dashboard")
    if not hasattr(pd, "_load_history"):
        pytest.skip("_load_history not yet implemented (06-03)")

    nonexistent = tmp_path / "no_file.json"
    with patch.object(pd, "_HISTORY_FILE", nonexistent):
        result = pd._load_history()
    assert result == {}


def test_hist01_entry_schema(tmp_path):
    """History entries must contain card_name, approved_at, card_url keys."""
    pd = pytest.importorskip("pipeline_dashboard")
    if not hasattr(pd, "_save_history") or not hasattr(pd, "_load_history"):
        pytest.skip("_save_history/_load_history not yet implemented (06-03)")

    entry = {"card_name": "X", "approved_at": "2026-01-01", "card_url": "https://trello.com/c/xyz"}
    hist_file = tmp_path / "pipeline_history.json"

    with patch.object(pd, "_HISTORY_FILE", hist_file):
        pd._save_history({"card1": entry})
        loaded = pd._load_history()

    assert "card_name" in loaded["card1"]
    assert "approved_at" in loaded["card1"]
    assert "card_url" in loaded["card1"]
