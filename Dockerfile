FROM python:3.12-slim

# uv for fast, reproducible installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src

RUN uv pip install --system --no-cache .

ENV MCP_HOST=0.0.0.0 \
    MCP_PORT=8000
EXPOSE 8000

# Streamable HTTP transport, listening on all interfaces inside the container.
CMD ["python", "-m", "moates_mcp", "--http"]
