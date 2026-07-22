#!/usr/bin/env bash
#
# Deploy moates-mcp to the production droplet.
#
# What it does, end to end:
#   1. Ships the current committed code (git HEAD) to the droplet build context.
#   2. Rebuilds the Docker image and recreates the container via docker compose.
#   3. Verifies the container is up and the live public endpoint serves the new code.
#
# The droplet runs moates-mcp as a Docker container (moates-mcp-prod) behind a
# dockerised nginx reverse proxy (nginx-proxy-prod) on the shared
# backend-prod_api-network. There is no git checkout or systemd service there;
# this script is the single source of truth for deploying.
#
# Usage:
#   deploy/deploy.sh              # deploy committed HEAD
#   deploy/deploy.sh --allow-dirty  # deploy even if the working tree is dirty
#
# Config (override via env):
#   MOATES_MCP_SSH_HOST    ssh host/alias for the droplet   (default: do)
#   MOATES_MCP_REMOTE_DIR  build context on the droplet      (default: /opt/moates_mcp)
#   MOATES_MCP_URL         public endpoint to verify         (default: https://mcp.moates.com.au/mcp)

set -euo pipefail

SSH_HOST="${MOATES_MCP_SSH_HOST:-do}"
REMOTE_DIR="${MOATES_MCP_REMOTE_DIR:-/opt/moates_mcp}"
PUBLIC_URL="${MOATES_MCP_URL:-https://mcp.moates.com.au/mcp}"
CONTAINER="moates-mcp-prod"

ALLOW_DIRTY=0
[[ "${1:-}" == "--allow-dirty" ]] && ALLOW_DIRTY=1

# Always operate from the repo root (the dir above this script).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

log()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; exit 1; }

# --- Preflight -------------------------------------------------------------
command -v git >/dev/null || die "git not found"
git rev-parse --git-dir >/dev/null 2>&1 || die "not inside the moates_mcp git repo"

REV="$(git rev-parse --short HEAD)"

if [[ -n "$(git status --porcelain)" ]]; then
  if [[ "$ALLOW_DIRTY" -eq 1 ]]; then
    log "working tree is dirty; deploying committed HEAD ($REV) anyway (--allow-dirty)"
  else
    die "working tree has uncommitted changes. Commit them, or pass --allow-dirty to deploy HEAD ($REV) regardless."
  fi
fi

if git rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
  AHEAD="$(git rev-list --count '@{upstream}..HEAD')"
  [[ "$AHEAD" -gt 0 ]] && log "note: HEAD is $AHEAD commit(s) ahead of upstream (not pushed). Deploying local HEAD ($REV)."
fi

log "Deploying $REV to $SSH_HOST:$REMOTE_DIR"

# --- 1. Ship committed code -----------------------------------------------
log "Shipping committed tree to build context"
git archive --format=tar HEAD \
  | ssh "$SSH_HOST" "tar -x -C '$REMOTE_DIR' && chown -R 1000:1000 '$REMOTE_DIR'"
ok "code shipped"

# --- 2. Build + recreate via compose --------------------------------------
log "Rebuilding image and recreating container"
# On first migration the container may exist from an old `docker run` (no compose
# labels). Remove it so compose can take ownership cleanly; if already
# compose-managed, leave it for compose to recreate.
ssh "$SSH_HOST" bash -s "$REMOTE_DIR" "$CONTAINER" <<'REMOTE'
set -euo pipefail
REMOTE_DIR="$1"; CONTAINER="$2"
if docker inspect "$CONTAINER" >/dev/null 2>&1; then
  proj="$(docker inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' "$CONTAINER" 2>/dev/null || true)"
  if [[ -z "$proj" ]]; then
    echo "  removing unmanaged container $CONTAINER (one-time migration to compose)"
    docker rm -f "$CONTAINER" >/dev/null
  fi
fi
cd "$REMOTE_DIR/deploy"
docker compose up -d --build
docker image prune -f >/dev/null 2>&1 || true
REMOTE
ok "container recreated"

# --- 3. Verify ------------------------------------------------------------
log "Verifying container health on the droplet"
sleep 2
ssh "$SSH_HOST" "docker ps --filter name=$CONTAINER --format '  {{.Names}} {{.Status}} {{.Image}}'" \
  | grep -q "Up" || die "container is not running; check: ssh $SSH_HOST docker logs $CONTAINER"
ok "container is up"

log "Verifying live endpoint ($PUBLIC_URL)"
# Poll: nginx/uvicorn may take a moment to accept connections after recreate.
attempt=0
until [[ "$attempt" -ge 10 ]]; do
  resp="$(curl -s --max-time 10 \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -X POST "$PUBLIC_URL" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"deploy-verify","version":"1.0"}}}' \
    2>/dev/null || true)"
  if grep -q '"serverInfo"' <<<"$resp"; then
    ok "initialize handshake OK"
    break
  fi
  attempt=$((attempt + 1))
  sleep 2
done
[[ "$attempt" -ge 10 ]] && die "endpoint did not respond to initialize after recreate"

tools="$(curl -s --max-time 10 \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -X POST "$PUBLIC_URL" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' 2>/dev/null || true)"
tool_count="$(grep -o '"name":' <<<"$tools" | wc -l | tr -d ' ')"
ok "tools/list served ($tool_count tools)"

printf '\033[1;32m\n✓ Deployed %s to %s\033[0m\n' "$REV" "$PUBLIC_URL"
