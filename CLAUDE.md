# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`moates-mcp` is a [Model Context Protocol](https://modelcontextprotocol.io) server that
serves accurate, structured facts about Marcus Oates (his resume, experience, projects,
skills). Any MCP client (Claude Desktop, Claude Code, an Agent SDK app) connects and calls
its tools; the *client* brings the LLM, this server just returns grounded data so the model
doesn't guess. The content mirrors https://moates.com.au.

## Commands

```bash
# Setup
uv venv --python 3.12
uv pip install -e ".[dev]"

# Run over stdio (quick local test / Claude Desktop config)
uv run moates-mcp

# Run over Streamable HTTP on 127.0.0.1:8000/mcp (add MCP_HOST=0.0.0.0 to bind all interfaces)
uv run python -m moates_mcp --http

# Tests
uv run pytest                                    # all
uv run pytest tests/test_server.py::test_search_finds_voice_ai   # a single test
```

`MCP_HOST` (default `127.0.0.1`) and `MCP_PORT` (default `8000`) configure the HTTP bind.

## Architecture

Three-file package under `src/moates_mcp/`, with a strict separation between data and serving:

- **`data.py`** — the single source of truth. Plain module-level constants (`PROFILE`,
  `EXPERIENCE`, `EDUCATION`, `SKILLS`, `PROJECTS`, `INTERESTS`, `BEYOND_WORK`, `STATUS_LABEL`)
  plus two pure helpers (`project_by_key`, `resume_markdown`). **All content edits happen
  here.** No MCP or server concerns leak into this file. Content mirrors the portfolio site
  (`~/personal/github_page`) and the resume PDF; keep Australian English, no em-dashes, no
  accented characters. Each project carries a `tagline`, high-level `tech` chips, optional
  `tech_detail`, and a `sections` list (`{title, summary, points[]}`) holding the deep
  per-feature / architecture detail that `get_project` and `search` surface.
- **`server.py`** — builds a single `FastMCP` instance and decorates thin wrapper functions
  (`@mcp.tool()`, `@mcp.resource(...)`, `@mcp.prompt()`) that read from `data.py`. The
  server holds no business logic beyond filtering/shaping what `data.py` provides.
- **`__main__.py` / `__init__.py`** — both re-export `server.main`, so `python -m moates_mcp`
  and the `moates-mcp` console script are equivalent entry points.

`main()` picks the transport from `argv`: `--http` → `streamable-http`, otherwise `stdio`.
The `FastMCP` instance is created with `stateless_http=True` and `json_response=True` —
each request is self-contained, which is what lets it sit behind nginx as a plain ASGI app.

### Key conventions

- **Tools are decorated functions but also plain callables.** Tests in `tests/test_server.py`
  import them directly (`from moates_mcp.server import search`) and call them — so tool
  bodies must stay side-effect-free and independently callable, not rely on MCP request
  context.
- **Project `status`** is one of `prod` / `test` / `poc`; `STATUS_LABEL` maps these to
  human-readable strings. `list_projects(status=...)` filters on the raw code.
- **`project_by_key`** matches on either the `key` or the `name` (case/space/hyphen
  insensitive), so `get_project` accepts `"gym_junkie"` or `"Gym Junkie"`.
- Tools return dicts/lists (structured) except `get_resume`/`resume_resource`, which return
  the rendered markdown string from `resume_markdown()`.

## Deployment

Deploys like any ASGI web app (see `deploy/`): runs on `127.0.0.1:8000` via the `Dockerfile`
or the `moates-mcp.service` systemd unit, fronted by nginx (`nginx.conf`) with a Let's
Encrypt cert on `443`, proxying to `/mcp` on `mcp.moates.com.au`. The nginx config disables
buffering and uses a long read timeout because Streamable HTTP may stream over SSE.
