"""MCP server exposing facts about Marcus Oates.

Any MCP client (Claude Desktop, Claude Code, an Agent SDK app, etc.) can connect
over Streamable HTTP and use these tools to answer questions about Marcus. The
connecting client provides the LLM; this server just serves accurate, structured
data so the model does not have to guess.

Run locally:      python -m moates_mcp            (stdio, for a quick local test)
Run over HTTP:    python -m moates_mcp --http     (Streamable HTTP, for the droplet)
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from . import data

HOST = os.environ.get("MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("MCP_PORT", "8000"))

INSTRUCTIONS = (
    "This server answers questions about Marcus Oates, a Sydney-based senior software "
    "engineer specialising in voice AI and backend systems. Use get_profile for an "
    "overview, list_projects/get_project for his work (get_project returns rich "
    "per-project detail: features, architecture and how each project works), "
    "get_experience for his career history, get_education for his qualifications, "
    "get_skills for his tech stack, get_interests for hobbies, and get_resume for "
    "everything in one document. search does a keyword lookup across all of it. Only "
    "answer from the data these tools return; do not invent details."
)

# stateless_http keeps each request self-contained, which is the right fit for a
# public, read-only endpoint sitting behind nginx on a droplet.
mcp = FastMCP(
    "Marcus Oates",
    instructions=INSTRUCTIONS,
    host=HOST,
    port=PORT,
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def get_profile() -> dict:
    """Get a high-level overview of Marcus: name, title, location, summary and contact links."""
    return data.PROFILE


@mcp.tool()
def list_projects(status: str | None = None) -> list[dict]:
    """List Marcus's projects.

    Args:
        status: Optional filter. One of "prod" (in production), "test" (in testing),
            or "poc" (proof of concept). Omit to list every project.
    """
    projects = data.PROJECTS
    if status:
        wanted = status.strip().lower()
        projects = [p for p in projects if p["status"] == wanted]
    return [
        {
            "key": p["key"],
            "name": p["name"],
            "status": p["status"],
            "status_label": data.STATUS_LABEL[p["status"]],
            "blurb": p["blurb"],
            "tech": p["tech"],
        }
        for p in projects
    ]


@mcp.tool()
def get_project(key: str) -> dict:
    """Get full detail for a single project by its key or name (e.g. "gym_junkie" or "Gym Junkie")."""
    project = data.project_by_key(key)
    if project is None:
        available = ", ".join(p["key"] for p in data.PROJECTS)
        return {"error": f"No project matching '{key}'. Available keys: {available}"}
    return {**project, "status_label": data.STATUS_LABEL[project["status"]]}


@mcp.tool()
def get_experience() -> list[dict]:
    """Get Marcus's work history: roles, companies, dates and detailed highlights."""
    return data.EXPERIENCE


@mcp.tool()
def get_education() -> list[dict]:
    """Get Marcus's education: degrees, institutions, dates, results and highlights."""
    return data.EDUCATION


@mcp.tool()
def get_skills() -> list[dict]:
    """Get Marcus's technical skills and tools, grouped by category."""
    return data.SKILLS


@mcp.tool()
def get_interests() -> dict:
    """Get what Marcus does outside of work (sport, training, hobbies)."""
    return {"summary": data.BEYOND_WORK, "interests": data.INTERESTS}


@mcp.tool()
def get_resume() -> str:
    """Get Marcus's complete resume as a single markdown document (profile, experience, skills, projects)."""
    return data.resume_markdown()


@mcp.tool()
def search(query: str) -> list[dict]:
    """Keyword-search everything about Marcus (experience, projects, skills).

    Returns matching snippets with a source label so the model can cite where a fact came from.
    """
    q = query.strip().lower()
    if not q:
        return []
    hits: list[dict] = []

    for exp in data.EXPERIENCE:
        haystack = " ".join([exp["role"], exp["company"], exp["summary"], *exp["highlights"]]).lower()
        if q in haystack:
            hits.append({
                "source": f"experience:{exp['company']}",
                "text": f"{exp['role']} at {exp['company']} ({exp['dates']}): {exp['summary']}",
            })

    for ed in data.EDUCATION:
        haystack = " ".join([ed["qualification"], ed["institution"], ed["result"], *ed["highlights"]]).lower()
        if q in haystack:
            hits.append({
                "source": f"education:{ed['institution']}",
                "text": f"{ed['qualification']}, {ed['institution']} ({ed['dates']}): {ed['result']}",
            })

    for proj in data.PROJECTS:
        section_text = " ".join(
            " ".join([s.get("title", ""), s.get("summary", ""), *s.get("points", [])])
            for s in proj.get("sections", [])
        )
        haystack = " ".join(
            [proj["name"], proj["blurb"], proj["description"], proj.get("tagline", ""), section_text, *proj["tech"]]
        ).lower()
        if q in haystack:
            hits.append({
                "source": f"project:{proj['key']}",
                "text": f"{proj['name']}: {proj['description']}",
            })

    for group in data.SKILLS:
        if q in group["group"].lower() or any(q in item.lower() for item in group["items"]):
            hits.append({
                "source": f"skills:{group['group']}",
                "text": f"{group['group']}: {', '.join(group['items'])}",
            })

    return hits or [{"source": "none", "text": f"No matches for '{query}'."}]


@mcp.resource("resume://marcus")
def resume_resource() -> str:
    """Marcus's full resume as a readable document."""
    return data.resume_markdown()


@mcp.prompt()
def ask_about_marcus(question: str) -> str:
    """Starter prompt for asking a question about Marcus, grounded in this server's tools."""
    return (
        "You are answering questions about Marcus Oates using the tools provided by this "
        "MCP server. Call the relevant tools (get_profile, get_experience, get_education, "
        "list_projects, get_project, get_skills, get_interests, get_resume, search) and "
        "answer only from what they return. "
        f"If something is not covered, say so.\n\nQuestion: {question}"
    )


def main() -> None:
    import sys

    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
