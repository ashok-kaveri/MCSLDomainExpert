import json
from unittest.mock import patch


class _Resp:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload or {}
        self.status_code = status_code

    def json(self):
        return self._payload


def test_channel_upload_uses_external_upload_flow(monkeypatch):
    """files.upload is retired — the helper must use the reserve/put/complete flow."""
    from pipeline import slack_client

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    calls = []

    def fake_get(url, **kwargs):
        calls.append(("GET", url, kwargs))
        return _Resp({"ok": True, "upload_url": "https://files.slack.com/upload/x", "file_id": "F123"})

    def fake_post(url, **kwargs):
        calls.append(("POST", url, kwargs))
        if "files.slack.com" in url:
            return _Resp(status_code=200)
        return _Resp({"ok": True})

    with patch.object(slack_client.requests, "get", fake_get), \
         patch.object(slack_client.requests, "post", fake_post):
        result = slack_client.upload_file_to_slack_channel(
            channel_id="C123", filename="guide.pdf", file_bytes=b"%PDF-1.4 body",
            title="Support Guide", initial_comment="hello",
        )

    assert result == {"ok": True, "file_id": "F123", "error": ""}
    urls = [url for _, url, _ in calls]
    assert any("files.getUploadURLExternal" in u for u in urls)
    assert any("files.completeUploadExternal" in u for u in urls)
    assert not any("files.upload" in u for u in urls)

    complete = next(kw for _, url, kw in calls if "completeUploadExternal" in url)
    files_payload = json.loads(complete["data"]["files"])
    assert files_payload == [{"id": "F123", "title": "Support Guide"}]
    assert complete["data"]["channel_id"] == "C123"
    assert complete["data"]["initial_comment"] == "hello"


def test_channel_upload_surfaces_reserve_error(monkeypatch):
    from pipeline import slack_client

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")

    with patch.object(slack_client.requests, "get",
                      lambda *a, **k: _Resp({"ok": False, "error": "missing_scope"})):
        result = slack_client.upload_file_to_slack_channel(
            channel_id="C123", filename="guide.pdf", file_bytes=b"pdf",
        )

    assert result["ok"] is False
    assert result["error"] == "missing_scope"


def test_channel_upload_requires_token_channel_and_bytes(monkeypatch):
    from pipeline import slack_client

    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    assert slack_client.upload_file_to_slack_channel("C1", "a.pdf", b"x")["error"] == (
        "SLACK_BOT_TOKEN is not set"
    )

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    assert slack_client.upload_file_to_slack_channel("", "a.pdf", b"x")["error"] == "No channel selected"
    assert slack_client.upload_file_to_slack_channel("C1", "a.pdf", b"")["error"] == (
        "No file bytes to upload"
    )
