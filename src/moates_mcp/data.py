"""Structured facts about Marcus Oates.

This is the single source of truth the MCP server exposes. It mirrors the
content on https://moates.com.au (about page, projects, contact) so an LLM
connected over MCP can answer questions accurately instead of guessing.
"""

from __future__ import annotations

PROFILE = {
    "name": "Marcus Oates",
    "title": "Senior Software Engineer, AI & Backend",
    "location": "Sydney, Australia",
    "summary": (
        "Senior software engineer focused on voice AI and the backend systems behind "
        "it, plus the apps, services and data around them. Currently the first employee "
        "at a voice AI startup, owning the core voice agent backend in production."
    ),
    "website": "https://moates.com.au",
    "contact": {
        "email": "marcusjoates@gmail.com",
        "work_email": "marcus@voxworks.ai",
        "phone": "+61 428 211 020",
        "github": "https://github.com/moates695",
        "linkedin": "https://www.linkedin.com/in/marcus-oates-52814a233/",
        "strava": "https://www.strava.com/athletes/46665081",
        "pypi": "https://pypi.org/user/moates/",
    },
}

EXPERIENCE = [
    {
        "role": "Senior Software Engineer, AI & Backend",
        "company": "Voxworks",
        "company_url": "https://voxworks.ai/",
        "dates": "Jan 2026 to present",
        "current": True,
        "summary": (
            "First employee at a voice AI startup, leading a ground-up restructure of the "
            "core voice agent backend and scaling call concurrency by 400%."
        ),
        "highlights": [
            "As the startup's first employee, took operational control of the voice agent's backend architecture and led a ground-up restructure of the codebase, the company's core product, owning its reliability and ongoing development in production",
            "Developed agentic AI development workflows and custom Model Context Protocol (MCP) tooling that dramatically accelerated development and enabled rapid prototyping, under heavy human oversight with disciplined review to keep code quality high",
            "Rebuilt the core conversation logic while maintaining interoperability with the existing live system, so clients continued to be served without interruption",
            "Extended reliable call handling from ~2-minute calls to consistently sustaining 10 to 20 minute conversations that stay on script and complete their objectives",
            "Increased call concurrency by 400% through system optimisations, managing concurrency and cost-effectiveness across the pipeline to balance throughput against infrastructure spend",
            "Architected the agent's conversational dynamics for a ~10% improvement in average response latency, prioritising accuracy so the agent does not stray from its call objectives",
            "Built automated testing for the voice system, from unit and integration tests to concurrent automated call runs, using AI agents to analyse call dynamics and debug conversational issues across a large sample space",
            "Established automated CI/CD deployment pipelines with real-time observability and monitoring in Grafana, giving instant visibility into call performance and system health",
            "Converted the voice agent to a chat agent while maintaining the core integrations, primarily used for client testing",
        ],
    },
    {
        "role": "Automation Software Engineer",
        "company": "Downer Group",
        "company_url": None,
        "dates": "May 2023 to Dec 2025",
        "current": False,
        "summary": (
            "Designed and shipped automation across cloud and on-prem systems, turning "
            "manual workflows into monitored, cost-efficient services."
        ),
        "highlights": [
            "Automated data extraction from spreadsheets using Azure Function Apps, stored in a database with a Power BI connection, saving ~$175k a year per business-unit implementation and eliminating manual transcription errors",
            "Created a custom internal Azure dashboard for monitoring project resources across subscriptions, with resource actions and deployment monitoring",
            "Reduced operating costs of Azure resources by ~60% by scheduling startup and shutdown events through a centralised tagging policy enacted via the dashboard",
            "Automated Konect API queries for critical field work, notifying the requisite authorities to consistently meet SLAs and avoid total penalties of ~$450k",
            "Enhanced security through daily storage account key rotation and SAS generation via Azure Key Vault, reducing 80-100 points of failure to a single centralised point",
            "Extracted text with OCR from CAD drawing PDFs and generated project report spreadsheets, a time saving of ~95%",
            "Wrote project setup shell scripts that deploy environments and resources in Azure, linked to custom GitHub branch environments with rules and protections to enable consistent IaC deployments using Bicep",
            "Implemented bespoke deep learning and computer vision solutions for real-time artefact recognition with ~94% accuracy",
        ],
    },
    {
        "role": "Engineering Intern",
        "company": "Incat Crowther",
        "company_url": None,
        "dates": "Feb 2023 to May 2023",
        "current": False,
        "summary": (
            "Produced technical drawings for double-hull commercial vessels (30-120 ft) "
            "with AutoCAD LT."
        ),
        "highlights": [
            "Produced accurate technical drawings with AutoCAD LT, focusing on double-hull commercial vessels of 30-120 ft",
            "Created and modified technical frame and construction drawings for 3 vessels",
            "Complied with relevant classing authorities' engineering standards so vessels were safe under varying oceanic conditions",
            "Produced precise cut-part, engine/rudder modification and machinery arrangement drawings within a dynamic environment",
        ],
    },
]

SKILLS = [
    {"group": "Languages", "items": ["Python", "TypeScript", "JavaScript", "SQL"]},
    {"group": "Frontend", "items": ["React", "React Native", "Expo", "Jotai", "MUI"]},
    {"group": "Backend", "items": ["Node / Express", "FastAPI", "WebSockets", "REST APIs"]},
    {"group": "Data", "items": ["Postgres", "Redis", "PowerBI", "Data analytics"]},
    {"group": "Cloud & DevOps", "items": ["Azure", "AWS", "Bicep (IaC)", "GitHub Actions", "Docker", "Cloudflare"]},
    {"group": "AI / LLMs", "items": ["Voice agents", "LLM fine-tuning", "Prompt engineering", "MCP tooling", "RAG", "LLM evals"]},
    {"group": "AI / ML", "items": ["Deep learning", "Computer vision", "OCR", "Applied ML"]},
]

INTERESTS = [
    "Strength training",
    "Ironman training",
    "Bouldering",
    "Mountain biking",
    "Tennis",
    "Ultimate frisbee",
    "Soccer",
    "Time outdoors",
]

BEYOND_WORK = (
    "Away from the keyboard I stay active and spend as much time outdoors as I can. I "
    "train regularly at the gym and am currently working towards an Ironman, and I like "
    "the mix of endurance and team sport, from bouldering and mountain biking with "
    "friends to tennis, ultimate frisbee and soccer. The same drive that keeps me "
    "chasing a hard problem at work is what keeps me chasing the next goal outside it."
)

# status: prod = in production, test = in testing, poc = proof of concept
PROJECTS = [
    {
        "key": "gym_junkie",
        "name": "Gym Junkie",
        "status": "prod",
        "blurb": "A free gym workout tracker with deep analytics, graphing and leaderboards.",
        "description": (
            "A free fitness app built by a backend engineer around data. Log sets fast, then "
            "dig into analytics, progressive-overload graphs, muscle heatmaps and leaderboards, "
            "with no subscription, no fluff. React Native front end, Express + Python services, "
            "Postgres and an ML layer behind it."
        ),
        "tech": ["Full stack", "React / TS", "Express", "Python", "Postgres", "AI / ML"],
        "links": {
            "Play Store": "https://play.google.com/store/apps/details?id=au.com.moates.gymjunkie&hl=en",
            "App Store": "https://apps.apple.com/au/app/gym-junkie/id6769685454",
        },
    },
    {
        "key": "woodchuck",
        "name": "Woodchuck",
        "status": "test",
        "blurb": "On-device scorer for the lawn game Finska (Molkky). No sign in, no backend, no tracking.",
        "description": (
            "A fully client-side mobile scorer for the lawn game Finska (Molkky). Download and "
            "go, with no sign in, no backend, no tracking. Handles teams, rotating throws, "
            "mid-game swaps and rule customisation, with save-and-continue snapshots."
        ),
        "tech": ["Client side", "Expo", "React / TS"],
        "links": {
            "Play Store": "https://play.google.com/store/apps/details?id=au.com.moates.woodchuck&hl=en",
        },
    },
    {
        "key": "poppycock",
        "name": "Poppycock",
        "status": "poc",
        "blurb": "Real-time companion app for the physical Balderdash card game.",
        "description": (
            "A real-time companion for the physical Balderdash card game. Host a room to run "
            "bluffs, voting and scoring while you play with the cards. Full-stack with FastAPI, "
            "WebSockets and Postgres."
        ),
        "tech": ["Full stack", "Expo", "React / TS", "Python", "FastAPI", "WebSocket", "Postgres"],
        "links": {"Source": "https://github.com/moates695/balderdash"},
    },
    {
        "key": "imax_bot",
        "name": "IMAX Watch Agent",
        "status": "test",
        "blurb": "Watches Event Cinemas IMAX Sydney and pings you on Telegram the moment films or tickets appear.",
        "description": (
            "A Python agent that scans Event Cinemas IMAX Sydney on a schedule and alerts you on "
            "Telegram when films appear, tickets open, or a watchlisted title becomes bookable, "
            "with a per-session seat breakdown and a daily digest. State lives in a local file so "
            "each alert fires once and never repeats; deployed as a plain cron job."
        ),
        "tech": ["Python", "Telegram", "Automation"],
        "links": {"Source": "https://github.com/moates695/imax_bot"},
    },
    {
        "key": "cellular_tracking",
        "name": "Cellular Tracking",
        "status": "prod",
        "blurb": "Computer-vision pipeline for segmenting, tracking and analysing cell division.",
        "description": (
            "A computer-vision project for segmenting cells, tracking their paths across frames "
            "and identifying divisions. Combines classical image analysis with deep learning."
        ),
        "tech": ["AI / ML", "Python"],
        "links": {"Source": "https://github.com/moates695/cs9517_Group_Project"},
    },
    {
        "key": "downer_helper",
        "name": "Downer Helper",
        "status": "prod",
        "blurb": "A PyPI package that wraps the Azure SDK to cut code repetition across projects.",
        "description": (
            "A published PyPI package wrapping common Azure SDK commands to reduce code "
            "replication and technical debt across projects. Deployed straight from GitHub and "
            "available for anyone to use."
        ),
        "tech": ["Python", "Package"],
        "links": {"PyPI": "https://pypi.org/project/downerhelper/"},
    },
    {
        "key": "postgres_deploy",
        "name": "Postgres Deploy",
        "status": "prod",
        "blurb": "A PyPI package that deploys and updates Postgres schemas from config files.",
        "description": (
            "A published PyPI package that deploys and updates Postgres schemas from a set of "
            "configuration files, making it easy to keep different database environments "
            "consistent."
        ),
        "tech": ["Python", "Package"],
        "links": {"PyPI": "https://pypi.org/project/postgresdeploy/"},
    },
]

STATUS_LABEL = {"prod": "In production", "test": "In testing", "poc": "Proof of concept"}


def project_by_key(key: str) -> dict | None:
    key = key.strip().lower().replace("-", "_").replace(" ", "_")
    for project in PROJECTS:
        if project["key"] == key or project["name"].lower().replace(" ", "_") == key:
            return project
    return None


def resume_markdown() -> str:
    """Render the full profile as a single plain-text/markdown resume."""
    lines: list[str] = []
    p = PROFILE
    lines.append(f"# {p['name']}")
    lines.append(f"{p['title']} - {p['location']}")
    lines.append("")
    lines.append(p["summary"])
    lines.append("")
    c = p["contact"]
    lines.append("## Contact")
    lines.append(f"- Email: {c['email']}")
    lines.append(f"- Website: {p['website']}")
    lines.append(f"- GitHub: {c['github']}")
    lines.append(f"- LinkedIn: {c['linkedin']}")
    lines.append("")
    lines.append("## Experience")
    for exp in EXPERIENCE:
        lines.append(f"### {exp['role']} - {exp['company']} ({exp['dates']})")
        lines.append(exp["summary"])
        for h in exp["highlights"]:
            lines.append(f"- {h}")
        lines.append("")
    lines.append("## Skills & tools")
    for s in SKILLS:
        lines.append(f"- {s['group']}: {', '.join(s['items'])}")
    lines.append("")
    lines.append("## Projects")
    for proj in PROJECTS:
        lines.append(f"### {proj['name']} ({STATUS_LABEL[proj['status']]})")
        lines.append(proj["description"])
        lines.append(f"Tech: {', '.join(proj['tech'])}")
        lines.append("")
    lines.append("## Beyond work")
    lines.append(BEYOND_WORK)
    return "\n".join(lines).strip() + "\n"
