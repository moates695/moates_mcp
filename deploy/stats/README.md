# moates site analytics: deployment

A FastAPI collector (`moates_stats.app`) that records what visitors do on
https://moates.com.au. GitHub Pages is static hosting with no access logs and
nowhere to run code, so the page beacons its own events to this service.

It runs as a Docker container (`moates-stats-prod`) on the shared
`backend-prod_api-network`, alongside `moates-chat-prod` and `moates-mcp-prod`,
and writes to the droplet's **host** Postgres rather than a database of its own.

## What is stored

No raw IP addresses. The visitor's address is used to derive a salted daily hash
and to read Cloudflare's geo headers, then discarded. The hash rotates at UTC
midnight, so it identifies "the same visitor today" and nothing further, which
is exactly what a unique-visitor count needs and no more.

| | |
| --- | --- |
| Per session | daily IP hash, country/city/region, referrer, landing page, UTM tags, user agent, device class, language, screen size, bot flag |
| Per event | timestamp, kind (`pageview`/`click`/`outbound`/`session_end`), path, target, free-form `meta` jsonb |

Crawler traffic is **flagged, not dropped** (`sessions.is_bot`), so it can be
excluded at query time but is still there when you want to know how often you
are being indexed.

## One-time setup on the droplet

### 1. Database and roles

The droplet runs Postgres 16 as a host systemd service. Create a dedicated
database so a bad analytics query can never touch the other apps' data:

```bash
ssh do
sudo -u postgres psql <<'SQL'
CREATE ROLE analytics_rw LOGIN PASSWORD 'pick-a-strong-one';
CREATE ROLE analytics_ro LOGIN PASSWORD 'pick-another-one';
CREATE DATABASE analytics OWNER analytics_rw;
SQL

sudo -u postgres psql -d analytics <<'SQL'
GRANT CONNECT ON DATABASE analytics TO analytics_ro;
GRANT USAGE ON SCHEMA public TO analytics_ro;
ALTER DEFAULT PRIVILEGES FOR ROLE analytics_rw IN SCHEMA public
    GRANT SELECT ON TABLES TO analytics_ro;
SQL
```

`analytics_rw` is the service. `analytics_ro` is for you, over the SSH tunnel:
read-only, so an exploratory query cannot delete a month of data.

The tables themselves are created by the service on startup (`schema.sql` is
idempotent), so there is no migration step to run here.

### 2. Let the container reach the host Postgres

**Nothing to change here as of 2026-08-12** — the droplet is already set up for
it, and both of the obvious edits would be redundant:

- `postgresql.conf` already has `listen_addresses = '*'`.
- `pg_hba.conf` already has `host all all 172.16.0.0/12 md5`, which covers both
  docker bridges (the shared network is `172.18.0.0/16`; `host.docker.internal`
  resolves to the default bridge gateway `172.17.0.1`).

`md5` in pg_hba is not a downgrade in practice: since PostgreSQL 10 a role whose
password is stored as SCRAM authenticates with SCRAM even when the line says
md5, and PG16 hashes new passwords with SCRAM by default.

Verify from inside the network rather than assuming:

```bash
ssh do 'docker run --rm --network backend-prod_api-network \
  --add-host host.docker.internal:host-gateway postgres:16-alpine \
  psql "postgresql://analytics_rw:...@host.docker.internal:5432/analytics" -c "select 1"'
```

> **Unrelated but worth fixing:** port 5432 is reachable from the public
> internet (`listen_addresses = '*'`, ufw inactive, iptables INPUT policy
> ACCEPT). `pg_hba.conf` still rejects any source outside the allow-list, so
> this is exposure rather than an open door, but it invites version
> fingerprinting and connection-exhaustion, and turns any future pg_hba slip
> into an immediate compromise. A DigitalOcean cloud firewall, or:
>
> ```bash
> ufw allow OpenSSH && ufw allow 80,443/tcp && ufw deny 5432/tcp && ufw enable
> ```
>
> Check the docker bridges still reach Postgres afterwards; ufw and Docker
> interact badly and `DOCKER-USER` rules may be needed.

### 3. Build context and secrets

```bash
ssh do 'mkdir -p /opt/moates_stats/deploy/stats'
ssh do 'cat > /opt/moates_stats/deploy/stats/.env' <<'EOF'
STATS_DATABASE_URL=postgresql://analytics_rw:pick-a-strong-one@host.docker.internal:5432/analytics
# Any long random string. Changing it re-anonymises every future hash, so treat
# it as a secret and do not rotate it casually.
STATS_IP_SALT=generate-with-openssl-rand-hex-32
# Optional overrides:
# STATS_ALLOWED_ORIGINS=https://moates.com.au,https://www.moates.com.au
EOF
```

Generate the salt with `openssl rand -hex 32`. Note that an **unset salt means
no hash is stored at all** rather than an unsalted one, since a bare SHA-256 of
an IPv4 address is trivially reversible.

### 4. DNS

Add `stats.moates.com.au` in Cloudflare pointing at the droplet, **proxied**
(orange cloud). The proxy is not optional here: it is what supplies
`CF-Connecting-IP` and the geo headers.

Then enable **Rules → Transform Rules → Managed Transforms → Add visitor
location headers** on the zone. Without it you get `CF-IPCountry` only, and
city/region/timezone stay empty. Nothing breaks, the columns are just null.

### 5. Reverse-proxy vhost

Public subdomains are fronted by a single dockerised proxy, `nginx-proxy-prod`,
which renders one shared template
(`/root/gym_junkie_server/nginx/nginx.conf.template`) via the image's envsubst
step. Append a `stats` vhost mirroring the `chat` block:

```nginx
server {
    listen 80;
    server_name stats.moates.com.au;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name stats.moates.com.au;

    ssl_certificate     /etc/nginx/ssl/cloudflare-cert.pem;
    ssl_certificate_key /etc/nginx/ssl/cloudflare-key.pem;

    # Beacons are small; anything larger is not one of ours.
    client_max_body_size 32k;

    location / {
        resolver 127.0.0.11 valid=30s;               # Docker embedded DNS
        set $stats_upstream http://moates-stats-prod:8000;
        proxy_pass $stats_upstream;

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_read_timeout 15s;
    }
}
```

Validate the render in a throwaway container on the shared network before
touching the live proxy:

```bash
TPL=/root/gym_junkie_server/nginx/nginx.conf.template
ssh do "cp $TPL $TPL.bak-stats"
# ...append the block above to $TPL...
ssh do 'docker run --rm --network backend-prod_api-network \
  -e NGINX_ENVSUBST_FILTER="^API_PORT$" -e API_PORT=8000 \
  -v /root/gym_junkie_server/nginx/nginx.conf.template:/etc/nginx/templates/nginx.conf.template:ro \
  -v /root/gym_junkie_server/nginx/ssl:/etc/nginx/ssl:ro \
  nginx:alpine nginx -t'
```

Only once `nginx -t` reports **syntax is ok** / **test is successful**, apply it
by restarting the proxy (a plain reload will *not* re-render the template):

```bash
ssh do 'docker restart nginx-proxy-prod'
```

That is a ~1-2s blip for every site behind the proxy, so it is
validated-then-restart, never restart-and-hope. Roll back with
`cp $TPL.bak-stats $TPL && docker restart nginx-proxy-prod`.

## Deploy

From a clone of this repo (not on the droplet):

```bash
deploy/deploy_stats.sh                # deploy committed HEAD
deploy/deploy_stats.sh --allow-dirty  # deploy with a dirty working tree
```

## Reading the data

Open the tunnel, then query with the read-only role:

```bash
ssh -f -N -L 25433:localhost:5432 do
psql "postgresql://analytics_ro@localhost:25433/analytics"
```

`scripts/stats_queries.sql` in this repo holds ready-made queries (traffic by
day, most-clicked targets, top pages, referrers, geography, entry and exit
pages). Run them with `\i scripts/stats_queries.sql` or paste individually.

## Local test

```bash
uv sync --extra stats
STATS_DATABASE_URL=postgresql://localhost/analytics STATS_IP_SALT=dev \
  uv run uvicorn moates_stats.app:app --port 8000
curl -s localhost:8000/health
curl -s -X POST localhost:8000/e -H 'Content-Type: application/json' \
  -d '{"sid":"3f2504e0-4f89-11d3-9a0c-0305e82c3301","ctx":{"land":"/"},"events":[{"k":"pageview","p":"/"}]}' -i
```

Without `STATS_DATABASE_URL` the service still starts and still answers 204; it
just discards everything. That is deliberate: a collector that refuses to boot
turns a database problem into a red deploy.

## Tuning (environment variables)

| Variable | Default | Purpose |
| --- | --- | --- |
| `STATS_DATABASE_URL` | *(unset)* | Postgres connection string; unset means discard |
| `STATS_IP_SALT` | *(unset)* | Salt for the daily IP hash; unset means store no hash |
| `STATS_ALLOWED_ORIGINS` | site apex + www | CORS allow-list |
| `STATS_MAX_EVENTS_PER_BATCH` | `50` | Events accepted per request |
| `STATS_MAX_STR` | `500` | Cap on stored string length |
| `STATS_MAX_META_KEYS` | `12` | Cap on `meta` keys per event |
| `STATS_PER_IP_PER_MINUTE` | `60` | Per-IP request burst limit |
| `STATS_PER_IP_EVENTS_PER_DAY` | `2000` | Per-IP daily event limit |
| `STATS_GLOBAL_EVENTS_PER_DAY` | `200000` | Global daily backstop |
| `STATS_POOL_MIN` / `STATS_POOL_MAX` | `1` / `3` | Connection pool size |

Rate limits are per process and reset on restart. They are a first line of
defence against one script filling the table, not a serious anti-abuse system;
the real backstop is that a dropped event costs nothing.

## Retention

Nothing prunes automatically. Portfolio traffic will take years to become
inconvenient, but if you want a cap, a monthly cron is enough:

```sql
DELETE FROM events   WHERE ts         < now() - interval '18 months';
DELETE FROM sessions WHERE last_seen  < now() - interval '18 months';
```
