"""FastAPI collector for moates.com.au site analytics.

The site is served from GitHub Pages, which gives us no access logs and no place
to run code, so the page beacons its own events here. Everything about this
service is shaped by two rules:

1. **The site comes first.** A visitor must never wait on, or be affected by,
   analytics. `/e` validates cheaply, answers 204, and does the database write
   in a background task. There is no code path where a slow or dead database is
   visible to the browser.
2. **No raw IPs are stored.** The address is used to derive a salted daily hash
   and to read Cloudflare's geo headers, then discarded. What lands in Postgres
   identifies "the same visitor today" and a city, and nothing more.

Cloudflare fronts every *.moates.com.au subdomain, so `CF-Connecting-IP` and the
visitor location headers are available for free and there is no geo database to
ship or keep current.
"""

from __future__ import annotations

import logging
import os
import re
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from moates_stats import db

log = logging.getLogger("moates_stats")

# --- Config (all overridable via environment) ------------------------------

ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "STATS_ALLOWED_ORIGINS",
        "https://moates.com.au,https://www.moates.com.au",
    ).split(",")
    if o.strip()
]

# Payload caps. These bound how much one request can cost us, which matters more
# than usual here because the endpoint is unauthenticated by necessity.
MAX_EVENTS_PER_BATCH = int(os.environ.get("STATS_MAX_EVENTS_PER_BATCH", "50"))
MAX_BODY_BYTES = int(os.environ.get("STATS_MAX_BODY_BYTES", "32768"))
MAX_STR = int(os.environ.get("STATS_MAX_STR", "500"))
MAX_META_KEYS = int(os.environ.get("STATS_MAX_META_KEYS", "12"))

# Rate limits, per process and reset on restart. A first line of defence against
# one visitor (or one script) filling the table, not a serious anti-abuse system.
PER_IP_PER_MINUTE = int(os.environ.get("STATS_PER_IP_PER_MINUTE", "60"))
PER_IP_EVENTS_PER_DAY = int(os.environ.get("STATS_PER_IP_EVENTS_PER_DAY", "2000"))
GLOBAL_EVENTS_PER_DAY = int(os.environ.get("STATS_GLOBAL_EVENTS_PER_DAY", "200000"))

KINDS = {"pageview", "click", "outbound", "session_end"}

# Deliberately broad. Crawler traffic is kept, not dropped, so a false positive
# costs a filtered row rather than a lost visitor.
BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|headless|phantom|puppeteer|playwright|"
    r"curl|wget|python-requests|httpx|go-http-client|axios|scrapy|lighthouse|"
    r"facebookexternalhit|whatsapp|telegrambot|discordbot|preview|monitor|uptime",
    re.I,
)
MOBILE_RE = re.compile(r"iphone|ipod|android.*mobile|windows phone|mobile safari", re.I)
TABLET_RE = re.compile(r"ipad|android(?!.*mobile)|tablet", re.I)


# --- Rate limiting (in-memory, per process) --------------------------------


class RateLimiter:
    """Sliding-window counters for per-IP request and event rates."""

    def __init__(self) -> None:
        self._per_ip: dict[str, deque[float]] = defaultdict(deque)
        self._ip_events: dict[str, deque[tuple[float, int]]] = defaultdict(deque)
        self._global_events: deque[tuple[float, int]] = deque()

    @staticmethod
    def _trim(window: deque, now: float, span: float) -> None:
        while window:
            first = window[0]
            stamp = first[0] if isinstance(first, tuple) else first
            if stamp > now - span:
                break
            window.popleft()

    @staticmethod
    def _sum(window: deque[tuple[float, int]]) -> int:
        return sum(n for _, n in window)

    def allow(self, ip: str, count: int) -> bool:
        """Record a batch of `count` events from `ip`; False if it should be dropped."""
        now = time.time()
        day = 86_400

        self._trim(self._global_events, now, day)
        if self._sum(self._global_events) >= GLOBAL_EVENTS_PER_DAY:
            return False

        hits = self._per_ip[ip]
        self._trim(hits, now, 60)
        if len(hits) >= PER_IP_PER_MINUTE:
            return False

        ip_events = self._ip_events[ip]
        self._trim(ip_events, now, day)
        if self._sum(ip_events) >= PER_IP_EVENTS_PER_DAY:
            return False

        hits.append(now)
        ip_events.append((now, count))
        self._global_events.append((now, count))
        return True


limiter = RateLimiter()


# --- Request parsing --------------------------------------------------------


def client_ip(request: Request) -> str:
    """The visitor's address, preferring Cloudflare's header over the proxy chain.

    Used to derive a hash and nothing else; it is never stored or logged.
    """
    cf = request.headers.get("cf-connecting-ip")
    if cf:
        return cf.strip()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


def geo(request: Request) -> dict[str, str | None]:
    """Location from Cloudflare's visitor location headers.

    `CF-IPCountry` is present on every plan. The city/region/timezone headers
    require the "Add visitor location headers" managed transform to be enabled
    on the zone; without it these are simply absent, which is why nothing here
    treats a missing header as an error.
    """

    def header(name: str) -> str | None:
        value = (request.headers.get(name) or "").strip()
        # Cloudflare uses XX for "unknown" and T1 for Tor exit nodes.
        if not value or value in {"XX", "T1"}:
            return None
        return value[:MAX_STR]

    return {
        "country": header("cf-ipcountry"),
        "city": header("cf-ipcity"),
        "region": header("cf-region"),
        "cf_timezone": header("cf-timezone"),
    }


def device_of(user_agent: str) -> str:
    if not user_agent:
        return "unknown"
    if TABLET_RE.search(user_agent):
        return "tablet"
    if MOBILE_RE.search(user_agent):
        return "mobile"
    return "desktop"


def clean(value: Any, limit: int | None = None) -> str | None:
    """Trim a client-supplied string to something safe to store.

    The limit is resolved per call rather than bound as a default argument, so
    MAX_STR stays a genuine runtime setting instead of silently freezing to
    whatever the environment held at import.
    """
    if not isinstance(value, str):
        return None
    trimmed = value.strip()[: MAX_STR if limit is None else limit]
    return trimmed or None


def clean_meta(meta: Any) -> dict[str, Any] | None:
    """Keep a small, flat, scalar-only slice of a client-supplied meta object.

    The column is jsonb precisely so new event properties need no migration, but
    that freedom is the client's, not the internet's: nesting and long values are
    dropped here rather than stored.
    """
    if not isinstance(meta, dict) or not meta:
        return None
    out: dict[str, Any] = {}
    for key, value in list(meta.items())[:MAX_META_KEYS]:
        if not isinstance(key, str):
            continue
        if isinstance(value, bool) or isinstance(value, int) or isinstance(value, float):
            out[key[:64]] = value
        elif isinstance(value, str):
            out[key[:64]] = value[:200]
    return out or None


def event_time(raw: Any) -> datetime:
    """Client timestamp (epoch ms), clamped to something believable.

    Clocks on the open internet are wrong in both directions, sometimes by
    years. A timestamp more than a day out is discarded in favour of server
    time, so one bad clock cannot scatter rows across the table's history.
    """
    now = datetime.now(timezone.utc)
    if isinstance(raw, (int, float)) and raw > 0:
        try:
            stamp = datetime.fromtimestamp(raw / 1000, tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            return now
        if abs(stamp - now) <= timedelta(days=1):
            return stamp
    return now


# --- API models -------------------------------------------------------------


class EventIn(BaseModel):
    k: str = Field(default="", max_length=32)          # kind
    p: str | None = Field(default=None, max_length=2000)  # path
    t: str | None = Field(default=None, max_length=2000)  # target
    ts: float | None = None                             # client epoch ms
    m: dict[str, Any] | None = None                     # meta


class ContextIn(BaseModel):
    ref: str | None = Field(default=None, max_length=2000)
    land: str | None = Field(default=None, max_length=2000)
    utm_source: str | None = Field(default=None, max_length=200)
    utm_medium: str | None = Field(default=None, max_length=200)
    utm_campaign: str | None = Field(default=None, max_length=200)
    lang: str | None = Field(default=None, max_length=32)
    sw: int | None = None
    sh: int | None = None


class BatchIn(BaseModel):
    sid: str = Field(default="", max_length=64)
    ctx: ContextIn = Field(default_factory=ContextIn)
    events: list[EventIn] = Field(default_factory=list)


UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


# --- App --------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Apply the schema at startup, but never refuse to start without a database.

    A collector that will not boot is worse than one that drops events: it turns
    a database problem into a red deploy and a broken health check.
    """
    if db.configured():
        try:
            db.init_schema()
        except Exception:
            log.warning("could not apply analytics schema at startup", exc_info=True)
    else:
        log.warning("STATS_DATABASE_URL is not set; events will be discarded")
    yield


app = FastAPI(title="moates stats", docs_url=None, redoc_url=None, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "db": db.configured()}


@app.post("/e", status_code=204, response_class=Response)
async def collect(request: Request, background: BackgroundTasks) -> Response:
    """Accept a batch of events.

    Answers 204 in every case a well-formed request can produce, including when
    the batch is rate limited or the database is down. The browser is told
    nothing about the outcome because there is nothing it could usefully do with
    the information, and a client that retries on failure is a client that can
    amplify an outage.

    The body is parsed by hand rather than declared as a Pydantic parameter so
    the endpoint does not care about Content-Type. That matters: the page sends
    these with `navigator.sendBeacon` during unload, and an `application/json`
    beacon is a preflighted cross-origin request. A preflight that does not
    finish before the tab closes loses the batch, so the client sends
    `text/plain` (a CORS-simple request) and we accept it here.
    """
    raw = await request.body()
    if len(raw) > MAX_BODY_BYTES:
        raise HTTPException(413, "payload too large")
    try:
        batch = BatchIn.model_validate_json(raw)
    except Exception:
        raise HTTPException(400, "bad payload")

    if not UUID_RE.match(batch.sid):
        raise HTTPException(400, "bad session id")

    rows = [row for row in (parse_event(e) for e in batch.events[:MAX_EVENTS_PER_BATCH]) if row]
    if not rows:
        return Response(status_code=204)

    ip = client_ip(request)
    if not limiter.allow(ip or "unknown", len(rows)):
        return Response(status_code=204)

    if not db.configured():
        return Response(status_code=204)

    user_agent = clean(request.headers.get("user-agent"), 500) or ""
    session = {
        "session_id": batch.sid.lower(),
        "ip_hash": db.hash_ip(ip),
        **geo(request),
        "referrer": clean(batch.ctx.ref, 2000),
        "landing_path": clean(batch.ctx.land, 500),
        "utm_source": clean(batch.ctx.utm_source, 200),
        "utm_medium": clean(batch.ctx.utm_medium, 200),
        "utm_campaign": clean(batch.ctx.utm_campaign, 200),
        "user_agent": user_agent or None,
        "device": device_of(user_agent),
        "browser_lang": clean(batch.ctx.lang, 32),
        "screen_w": bounded_int(batch.ctx.sw),
        "screen_h": bounded_int(batch.ctx.sh),
        "is_bot": bool(BOT_RE.search(user_agent)) if user_agent else True,
    }

    # Runs after the response is flushed. A sync callable, so Starlette hands it
    # to the threadpool and the blocking database work stays off the event loop.
    background.add_task(db.write_batch, session, rows)
    return Response(status_code=204)


def parse_event(event: EventIn) -> dict[str, Any] | None:
    """Normalise one incoming event, or None if it is not something we record."""
    kind = (event.k or "").strip().lower()
    if kind not in KINDS:
        return None
    return {
        "kind": kind,
        "path": clean(event.p),
        "target": clean(event.t),
        "ts": event_time(event.ts),
        "meta": clean_meta(event.m),
    }


def bounded_int(value: Any) -> int | None:
    """Screen dimensions, rejecting the absurd rather than storing it."""
    if isinstance(value, int) and 0 < value <= 20_000:
        return value
    return None
