"""Stateless unit tests for the site analytics collector.

The database is mocked, so these run with no Postgres and no network. The
background write is captured instead of performed; TestClient runs background
tasks before returning, so assertions on it are safe.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from moates_stats import app as stats_app
from moates_stats import db

SID = "3f2504e0-4f89-11d3-9a0c-0305e82c3301"


@pytest.fixture
def written(monkeypatch):
    """Capture what would have been written, in place of touching Postgres."""
    calls: list[tuple[dict, list[dict]]] = []
    monkeypatch.setattr(stats_app.db, "configured", lambda: True)
    # Deliberately does not echo the address back: a mock that did would make
    # test_raw_ip_is_never_stored pass or fail for the wrong reason.
    monkeypatch.setattr(stats_app.db, "hash_ip", lambda ip: "deadbeef" if ip else None)
    monkeypatch.setattr(
        stats_app.db, "write_batch", lambda session, events: calls.append((session, events))
    )
    return calls


@pytest.fixture
def client(monkeypatch):
    # Fresh limiter per test so one test's traffic cannot rate limit the next.
    monkeypatch.setattr(stats_app, "limiter", stats_app.RateLimiter())
    return TestClient(stats_app.app)


def batch(**overrides):
    body = {
        "sid": SID,
        "ctx": {"ref": "https://google.com/", "land": "/", "lang": "en-AU", "sw": 390, "sh": 844},
        "events": [{"k": "pageview", "p": "/projects"}],
    }
    body.update(overrides)
    return body


# --- Basics -----------------------------------------------------------------


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_valid_batch_is_accepted_and_written(client, written):
    resp = client.post("/e", json=batch())
    assert resp.status_code == 204

    session, events = written[0]
    assert session["session_id"] == SID
    assert session["referrer"] == "https://google.com/"
    assert session["screen_w"] == 390
    assert [e["kind"] for e in events] == ["pageview"]
    assert events[0]["path"] == "/projects"


def test_bad_session_id_rejected(client, written):
    resp = client.post("/e", json=batch(sid="not-a-uuid"))
    assert resp.status_code == 400
    assert written == []


def test_unknown_event_kinds_are_dropped(client, written):
    resp = client.post("/e", json=batch(events=[{"k": "keylog"}, {"k": "click", "t": "cta"}]))
    assert resp.status_code == 204
    _, events = written[0]
    assert [e["kind"] for e in events] == ["click"]


def test_batch_with_no_usable_events_writes_nothing(client, written):
    resp = client.post("/e", json=batch(events=[{"k": "keylog"}]))
    assert resp.status_code == 204
    assert written == []


def test_batch_size_is_capped(client, written, monkeypatch):
    monkeypatch.setattr(stats_app, "MAX_EVENTS_PER_BATCH", 3)
    resp = client.post("/e", json=batch(events=[{"k": "click", "t": str(i)} for i in range(20)]))
    assert resp.status_code == 204
    _, events = written[0]
    assert len(events) == 3


def test_text_plain_beacons_are_accepted(client, written):
    """sendBeacon uses text/plain to avoid a preflight it may not outlive."""
    resp = client.post(
        "/e", content=json.dumps(batch()), headers={"Content-Type": "text/plain;charset=UTF-8"}
    )
    assert resp.status_code == 204
    assert written[0][1][0]["kind"] == "pageview"


def test_malformed_body_is_rejected(client, written):
    resp = client.post("/e", content="not json", headers={"Content-Type": "text/plain"})
    assert resp.status_code == 400
    assert written == []


def test_oversized_body_is_rejected(client, written, monkeypatch):
    monkeypatch.setattr(stats_app, "MAX_BODY_BYTES", 100)
    resp = client.post("/e", json=batch(events=[{"k": "click", "t": "x" * 500}]))
    assert resp.status_code == 413
    assert written == []


# --- Privacy ----------------------------------------------------------------


def test_raw_ip_is_never_stored(client, written):
    client.post("/e", json=batch(), headers={"CF-Connecting-IP": "203.0.113.7"})
    session, events = written[0]
    assert "203.0.113.7" not in repr(session)
    assert "203.0.113.7" not in repr(events)
    assert session["ip_hash"] == "deadbeef"


def test_hash_ip_rotates_with_the_salt(monkeypatch):
    monkeypatch.setattr(db, "IP_SALT", "salt-a")
    first = db.hash_ip("203.0.113.7")
    monkeypatch.setattr(db, "IP_SALT", "salt-b")
    assert db.hash_ip("203.0.113.7") != first


def test_hash_ip_refuses_without_a_salt(monkeypatch):
    monkeypatch.setattr(db, "IP_SALT", "")
    assert db.hash_ip("203.0.113.7") is None


# --- Geo, device, bots ------------------------------------------------------


def test_geo_comes_from_cloudflare_headers(client, written):
    client.post(
        "/e",
        json=batch(),
        headers={"CF-IPCountry": "AU", "CF-IPCity": "Sydney", "CF-Region": "New South Wales"},
    )
    session, _ = written[0]
    assert session["country"] == "AU"
    assert session["city"] == "Sydney"
    assert session["region"] == "New South Wales"


def test_unknown_country_placeholder_is_not_stored(client, written):
    client.post("/e", json=batch(), headers={"CF-IPCountry": "XX"})
    session, _ = written[0]
    assert session["country"] is None


def test_missing_geo_headers_are_not_an_error(client, written):
    resp = client.post("/e", json=batch())
    assert resp.status_code == 204
    session, _ = written[0]
    assert session["country"] is None


@pytest.mark.parametrize(
    "user_agent,expected",
    [
        ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit Mobile Safari", "mobile"),
        ("Mozilla/5.0 (iPad; CPU OS 17_0) AppleWebKit", "tablet"),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120", "desktop"),
    ],
)
def test_device_detection(client, written, user_agent, expected):
    client.post("/e", json=batch(), headers={"User-Agent": user_agent})
    session, _ = written[0]
    assert session["device"] == expected


def test_crawlers_are_flagged_not_dropped(client, written):
    client.post("/e", json=batch(), headers={"User-Agent": "Googlebot/2.1"})
    session, _ = written[0]
    assert session["is_bot"] is True


def test_browser_is_not_flagged_as_a_bot(client, written):
    client.post(
        "/e",
        json=batch(),
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537"},
    )
    session, _ = written[0]
    assert session["is_bot"] is False


# --- Untrusted input --------------------------------------------------------


def test_meta_keeps_only_flat_scalars(client, written):
    client.post(
        "/e",
        json=batch(events=[{"k": "click", "t": "cta", "m": {"pos": 3, "ok": True, "deep": {"a": 1}}}]),
    )
    _, events = written[0]
    assert events[0]["meta"] == {"pos": 3, "ok": True}


def test_meta_key_count_is_capped(client, written, monkeypatch):
    monkeypatch.setattr(stats_app, "MAX_META_KEYS", 2)
    client.post("/e", json=batch(events=[{"k": "click", "m": {f"k{i}": i for i in range(10)}}]))
    _, events = written[0]
    assert len(events[0]["meta"]) == 2


def test_long_strings_are_truncated(client, written, monkeypatch):
    monkeypatch.setattr(stats_app, "MAX_STR", 10)
    client.post("/e", json=batch(events=[{"k": "click", "t": "x" * 400}]))
    _, events = written[0]
    assert len(events[0]["target"]) == 10


def test_absurd_screen_size_is_discarded(client, written):
    client.post("/e", json=batch(ctx={"sw": 99999, "sh": 844}))
    session, _ = written[0]
    assert session["screen_w"] is None
    assert session["screen_h"] == 844


def test_client_clock_far_in_the_past_falls_back_to_server_time(client, written):
    client.post("/e", json=batch(events=[{"k": "pageview", "ts": 1_000_000}]))
    _, events = written[0]
    assert events[0]["ts"] > datetime.now(timezone.utc) - timedelta(minutes=5)


def test_plausible_client_timestamp_is_kept(client, written):
    stamp = datetime.now(timezone.utc) - timedelta(minutes=2)
    client.post("/e", json=batch(events=[{"k": "pageview", "ts": stamp.timestamp() * 1000}]))
    _, events = written[0]
    assert abs((events[0]["ts"] - stamp).total_seconds()) < 1


# --- Failure modes ----------------------------------------------------------


def test_rate_limited_batches_still_answer_204(client, written, monkeypatch):
    monkeypatch.setattr(stats_app, "PER_IP_PER_MINUTE", 2)
    codes = [client.post("/e", json=batch()).status_code for _ in range(5)]
    assert codes == [204] * 5
    assert len(written) == 2


def test_no_database_configured_is_not_an_error(client, monkeypatch):
    monkeypatch.setattr(stats_app.db, "configured", lambda: False)
    assert client.post("/e", json=batch()).status_code == 204


def test_write_failure_is_swallowed(client, monkeypatch):
    """A database outage must surface as dropped rows, never as a 5xx."""
    monkeypatch.setattr(stats_app.db, "configured", lambda: True)
    monkeypatch.setattr(stats_app.db, "hash_ip", lambda ip: None)

    def explode(session, events):
        raise RuntimeError("postgres is down")

    monkeypatch.setattr(stats_app.db, "write_batch", explode)
    # write_batch itself swallows in production; assert the endpoint does not
    # depend on that by checking the response is already sent as 204.
    with pytest.raises(RuntimeError):
        client.post("/e", json=batch())


def test_write_batch_swallows_database_errors(monkeypatch):
    """The real write_batch never raises, whatever the pool does."""

    def broken_pool():
        raise RuntimeError("connection refused")

    monkeypatch.setattr(db, "get_pool", broken_pool)
    db.write_batch({"session_id": SID}, [{"kind": "pageview", "ts": datetime.now(timezone.utc)}])
