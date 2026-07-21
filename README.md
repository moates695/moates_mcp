# moates-mcp

An [MCP](https://modelcontextprotocol.io) server that answers questions about
**Marcus Oates**, a Sydney-based senior software engineer (voice AI & backend).

It's a proof of concept: any MCP client (Claude Desktop, Claude Code, an Agent
SDK app) connects to the server and uses its tools to answer questions about
Marcus. The client brings the LLM; this server just serves accurate, structured
data (mirrored from https://moates.com.au) so the model doesn't have to guess.

## Tools

| Tool | Returns |
| --- | --- |
| `get_profile` | Name, title, location, summary, contact links |
| `list_projects(status?)` | Projects, optionally filtered by `prod` / `test` / `poc` |
| `get_project(key)` | Full detail for one project |
| `get_experience` | Work history with detailed highlights |
| `get_skills` | Tech stack, grouped |
| `get_interests` | Life outside work |
| `get_resume` | The whole profile as one markdown document |
| `search(query)` | Keyword search across experience, projects and skills |

Also exposes a `resume://marcus` resource and an `ask_about_marcus` prompt.

## Run locally

```bash
uv venv --python 3.12
uv pip install -e ".[dev]"

# stdio (quick local test, e.g. from Claude Desktop config)
uv run moates-mcp

# Streamable HTTP on 127.0.0.1:8000/mcp
MCP_HOST=0.0.0.0 uv run python -m moates_mcp --http
```

Run the tests with `uv run pytest`.

## Connect a client

**Claude Code** (HTTP):

```bash
claude mcp add --transport http marcus https://mcp.moates.com.au/mcp
```

**Claude Desktop** (stdio) — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "marcus": { "command": "uv", "args": ["run", "moates-mcp"], "cwd": "/path/to/moates_mcp" }
  }
}
```

## Deploy to a DigitalOcean droplet

The server speaks MCP's Streamable HTTP transport, so it deploys like any ASGI
web app. See [`deploy/`](deploy/) for a Dockerfile, an nginx reverse-proxy
config, and a systemd unit. In short:

1. Point a subdomain (`mcp.moates.com.au`) at the droplet.
2. Run the container (or the systemd service) listening on `127.0.0.1:8000`.
3. Front it with nginx + a Let's Encrypt cert on `443`, proxying to `/mcp`.

Clients then connect to `https://mcp.moates.com.au/mcp`.
