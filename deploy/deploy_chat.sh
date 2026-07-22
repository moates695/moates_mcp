#!/usr/bin/env bash
#
# Deploy the moates web chat proxy to the production droplet.
#
# What it does, end to end:
#   1. Ships the current committed code (git HEAD) to the droplet build context.
#   2. Rebuilds the Docker image and recreates the container via docker compose.
#   3. Verifies the container is up and the live /health endpoint responds.
#
# The chat proxy runs as a Docker container (moates-chat-prod) behind the shared
# nginx reverse proxy on backend-prod_api-network, exactly like moates-mcp.
#
# One-time setup on the droplet (see deploy/chat/README.md):
#   - Create $REMOTE_DIR and drop a deploy/chat/.env there with OPENAI_API_KEY.
#   - Point chat.moates.com.au DNS at the droplet and wire the nginx vhost + TLS.
#   - Set a monthly spend cap on the OpenAI account (the real money guardrail).
#
# Usage:
#   deploy/deploy_chat.sh                 # deploy committed HEAD
#   deploy/deploy_chat.sh --allow-dirty   # deploy even if the working tree is dirty
#
# Config (override via env):
#   MOATES_CHAT_SSH_HOST    ssh host/alias for the droplet   (default: do)
#   MOATES_CHAT_REMOTE_DIR  build context on the droplet      (default: /opt/moates_chat)
#   MOATES_CHAT_URL         public endpoint to verify         (default: https://chat.moates.com.au/health)

set -euo pipefail

SSH_HOST="${MOATES_CHAT_SSH_HOST:-do}"
REMOTE_DIR="${MOATES_CHAT_REMOTE_DIR:-/opt/moates_chat}"
PUBLIC_URL="${MOATES_CHAT_URL:-https://chat.moates.com.au/health}"
CONTAINER="moates-chat-prod"

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

log "Deploying $REV to $SSH_HOST:$REMOTE_DIR"

# --- 1. Ship committed code -----------------------------------------------
# The remote dir and deploy/chat/.env (secrets) must already exist; we never
# ship the key. Fail early with a clear message if setup was skipped.
log "Checking remote setup"
ssh "$SSH_HOST" "test -f '$REMOTE_DIR/deploy/chat/.env'" \
  || die "missing $REMOTE_DIR/deploy/chat/.env on $SSH_HOST (see deploy/chat/README.md)"

log "Shipping committed tree to build context"
git archive --format=tar HEAD \
  | ssh "$SSH_HOST" "tar -x --exclude='deploy/chat/.env' -C '$REMOTE_DIR' && chown -R 1000:1000 '$REMOTE_DIR'"
ok "code shipped"

# --- 2. Build + recreate via compose --------------------------------------
log "Rebuilding image and recreating container"
ssh "$SSH_HOST" bash -s "$REMOTE_DIR" <<'REMOTE'
set -euo pipefail
REMOTE_DIR="$1"
cd "$REMOTE_DIR/deploy/chat"
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
attempt=0
until [[ "$attempt" -ge 10 ]]; do
  resp="$(curl -s --max-time 10 "$PUBLIC_URL" 2>/dev/null || true)"
  if grep -q '"status"' <<<"$resp"; then
    ok "health endpoint OK"
    break
  fi
  attempt=$((attempt + 1))
  sleep 2
done
[[ "$attempt" -ge 10 ]] && die "endpoint did not respond to /health after recreate"

printf '\033[1;32m\n✓ Deployed %s to %s\033[0m\n' "$REV" "$PUBLIC_URL"
