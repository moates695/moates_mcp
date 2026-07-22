"""Public web chat proxy for moates.com.au.

A thin FastAPI service that answers visitor questions about Marcus Oates. It
reuses the same knowledge base as the MCP server (moates_mcp.data), but instead
of exposing tools it stuffs the whole (small, static) profile into a scoped
system prompt and asks a cheap LLM once per question. This keeps cost, latency
and the "only talk about Marcus" behaviour all in the good place.

Run locally:  uvicorn moates_chat.app:app --port 8000
"""
