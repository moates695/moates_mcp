# moates web chat proxy: deployment

A thin FastAPI service (`moates_chat.app`) that answers visitor questions about
Marcus on https://moates.com.au. It reuses the same knowledge base as the MCP
server (`moates_mcp.data`), stuffs it into a scoped system prompt, and calls a
cheap LLM once per question. No tool calls, no MCP round-trips.

It runs as a Docker container (`moates-chat-prod`) on the shared
`backend-prod_api-network`, alongside `moates-mcp-prod`.

## One-time setup on the droplet

1. **Create the build context and secrets dir**

   ```bash
   ssh do 'mkdir -p /opt/moates_chat/deploy/chat'
   ```

2. **Add the OpenAI key** (never committed, never shipped by the deploy script):

   ```bash
   ssh do 'cat > /opt/moates_chat/deploy/chat/.env' <<'EOF'
   OPENAI_API_KEY=sk-...your-key...
   # Optional overrides:
   # CHAT_MODEL=gpt-5-nano
   # CHAT_ALLOWED_ORIGINS=https://moates.com.au,https://www.moates.com.au
   EOF
   ```

3. **DNS**: add a `chat.moates.com.au` record in Cloudflare pointing at the
   droplet (proxied, like the other subdomains).

4. **Reverse-proxy vhost.** Public subdomains are fronted by a single dockerised
   proxy, `nginx-proxy-prod` (nginx:alpine on `backend-prod_api-network`,
   publishing 80/443). It renders its config from a mounted template via the
   image's envsubst step (`NGINX_ENVSUBST_FILTER=^API_PORT$`, so only
   `${API_PORT}` is substituted and all `$host`/`$proxy_*` nginx vars survive).
   A single wildcard Cloudflare origin cert
   (`/root/gym_junkie_server/nginx/ssl/cloudflare-cert.pem`) covers every
   `*.moates.com.au` subdomain. So `deploy/chat/nginx.conf` is only a bare-metal
   reference — the live setup is the shared template, not per-site files.

   Append a `chat` vhost to that template, mirroring the existing `mcp` block
   (80→443 redirect + a 443 server block that proxies to the container by name).
   Use a runtime resolver so nginx still starts if the chat service is down:

   ```nginx
   server {
       listen 80;
       server_name chat.moates.com.au;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl;
       http2 on;
       server_name chat.moates.com.au;

       ssl_certificate     /etc/nginx/ssl/cloudflare-cert.pem;
       ssl_certificate_key /etc/nginx/ssl/cloudflare-key.pem;

       location / {
           resolver 127.0.0.11 valid=30s;               # Docker embedded DNS
           set $chat_upstream http://moates-chat-prod:8000;
           proxy_pass $chat_upstream;

           # Every request past here costs money. The zone and the $client_key
           # map (which reads CF-Connecting-IP, since Cloudflare fronts this)
           # are declared once at the top of the template.
           limit_req zone=chat_zone burst=5 nodelay;

           proxy_http_version 1.1;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header Connection "";
           proxy_read_timeout 65s;
       }
   }
   ```

   Back up the template first, then **validate the render in a throwaway
   container on the shared network** (so load-time upstreams like `api` resolve)
   before touching the live proxy:

   ```bash
   TPL=/root/gym_junkie_server/nginx/nginx.conf.template
   ssh do "cp $TPL $TPL.bak-chat"
   # ...append the block above to $TPL...
   ssh do 'docker run --rm --network backend-prod_api-network \
     -e NGINX_ENVSUBST_FILTER="^API_PORT$" -e API_PORT=8000 \
     -v /root/gym_junkie_server/nginx/nginx.conf.template:/etc/nginx/templates/nginx.conf.template:ro \
     -v /root/gym_junkie_server/nginx/ssl:/etc/nginx/ssl:ro \
     nginx:alpine nginx -t'
   ```

   Only once `nginx -t` reports **syntax is ok** / **test is successful**, apply
   it by restarting the proxy (a plain reload will *not* re-render the template):

   ```bash
   ssh do 'docker restart nginx-proxy-prod'
   ```

   This is a ~1-2s blip for every site behind the proxy (chat, mcp, gymjunkie),
   so it is validated-then-restart, never restart-and-hope. Roll back with
   `cp $TPL.bak-chat $TPL && docker restart nginx-proxy-prod`.

5. **Set a spend cap (the real money guardrail).** In the OpenAI dashboard,
   create a dedicated project/key for this service and set a **monthly budget
   limit** (e.g. USD $2). The in-app rate limits are only a first line of
   defence and reset when the container restarts; the dashboard budget is the
   hard cap.

## Deploy

From a clone of this repo (not on the droplet):

```bash
deploy/deploy_chat.sh                # deploy committed HEAD
deploy/deploy_chat.sh --allow-dirty  # deploy with a dirty working tree
```

The script ships committed code, rebuilds the image, recreates the container,
and verifies `https://chat.moates.com.au/health`.

## Local test

```bash
uv sync --extra chat
OPENAI_API_KEY=sk-... uv run uvicorn moates_chat.app:app --port 8000
curl -s localhost:8000/health
curl -s -X POST localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What projects has Marcus built?"}'
```

## Tuning (environment variables)

| Variable | Default | Purpose |
| --- | --- | --- |
| `CHAT_MODEL` | `gpt-5-nano` | LLM model id |
| `CHAT_REASONING_EFFORT` | `minimal` | GPT-5 reasoning effort |
| `CHAT_MAX_OUTPUT_TOKENS` | `600` | Cap on answer length |
| `CHAT_MAX_MESSAGE_CHARS` | `500` | Cap on incoming question length |
| `CHAT_PER_IP_PER_MINUTE` | `8` | Per-IP burst limit |
| `CHAT_PER_IP_PER_DAY` | `80` | Per-IP daily limit |
| `CHAT_GLOBAL_PER_DAY` | `1500` | Global daily backstop |
| `CHAT_PER_IP_TOKENS_PER_DAY` | `150000` | Per-IP daily token budget (~20 questions) |
| `CHAT_GLOBAL_TOKENS_PER_DAY` | `3000000` | Global daily token budget |
| `CHAT_ASSUMED_TOKENS_PER_CALL` | `9000` | Charged when the provider reports no usage |
| `CHAT_ALLOWED_ORIGINS` | site apex + www | CORS allow-list |

Request counts and token budgets are both enforced; whichever runs out first
stops the conversation. Counts guard against hammering, tokens against spend:
the whole knowledge base rides along as the system prompt, so every question
costs roughly the same ~8k input tokens whatever its length.
