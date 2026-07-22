"""Stateless unit tests for the web chat proxy.

The OpenAI call is mocked, so these run with no API key and no network.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from moates_chat import app as chat_app


@pytest.fixture
def client(monkeypatch):
    # Fresh rate limiter per test so limits from one test don't bleed into another.
    monkeypatch.setattr(chat_app, "limiter", chat_app.RateLimiter())
    # Deterministic model reply; asserts the question is passed through.
    monkeypatch.setattr(
        chat_app, "generate_reply", lambda q: f"answer to: {q}"
    )
    return TestClient(chat_app.app)


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_chat_returns_reply(client):
    resp = client.post("/chat", json={"message": "What does Marcus do?"})
    assert resp.status_code == 200
    assert resp.json()["reply"] == "answer to: What does Marcus do?"


def test_empty_message_rejected(client):
    resp = client.post("/chat", json={"message": "   "})
    assert resp.status_code == 400


def test_message_is_length_capped(client, monkeypatch):
    monkeypatch.setattr(chat_app, "MAX_MESSAGE_CHARS", 10)
    seen = {}
    monkeypatch.setattr(chat_app, "generate_reply", lambda q: seen.setdefault("q", q) or "ok")
    resp = client.post("/chat", json={"message": "x" * 100})
    assert resp.status_code == 200
    assert len(seen["q"]) == 10


def test_per_minute_rate_limit(client, monkeypatch):
    monkeypatch.setattr(chat_app, "PER_IP_PER_MINUTE", 3)
    for _ in range(3):
        assert client.post("/chat", json={"message": "hi"}).status_code == 200
    resp = client.post("/chat", json={"message": "hi"})
    assert resp.status_code == 429


def test_global_daily_backstop(client, monkeypatch):
    monkeypatch.setattr(chat_app, "GLOBAL_PER_DAY", 2)
    monkeypatch.setattr(chat_app, "PER_IP_PER_MINUTE", 100)
    for _ in range(2):
        assert client.post("/chat", json={"message": "hi"}).status_code == 200
    resp = client.post("/chat", json={"message": "hi"})
    assert resp.status_code == 429


def test_provider_error_is_not_leaked(client, monkeypatch):
    def boom(_q):
        raise RuntimeError("secret key sk-abc123 leaked in stack")

    monkeypatch.setattr(chat_app, "generate_reply", boom)
    resp = client.post("/chat", json={"message": "hi"})
    assert resp.status_code == 503
    assert "sk-abc123" not in resp.text
    assert "secret" not in resp.text.lower()


def test_generate_reply_falls_back_to_refusal_on_empty(monkeypatch):
    class FakeResp:
        output_text = ""

    class FakeResponses:
        def create(self, **_kwargs):
            return FakeResp()

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setattr(chat_app, "_client", FakeClient())
    assert chat_app.generate_reply("anything") == chat_app.REFUSAL


def test_system_prompt_contains_kb_and_rules():
    # The whole KB is stuffed into the system prompt, and the scoping rule is present.
    assert "Marcus Oates" in chat_app.SYSTEM_PROMPT
    assert "Gym Junkie" in chat_app.SYSTEM_PROMPT
    assert chat_app.REFUSAL in chat_app.SYSTEM_PROMPT
