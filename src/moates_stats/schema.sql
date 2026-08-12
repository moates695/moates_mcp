-- Analytics schema for moates.com.au.
--
-- Applied on service startup, so it is written to be idempotent: a deploy that
-- adds a column re-runs this file harmlessly. Never write a destructive
-- statement in here.

CREATE TABLE IF NOT EXISTS sessions (
    session_id    uuid PRIMARY KEY,
    first_seen    timestamptz NOT NULL DEFAULT now(),
    last_seen     timestamptz NOT NULL DEFAULT now(),

    -- Salted daily hash of the visitor's IP, never the address itself. The salt
    -- rotates at UTC midnight, so a hash identifies "the same visitor today"
    -- and nothing beyond that.
    ip_hash       text,

    -- Geo, straight from Cloudflare's visitor location headers. Free, and it
    -- saves shipping a MaxMind database around.
    country       text,
    city          text,
    region        text,
    cf_timezone   text,

    referrer      text,
    landing_path  text,
    utm_source    text,
    utm_medium    text,
    utm_campaign  text,

    user_agent    text,
    device        text,          -- mobile | tablet | desktop | unknown
    browser_lang  text,
    screen_w      integer,
    screen_h      integer,

    -- Kept rather than dropped, so crawler traffic can be excluded at query
    -- time but is still there when you want to know how often you are indexed.
    is_bot        boolean NOT NULL DEFAULT false,
    event_count   integer NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS events (
    id          bigserial PRIMARY KEY,
    session_id  uuid NOT NULL REFERENCES sessions (session_id) ON DELETE CASCADE,
    ts          timestamptz NOT NULL DEFAULT now(),
    kind        text NOT NULL,   -- pageview | click | outbound | session_end
    path        text,            -- route the event happened on
    target      text,            -- data-track id, or the outbound URL
    meta        jsonb
);

CREATE INDEX IF NOT EXISTS events_ts_idx ON events (ts DESC);
CREATE INDEX IF NOT EXISTS events_kind_ts_idx ON events (kind, ts DESC);
CREATE INDEX IF NOT EXISTS events_session_idx ON events (session_id);
CREATE INDEX IF NOT EXISTS events_target_idx ON events (target) WHERE target IS NOT NULL;

CREATE INDEX IF NOT EXISTS sessions_first_seen_idx ON sessions (first_seen DESC);
CREATE INDEX IF NOT EXISTS sessions_human_idx ON sessions (first_seen DESC) WHERE NOT is_bot;
