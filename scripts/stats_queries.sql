-- Ready-made queries for the site analytics database.
--
--   ssh -f -N -L 25433:localhost:5432 do
--   psql "postgresql://analytics_ro@localhost:25433/analytics"
--
-- Every query excludes crawlers with `NOT is_bot`. Drop that clause when you
-- specifically want to know how often the site is being indexed.

-- Traffic by day, last 30 days.
SELECT date_trunc('day', s.first_seen)::date AS day,
       count(*)                              AS sessions,
       count(DISTINCT s.ip_hash)             AS unique_visitors,
       sum(s.event_count)                    AS events
FROM sessions s
WHERE NOT s.is_bot
  AND s.first_seen > now() - interval '30 days'
GROUP BY 1
ORDER BY 1 DESC;

-- What people actually click. This is the question the whole service exists to
-- answer, so it is the one to look at first.
SELECT e.target,
       count(*)                    AS clicks,
       count(DISTINCT e.session_id) AS sessions
FROM events e
JOIN sessions s USING (session_id)
WHERE e.kind IN ('click', 'outbound')
  AND NOT s.is_bot
  AND e.ts > now() - interval '30 days'
GROUP BY 1
ORDER BY clicks DESC
LIMIT 50;

-- Most-viewed pages.
SELECT e.path,
       count(*)                     AS views,
       count(DISTINCT e.session_id) AS sessions
FROM events e
JOIN sessions s USING (session_id)
WHERE e.kind = 'pageview'
  AND NOT s.is_bot
  AND e.ts > now() - interval '30 days'
GROUP BY 1
ORDER BY views DESC
LIMIT 50;

-- Where visitors come from. Direct traffic has a null referrer.
SELECT coalesce(nullif(split_part(split_part(s.referrer, '://', 2), '/', 1), ''), '(direct)') AS source,
       count(*) AS sessions
FROM sessions s
WHERE NOT s.is_bot
  AND s.first_seen > now() - interval '90 days'
GROUP BY 1
ORDER BY sessions DESC
LIMIT 30;

-- Geography. City is null unless the Cloudflare visitor-location managed
-- transform is enabled on the zone.
SELECT s.country,
       s.city,
       count(*)                  AS sessions,
       count(DISTINCT s.ip_hash) AS unique_visitors
FROM sessions s
WHERE NOT s.is_bot
  AND s.first_seen > now() - interval '90 days'
GROUP BY 1, 2
ORDER BY sessions DESC
LIMIT 40;

-- Device split, which is worth checking against the mobile work on the site.
SELECT s.device,
       count(*) AS sessions,
       round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM sessions s
WHERE NOT s.is_bot
  AND s.first_seen > now() - interval '90 days'
GROUP BY 1
ORDER BY sessions DESC;

-- Landing pages, and how engaged the visitors who arrived there were.
SELECT s.landing_path,
       count(*)              AS sessions,
       round(avg(s.event_count), 1) AS avg_events,
       count(*) FILTER (WHERE s.event_count <= 1) AS bounced
FROM sessions s
WHERE NOT s.is_bot
  AND s.first_seen > now() - interval '30 days'
GROUP BY 1
ORDER BY sessions DESC
LIMIT 30;

-- Session length. Sessions with a single event have no measurable duration, so
-- they are excluded rather than counted as zero.
SELECT round(avg(extract(epoch FROM s.last_seen - s.first_seen))) AS avg_seconds,
       round(percentile_cont(0.5) WITHIN GROUP (
           ORDER BY extract(epoch FROM s.last_seen - s.first_seen))) AS median_seconds
FROM sessions s
WHERE NOT s.is_bot
  AND s.event_count > 1
  AND s.first_seen > now() - interval '30 days';

-- Outbound clicks: which links off the site are actually worth having.
SELECT e.target, count(*) AS clicks
FROM events e
JOIN sessions s USING (session_id)
WHERE e.kind = 'outbound'
  AND NOT s.is_bot
  AND e.ts > now() - interval '90 days'
GROUP BY 1
ORDER BY clicks DESC
LIMIT 30;

-- One visitor's path through the site. Useful when a session looks interesting
-- in the summaries above and you want the story behind it.
-- SELECT ts, kind, path, target, meta
-- FROM events
-- WHERE session_id = '...'
-- ORDER BY ts;
