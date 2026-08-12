"""Postgres storage for the analytics collector.

The droplet already runs Postgres 16 as a host service (the dating and
event-picker apps use it), so this service connects out to it rather than
shipping a database of its own. On a 2 GB box that is the difference between
costing nothing and costing another container.

Everything here is deliberately lossy. A write that fails is logged and dropped:
there is no retry queue and no unbounded buffering, because analytics must never
be able to exhaust memory or take the service down. Losing a click is fine.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from importlib import resources
from typing import Any, Iterable

log = logging.getLogger("moates_stats.db")

DATABASE_URL = os.environ.get("STATS_DATABASE_URL", "")

# Salt for the daily IP hash. Without it the hash space is small enough to brute
# force (there are only ~4 billion IPv4 addresses), so an unset salt is a real
# weakness, not a nitpick: the service refuses to hash without one.
IP_SALT = os.environ.get("STATS_IP_SALT", "")

# Small pool. One uvicorn worker writing short transactions needs very little,
# and every idle connection is a few MB of Postgres backend on a small droplet.
POOL_MIN = int(os.environ.get("STATS_POOL_MIN", "1"))
POOL_MAX = int(os.environ.get("STATS_POOL_MAX", "3"))

_pool = None


def configured() -> bool:
    """True when a database URL is set, so the app can no-op cleanly without one."""
    return bool(DATABASE_URL)


def get_pool():
    """Return the connection pool, opening it on first use.

    Opened lazily and with check disabled at import so that tests, and a
    container started while Postgres is down, do not blow up on import.
    """
    global _pool
    if _pool is None:
        from psycopg_pool import ConnectionPool

        _pool = ConnectionPool(
            DATABASE_URL,
            min_size=POOL_MIN,
            max_size=POOL_MAX,
            # Don't block startup waiting for the database; the first write will
            # wait (briefly) instead, and fail softly if it is still down.
            open=True,
            timeout=5.0,
            kwargs={"application_name": "moates-stats"},
        )
    return _pool


def init_schema() -> None:
    """Apply schema.sql. Idempotent, so it is safe to run on every start."""
    ddl = resources.files("moates_stats").joinpath("schema.sql").read_text()
    with get_pool().connection() as conn:
        conn.execute(ddl)
    log.info("analytics schema applied")


def hash_ip(ip: str) -> str | None:
    """Salted daily hash of an IP address.

    The salt includes the UTC date, so the hash rotates at midnight. That makes
    "unique visitors" a per-day figure by construction, which is the only figure
    worth reporting anyway, and it means the stored value stops being useful for
    correlating a person across days.
    """
    if not ip or not IP_SALT:
        return None
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    digest = hashlib.sha256(f"{IP_SALT}:{day}:{ip}".encode("utf-8")).hexdigest()
    return digest[:32]


def write_batch(session: dict[str, Any], events: Iterable[dict[str, Any]]) -> None:
    """Upsert the session and insert its events, in one transaction.

    Called from a background task after the response has already gone out, so
    nothing here is on the visitor's critical path. Exceptions are swallowed:
    the browser has been answered and there is nobody left to tell.
    """
    rows = list(events)
    try:
        with get_pool().connection() as conn:
            with conn.transaction():
                _upsert_session(conn, session, len(rows))
                if rows:
                    _insert_events(conn, session["session_id"], rows)
    except Exception:
        # Logged, never raised. A database blip must not become a 500, and by
        # this point the browser has its 204 regardless.
        log.warning("dropped %d analytics event(s)", len(rows), exc_info=True)


def _upsert_session(conn, session: dict[str, Any], new_events: int) -> None:
    """Insert the session on first sight, otherwise just advance its counters.

    The first batch carries the visitor's context (referrer, device, geo). Later
    batches from the same tab must not overwrite it, so ON CONFLICT touches only
    last_seen and event_count. That keeps the landing page and original referrer
    intact for the whole session, which is what attribution needs.
    """
    conn.execute(
        """
        INSERT INTO sessions (
            session_id, first_seen, last_seen, ip_hash, country, city, region,
            cf_timezone, referrer, landing_path, utm_source, utm_medium,
            utm_campaign, user_agent, device, browser_lang, screen_w, screen_h,
            is_bot, event_count
        )
        VALUES (
            %(session_id)s, now(), now(), %(ip_hash)s, %(country)s, %(city)s,
            %(region)s, %(cf_timezone)s, %(referrer)s, %(landing_path)s,
            %(utm_source)s, %(utm_medium)s, %(utm_campaign)s, %(user_agent)s,
            %(device)s, %(browser_lang)s, %(screen_w)s, %(screen_h)s,
            %(is_bot)s, %(new_events)s
        )
        ON CONFLICT (session_id) DO UPDATE SET
            last_seen   = now(),
            event_count = sessions.event_count + EXCLUDED.event_count
        """,
        {**session, "new_events": new_events},
    )


def _insert_events(conn, session_id: str, rows: list[dict[str, Any]]) -> None:
    """Insert a batch of events with one round trip."""
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO events (session_id, ts, kind, path, target, meta)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            """,
            [
                (
                    session_id,
                    row["ts"],
                    row["kind"],
                    row.get("path"),
                    row.get("target"),
                    json.dumps(row["meta"]) if row.get("meta") else None,
                )
                for row in rows
            ],
        )
