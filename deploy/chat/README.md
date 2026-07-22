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

3. **DNS + TLS**: point `chat.moates.com.au` at the droplet, then wire the nginx
   vhost to `moates-chat-prod:8000` the same way `mcp.moates.com.au` was set up
   (see `deploy/chat/nginx.conf` for the bare-metal reference).

4. **Set a spend cap (the real money guardrail).** In the OpenAI dashboard,
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
| `CHAT_ALLOWED_ORIGINS` | site apex + www | CORS allow-list |
