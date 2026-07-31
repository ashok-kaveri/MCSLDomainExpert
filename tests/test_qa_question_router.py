"""tests/test_qa_question_router.py — routing + metric formatting for the Slack QA bot."""
from __future__ import annotations

from unittest.mock import patch

from pipeline import qa_question_router as router


# ── Intent routing ───────────────────────────────────────────────────────────

def test_automated_count_intent_calls_metrics_not_rag():
    fake = {"spec_files": 69, "test_blocks": 333, "folders": 13,
            "by_folder": {"orders": 20, "carriers": 15}}
    with patch("pipeline.qa_metrics.count_automated_cases", return_value=fake) as m, \
         patch.object(router, "_rag_answer") as rag:
        out = router.answer_question("How many cases are automated?")
    m.assert_called_once()
    rag.assert_not_called()
    assert "333" in out and "69" in out


def test_release_run_intent_calls_metrics_not_rag():
    fake = {"available": True, "total": 3, "passed": 3, "failures": 0,
            "failure_rate": "0%", "risk_level": "LOW", "decision": "PROCEED",
            "reason": "All tests passed", "flaky": []}
    with patch("pipeline.qa_metrics.latest_release_run", return_value=fake) as m, \
         patch.object(router, "_rag_answer") as rag:
        out = router.answer_question("How many cases ran as part of the release?")
    m.assert_called_once()
    rag.assert_not_called()
    assert "3 cases ran" in out and "PROCEED" in out


def test_release_intent_wins_over_automation_intent():
    # "how many cases ran" contains "how many cases"; release intent must take priority.
    with patch("pipeline.qa_metrics.latest_release_run", return_value={"available": False, "error": "x"}) as run, \
         patch("pipeline.qa_metrics.count_automated_cases") as auto:
        router.answer_question("how many test cases ran in the last run")
    run.assert_called_once()
    auto.assert_not_called()


def test_regression_count_intent_calls_metric_not_rag():
    fake = {"available": True, "total": 1980, "tab_count": 38, "by_tab": {"Orders Grid": 305}}
    with patch("pipeline.qa_metrics.count_regression_cases", return_value=fake) as m, \
         patch.object(router, "_rag_answer") as rag:
        out = router.answer_question("how many test cases are there in the regression sheet?")
    m.assert_called_once()
    rag.assert_not_called()
    assert "1980" in out and "38 tabs" in out


def test_freeform_question_falls_through_to_rag():
    with patch.object(router, "_rag_answer", return_value="RAG answer") as rag:
        out = router.answer_question("How do I add a UPS account?")
    rag.assert_called_once()
    assert out == "RAG answer"


def test_empty_question_returns_help():
    out = router.answer_question("   ")
    assert "automation coverage" in out.lower() or "ask me" in out.lower()


# ── Metric formatting edge cases ─────────────────────────────────────────────

def test_release_run_unavailable_is_reported_gracefully():
    fake = {"available": False, "error": "No run summary found."}
    with patch("pipeline.qa_metrics.latest_release_run", return_value=fake):
        out = router.answer_question("how many cases ran in the release")
    assert "No run summary" in out


# ── RAG path uses both collections ───────────────────────────────────────────

def test_trigger_keyword_matching():
    from pipeline import slack_qa_bot as bot
    triggers = ["mcslbot"]
    # Addressed → matched, keyword stripped
    assert bot._match_trigger("@mcslbot how many cases ran?", triggers) == (True, "how many cases ran?")
    assert bot._match_trigger("mcslbot: how many cases are automated", triggers) == (True, "how many cases are automated")
    assert bot._match_trigger("@MCSLBot generate support guide for lane \"x\"", triggers)[0] is True
    # Not addressed → ignored, even if it reads like a question
    assert bot._match_trigger("how many cases ran in the release?", triggers) == (False, "")
    assert bot._match_trigger("@fedexbot how many cases ran?", triggers) == (False, "")
    assert bot._match_trigger("", triggers) == (False, "")
    # Keyword must be a whole word (won't match 'mcslbottle')
    assert bot._match_trigger("mcslbottle test", triggers) == (False, "")


def test_trigger_parsing_from_env(monkeypatch):
    from pipeline import slack_qa_bot as bot
    monkeypatch.setenv("SLACK_QA_TRIGGERS", "@mcslBot, mcsl ,")
    assert bot._parse_triggers() == ["mcslbot", "mcsl"]
    monkeypatch.delenv("SLACK_QA_TRIGGERS", raising=False)
    assert bot._parse_triggers() == ["mcslbot"]  # default


def test_channel_allowlist_parsing(monkeypatch):
    from pipeline import slack_qa_bot as bot
    monkeypatch.setenv("SLACK_QA_CHANNELS", "#qa_members_internal, C08TFRPCW1Z ,")
    assert bot._parse_channel_allowlist() == ["qa_members_internal", "C08TFRPCW1Z"]


def test_resolve_channel_ids_passes_through_ids_without_api():
    from pipeline import slack_qa_bot as bot
    # Pure IDs resolve without any network call
    assert bot._resolve_channel_ids(["C08TFRPCW1Z", "G123ABC"]) == {"C08TFRPCW1Z", "G123ABC"}


def test_support_guide_request_parsing():
    from pipeline.support_guide_slack import parse_support_guide_request as p
    # Card by URL
    r = p("generate support guide for https://trello.com/c/Ab12Cd34/123-some-title")
    assert r == {"kind": "card", "card_ref": "Ab12Cd34"}
    # Lane combined
    r = p('generate support guide for lane "MCSL 381"')
    assert r == {"kind": "lane", "lane_name": "MCSL 381"}
    # Lane per-card
    r = p('generate per-card support guides for lane "MCSL 381"')
    assert r == {"kind": "lane_per_card", "lane_name": "MCSL 381"}
    # Lane name without quotes
    r = p("generate support guide for list Ready for QA")
    assert r["kind"] == "lane" and r["lane_name"] == "Ready for QA"
    # Trigger but no target
    assert p("can you make a support guide?")["kind"] == "unknown"
    # Not a support-guide request at all
    assert p("how many cases are automated?") is None
    assert p("hello team") is None


def test_support_guide_does_not_collide_with_metric_questions():
    # A metric question must NOT be captured by the support-guide parser.
    from pipeline.support_guide_slack import parse_support_guide_request as p
    assert p("how many cases ran in the release?") is None


def test_run_tests_request_parsing():
    from pipeline.test_trigger_slack import parse_run_tests_request as p
    assert p("run tests for special services") == {"keyword": "special services"}
    assert p("run test orderGrid") == {"keyword": "orderGrid"}
    assert p("trigger automation for cod") == {"keyword": "cod"}
    assert p("run all tests")["keyword"] == ""  # 'all' is a stopword → empty → refused downstream
    # Not a run-tests request
    assert p("how many cases ran in the release?") is None  # 'ran' != 'run'
    assert p("how many test cases are automated?") is None  # no run verb
    assert p("generate support guide for lane \"x\"") is None


def test_env_sample_request_parsing():
    from pipeline.env_sample_slack import parse_env_sample_request as p
    assert p("get env sample")
    assert p("share the env template")
    assert p("can you send the environment example file")
    assert not p("how do I add a UPS account?")
    assert not p("run smoke")


def test_env_sample_never_leaks_real_env(monkeypatch, tmp_path):
    from pipeline import env_sample_slack as es
    # Simulate a repo where real env files are tracked alongside the sample.
    (tmp_path / ".env_sample").write_text("STORE=__placeholder__\n")
    (tmp_path / ".env").write_text("STORE=secret-real\nTOKEN=xoxb-leak\n")
    (tmp_path / "carrier-envs").mkdir()
    (tmp_path / "carrier-envs" / "amazon.env").write_text("AMAZON_KEY=real-secret\n")
    monkeypatch.setattr(es, "_git_tracked",
                        lambda repo: {".env_sample", ".env", "carrier-envs/amazon.env"})
    out = es.get_env_samples(repo_path=str(tmp_path))
    names = [rel for rel, _ in out]
    assert names == [".env_sample"]                       # only the sample
    assert all("secret" not in c and "xoxb" not in c for _, c in out)  # no secrets


def test_detect_tag():
    from pipeline.test_trigger_slack import detect_tag
    assert detect_tag("smoke") == "@smoke"
    assert detect_tag("regression") == "@regression"
    assert detect_tag("@onboarding") == "@onboarding"
    assert detect_tag("sanity") == "@sanity"
    assert detect_tag("special services") is None   # folder, not a tag
    assert detect_tag("orderGrid") is None
    assert detect_tag("") is None


def test_find_specs_matches_folder(monkeypatch):
    from pipeline import test_trigger_slack as tt
    fake = {"orderGrid": ["tests/orderGrid/a.spec.ts", "tests/orderGrid/b.spec.ts"],
            "specialServices": ["tests/specialServices/c.spec.ts"]}
    monkeypatch.setattr(tt, "enumerate_specs", lambda repo: fake)
    repo, specs, folders = tt.find_specs("special services", repo_path="/x")
    assert specs == ["tests/specialServices/c.spec.ts"]
    repo, specs, folders = tt.find_specs("ordergrid", repo_path="/x")
    assert len(specs) == 2
    repo, specs, folders = tt.find_specs("", repo_path="/x")
    assert specs == [] and "orderGrid" in folders


def test_rag_answer_searches_wiki_and_code(monkeypatch):
    calls = {"search": 0, "search_code": []}

    def fake_search(q, k=8):
        calls["search"] += 1
        return []

    def fake_search_code(q, k=4, source_type=""):
        calls["search_code"].append(source_type)
        return []

    monkeypatch.setattr("rag.vectorstore.search", fake_search)
    monkeypatch.setattr("rag.code_indexer.search_code", fake_search_code)
    out = router._rag_answer("anything")
    assert calls["search"] == 1
    assert "automation" in calls["search_code"]
    # No docs found → friendly fallback, no LLM call needed
    assert "knowledge base" in out.lower()
