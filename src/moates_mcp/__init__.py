"""moates_mcp: an MCP server that answers questions about Marcus Oates."""

__all__ = ["main"]


def __getattr__(name: str):
    """Import the server on first use rather than at package import time.

    The chat proxy imports `moates_mcp.data` for the knowledge base and never
    touches the MCP SDK, but importing the package used to pull server.py in and
    the SDK with it, so an SDK release that moved FastMCP took the chat
    container down over an import it does not use.
    """
    if name == "main":
        from .server import main

        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
