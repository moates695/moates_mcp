# Deploying moates-mcp

Production runs on a DigitalOcean droplet as a **Docker container**, fronted by a
dockerised nginx reverse proxy. There is no git checkout and no systemd service
on the droplet: this repo is the single source of truth, and `deploy.sh` pushes
it out.

## One-command deploy

From a clone of this repo:

```bash
deploy/deploy.sh
```

That will:

1. Ship the current committed code (`git HEAD`) to the droplet build context
   (`/opt/moates_mcp`) over SSH.
2. Rebuild the image and recreate the container with
   `docker compose up -d --build` (see [`docker-compose.yml`](docker-compose.yml)).
3. Verify the container is up and the live endpoint
   (`https://mcp.moates.com.au/mcp`) answers an MCP `initialize` handshake and
   serves `tools/list`.

The script deploys **committed** code. Use `deploy/deploy.sh --allow-dirty` to
deploy `HEAD` with an uncommitted working tree.

There is a Claude Code skill wrapping this: run `/deploy` (or ask Claude to
"deploy moates-mcp").

### Config

Override via environment variables:

| Variable | Default | Meaning |
| --- | --- | --- |
| `MOATES_MCP_SSH_HOST` | `do` | SSH host/alias for the droplet |
| `MOATES_MCP_REMOTE_DIR` | `/opt/moates_mcp` | Build context on the droplet |
| `MOATES_MCP_URL` | `https://mcp.moates.com.au/mcp` | Endpoint to verify |

## How it fits together on the droplet

```
Cloudflare ──▶ nginx-proxy-prod (docker, :80/:443)
                    │  server_name mcp.moates.com.au
                    ▼  proxy_pass http://moates-mcp-prod:8000
              moates-mcp-prod (this project)
                    on network backend-prod_api-network
```

- The container joins the **external** `backend-prod_api-network` (created by the
  `gym_junkie_server` compose project) so nginx can reach it by container name.
- It publishes **no host port**; only nginx talks to it, over the docker network.
- `container_name: moates-mcp-prod` is fixed because the nginx config routes to
  that exact name (`set $mcp_upstream http://moates-mcp-prod:8000;`).

## Files here

- **`docker-compose.yml`** — the canonical, declarative container definition.
- **`deploy.sh`** — the deploy driver (ship → build → verify).
- **`nginx.conf`** — reference for the reverse-proxy vhost (the live config lives
  in the `nginx-proxy-prod` container).
- **`moates-mcp.service`** — unused reference for a no-Docker systemd deploy.
