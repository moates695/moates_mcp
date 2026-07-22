---
name: deploy
description: Deploy the moates-mcp MCP server to the production droplet (mcp.moates.com.au). Ships committed code, rebuilds the Docker image, recreates the container, and verifies the live endpoint. Use when the user asks to deploy, redeploy, ship, or push moates-mcp live.
allowed-tools: Bash
---

# Deploy moates-mcp

Deploy this repo to production. The droplet runs moates-mcp as a Docker container
(`moates-mcp-prod`) behind a dockerised nginx proxy on the shared
`backend-prod_api-network`; deployment is driven entirely by `deploy/deploy.sh`.

## Steps

1. **Sanity-check state first.** From the repo root, confirm what will ship:

   ```bash
   git -C /home/marcus/personal/moates_mcp status --short
   git -C /home/marcus/personal/moates_mcp log --oneline -1
   ```

   `deploy.sh` deploys **committed** `HEAD`. If there are uncommitted changes the
   user wants live, ask whether to commit first (preferred) or deploy with
   `--allow-dirty`. Do not commit on their behalf without asking.

2. **Run the deploy:**

   ```bash
   deploy/deploy.sh
   ```

   The script is self-verifying: it ships code over SSH (host alias `do`),
   rebuilds via `docker compose up -d --build`, then confirms the container is up
   and the public endpoint answers an MCP `initialize` + `tools/list`. It exits
   non-zero and prints an `error:` line on any failure.

3. **Report the outcome** to the user: the deployed short SHA, that the endpoint
   verified, and the tool count. If it failed, surface the `error:` line and the
   suggested `ssh do docker logs moates-mcp-prod` follow-up rather than retrying
   blindly.

## Notes

- Deploying is an outward-facing production change to a shared host (Gym Junkie's
  API and Redis run alongside it). The script touches only the moates-mcp
  container, but do not run it unless the user asked to deploy.
- Config can be overridden via env vars (`MOATES_MCP_SSH_HOST`,
  `MOATES_MCP_REMOTE_DIR`, `MOATES_MCP_URL`) — see `deploy/README.md`.
- This does **not** push to git. If `HEAD` isn't pushed, the script warns but
  still deploys local `HEAD`; remind the user to `git push` if they intended to.
