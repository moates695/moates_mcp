"""Structured facts about Marcus Oates.

This is the single source of truth the MCP server exposes. It mirrors the
content on https://moates.com.au (about, projects, education, contact) and his
resume so an LLM connected over MCP can answer questions accurately instead of
guessing.

Conventions (kept in sync with the portfolio site):
- Australian English spelling.
- No em-dashes in prose; use commas, colons, "to", or hyphens.
- No accented characters (e.g. "Molkky", "resume").
"""

from __future__ import annotations

PROFILE = {
    "name": "Marcus Oates",
    "title": "Senior Software Engineer, AI & Backend",
    "location": "Sydney, Australia",
    "summary": (
        "Senior software engineer focused on voice AI and the backend systems behind "
        "it, plus the apps, services and data around them. Currently the first employee "
        "at a voice AI startup, owning the core voice agent backend in production. "
        "UNSW dual-degree graduate (Bachelor of Engineering with First Class Honours / "
        "Computer Science majoring in Artificial Intelligence) and creator of Gym Junkie, "
        "a fitness tracking app live on the Google Play Store and Apple App Store."
    ),
    "elevator_pitch": (
        "Full stack engineer specialising in automation using AI and ML processes. I "
        "deliver scalable solutions for stakeholders, using agentic workflows to "
        "accelerate development."
    ),
    "philosophy": (
        "Build systems that are reliable, observable and easy to evolve. Solve real "
        "problems through clean abstractions and a focus on long-term maintainability."
    ),
    "website": "https://moates.com.au",
    "contact": {
        "email": "marcusjoates@gmail.com",
        "work_email": "marcus@voxworks.ai",
        "gym_junkie_support": "gymtrackeraus@gmail.com",
        "phone": "+61 428 211 020",
        "phone_note": "I don't pick up unknown numbers, so please leave a message.",
        "abn": "50261161443",
        "github": "https://github.com/moates695",
        "linkedin": "https://www.linkedin.com/in/marcus-oates-52814a233/",
        "strava": "https://www.strava.com/athletes/46665081",
        "expo": "https://expo.dev/accounts/moates",
        "pypi": "https://pypi.org/user/moates/",
        "discord": "https://discord.gg/uUd8hJNvzM",
        "paypal": "https://paypal.me/moates695",
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
            "Spearheaded Infrastructure as Code adoption across the team using GitHub Actions and Bicep",
        ],
    },
    {
        "role": "Engineering Intern",
        "company": "Incat Crowther",
        "company_url": None,
        "dates": "Feb 2023 to May 2023",
        "current": False,
        "summary": (
            "Short-term consultancy internship in naval engineering and architecture, "
            "producing technical drawings for double-hull commercial vessels (30-120 ft) "
            "with AutoCAD LT."
        ),
        "highlights": [
            "Produced accurate technical drawings with AutoCAD LT, focusing on double-hull commercial vessels of 30-120 ft",
            "Created and modified technical frame and construction drawings for 3 vessels, quickly learning how boats are constructed and outfitted for service",
            "Complied with relevant classing authorities' engineering standards so vessels were safe to operate under varying oceanic conditions",
            "Produced precise cut-part, engine and rudder modification, and machinery arrangement drawings for clients within a dynamic environment",
        ],
    },
]

EDUCATION = [
    {
        "qualification": (
            "Bachelor of Engineering (First Class Honours) / Computer Science "
            "(Artificial Intelligence)"
        ),
        "institution": "UNSW Sydney",
        "dates": "2019 to 2023",
        "result": "First Class Honours. Honours WAM 84 (13 High Distinctions, 7 Distinctions).",
        "highlights": [
            "Dual degree pairing an engineering (honours) program with a computer science major in artificial intelligence",
            "Notable marks: MTRN2500 Computing for Mechatronics = 98, COMP3311 Database Systems = 97, COMP3121 Algorithms and Programming Techniques = 96, MMAN3200 Linear Systems and Control = 95",
        ],
    },
    {
        "qualification": "Higher School Certificate",
        "institution": "St Augustine's College, Sydney",
        "dates": "2018",
        "result": "ATAR 97.30.",
        "highlights": [
            "Aggregate Cup recipient (2018)",
            "Stan Arneil Memorial Award recipient (2017)",
            "First XI Football team (2018)",
        ],
    },
]

SKILLS = [
    {
        "group": "Languages",
        "items": [
            "Python", "TypeScript", "JavaScript", "Java", "C", "C++",
            "SQL", "PL/pgSQL", "MATLAB", "Shell", "HTML", "CSS",
        ],
    },
    {
        "group": "Frontend & Mobile",
        "items": ["React (TS)", "React Native (TS)", "Expo", "Jotai", "MUI"],
    },
    {
        "group": "Backend",
        "items": ["Node / Express", "FastAPI", "WebSockets", "REST APIs", "psycopg2", "asyncpg"],
    },
    {
        "group": "Data",
        "items": ["Postgres", "Redis", "PowerBI", "Data analytics", "Vector search / RAG"],
    },
    {
        "group": "AI / LLMs",
        "items": [
            "Conversational voice agents", "LLM fine-tuning",
            "Prompt engineering (frontier & open-source models)",
            "OpenAI", "Anthropic", "Groq",
            "Deepgram (speech-to-text)", "Cartesia (text-to-speech)",
            "RAG with vector search", "Custom MCP servers",
            "LLM evaluation pipelines", "Automated testing at scale",
        ],
    },
    {
        "group": "AI coding agents",
        "items": ["Claude Code", "Codex", "OpenCode", "Agentic development workflows"],
    },
    {
        "group": "AI / ML (Python)",
        "items": [
            "TensorFlow", "OpenCV", "scikit-learn", "pandas", "Pillow",
            "Deep learning", "Computer vision", "OCR", "Applied ML",
        ],
    },
    {
        "group": "Azure",
        "items": [
            "Function Apps (standard & durable)", "Container Registry", "Container Instances",
            "Managed Identity", "Key Vault", "Storage Accounts (+ queues)", "Event Grid",
            "Postgres", "Logic Apps", "SharePoint automation",
            "VM deployment & monitoring", "Containerised Streamlit apps",
        ],
    },
    {
        "group": "AWS",
        "items": [
            "ECS", "Lambda (zip/containerised)", "NLB", "ElastiCache (Redis)",
            "RDS Postgres", "Secrets Manager", "CloudFormation", "aws CLI",
        ],
    },
    {
        "group": "DevOps",
        "items": ["Bicep (IaC)", "GitHub Actions", "Docker", "Cloudflare", "az / aws CLI"],
    },
    {
        "group": "Engineering & CAD",
        "items": ["SolidWorks", "AutoCAD LT", "Rhino"],
    },
]

INTERESTS = [
    "Triathlon / Ironman training",
    "Strength training",
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
    "chasing a hard problem at work is what keeps me chasing the next goal outside it. "
    "My triathlon and gym training also feeds directly into Gym Junkie, the fitness app "
    "I built and use myself."
)

# status: prod = in production, test = in testing, poc = proof of concept
PROJECTS = [
    {
        "key": "gym_junkie",
        "name": "Gym Junkie",
        "status": "prod",
        "blurb": "A free gym workout tracker with deep analytics, graphing and leaderboards.",
        "tagline": (
            "A free fitness app built on data, analytics and tracking. Record every set "
            "for progressive overload, then dig into the numbers, without paying yet "
            "another subscription."
        ),
        "description": (
            "A free fitness app built by a backend engineer around data. Log sets fast, then "
            "dig into analytics, progressive-overload graphs, muscle heatmaps and leaderboards, "
            "with no subscription, no fluff. React Native (Expo) front end, Python (FastAPI) and "
            "Express services, Postgres and Redis, with an ML layer behind it. Live on the "
            "Google Play Store and Apple App Store (Android and iOS)."
        ),
        "tech": ["Full stack", "React / TS", "Express", "Python", "Postgres", "AI / ML"],
        "tech_detail": (
            "React Native (Expo) frontend with a FastAPI (Python) backend on Postgres and "
            "Redis, plus Express services and an ML layer. Lightweight frontend focused on "
            "more functionality than existing paid apps."
        ),
        "links": {
            "Play Store": "https://play.google.com/store/apps/details?id=au.com.moates.gymjunkie&hl=en",
            "App Store": "https://apps.apple.com/au/app/gym-junkie/id6769685454",
            "Support email": "gymtrackeraus@gmail.com",
        },
        "sections": [
            {
                "title": "Why I built it",
                "summary": (
                    "Built by a backend engineer around data. In a workout I want to enter "
                    "data quickly, or pull up comparisons and analytics, without hunting "
                    "through menus. Whether you are an ego lifter or a science-based bro, "
                    "this app should have something for you."
                ),
                "points": [
                    "Fast set, rep and weight entry built for logging mid-workout with no fuss",
                    "Rich analytics and comparisons without pressing through a stack of menus",
                    "Free to use, with features and customisation usually locked behind a subscription",
                    "Friends without the noise: check in on your mates, but keep the focus on you",
                ],
            },
            {
                "title": "Workout logging",
                "summary": "Fast set entry that stays out of your way so you can focus on the lift.",
                "points": [
                    "A keyboard tuned for sets, reps and weight, with sensible defaults pulled from your last session, so you usually only tap once or twice per set",
                    "Mark a set as a drop set, or jump back to a previous set to fix a typo",
                    "A notes button on each exercise card title for quick reminders",
                    "Edit exercise controls: rearrange the order of exercises, copy an exercise, or delete one outright",
                    "Autosave and sync: drafts autosave continuously and sync to the cloud, so if your phone dies or you close the app you pick up right where you left off on any device",
                ],
            },
            {
                "title": "Exercise library",
                "summary": "A large catalogue covering every major muscle group, with the lifts you actually train floating to the top.",
                "points": [
                    "Filter by equipment, target muscle or movement pattern to narrow the catalogue fast",
                    "The picker remembers what you usually do, so your regular exercises float to the top",
                    "Mark exercises as favourites to pin your bread-and-butter lifts one tap away",
                    "Create a custom exercise from scratch: name it, tag the muscles it works, and it slots into your library alongside the built-ins",
                    "Create variations of existing exercises (e.g. incline DB press, neutral grip) without polluting the catalogue",
                ],
            },
            {
                "title": "Rest timer and heart rate",
                "summary": "Keep your rest honest and see exactly how hard you pushed each session.",
                "points": [
                    "A built-in rest timer that kicks off automatically when you log a set, floats above your workout, and can be dismissed or adjusted any time",
                    "Bluetooth heart-rate monitor support: pair a strap once in settings and your live heart rate shows up during the workout",
                    "Samples are stored against the workout, so you can look back at how hard you actually pushed",
                    "The app remembers your device and reconnects on its own when you start your next workout",
                ],
            },
            {
                "title": "Muscle targets",
                "summary": "Turn vague intentions (hit chest twice this week) into something you can actually track.",
                "points": [
                    "Pick a muscle group, choose what you are targeting (sets, total volume or total reps), then set the number and window (e.g. ten sets of back over a rolling seven days)",
                    "Every target shows up on the home screen as a progress card that fills as you log sets through the week",
                    "Run as many targets in parallel as you like: a high priority on legs, a maintenance target for arms, a don't-forget target for rear delts",
                ],
            },
            {
                "title": "Muscle heatmap",
                "summary": "The fastest way to spot a training gap before it becomes an imbalance.",
                "points": [
                    "A body diagram coloured by how recently and how heavily each muscle has been worked; bright muscles are fresh, faded ones are falling behind",
                    "A frequency view on the home screen shows training counts per muscle group over your chosen window, from the past 7 to 14 days or however long your rotation runs",
                    "Tune the colour scale and time window to match your split, whether push-pull-legs or more ad-hoc",
                ],
            },
            {
                "title": "Exercise stats",
                "summary": "Pick any lift and see its full history, personal records and progression at a glance.",
                "points": [
                    "A complete history of every set you have logged (weights, reps, dates), sortable however you like",
                    "N-rep max view: your best set at 1, 3, 5, 8, 10, 12 and 15 reps",
                    "Estimated maxes for rep ranges you do not directly train, handy for percentage-based programs",
                    "Progression charts plotting weight, volume or estimated 1RM over time",
                    "Live PR flags: hit a new personal record mid-workout and Gym Junkie flags it on the spot",
                ],
            },
            {
                "title": "Distributions and ratios",
                "summary": "Where is your training time actually going? A radar chart makes muscle-group balance instantly obvious.",
                "points": [
                    "A radar chart of your training split across muscle groups, so a neglected back is obvious next to well-worked chest and shoulders",
                    "Switch the metric between total volume, working sets and total reps to see the split from different angles",
                    "Volume biases towards heavier compounds, set count rewards spread, and rep count surfaces high-rep accessory work; use it before a deload or to keep yourself honest",
                ],
            },
            {
                "title": "History and calendar",
                "summary": "Every session you have ever logged, kept in one honest record of your consistency.",
                "points": [
                    "Tap any past session for the full breakdown: exercises, sets, weights, notes, muscle groups, duration and heart rate if you wore a strap",
                    "A yearly frequency calendar paints every training day green, with the shade scaling to how hard the session was",
                    "Copy an old workout as a template for today, or compare last month's performance against right now",
                ],
            },
            {
                "title": "Friends and leaderboards",
                "summary": "See what your gym mates are training and where you stack up, without the social-network noise.",
                "points": [
                    "Add gym mates and see their workouts in a feed: what they trained, how heavy and how long it took",
                    "Tap into a friend's profile to compare directly, same exercise and same rep range, side by side",
                    "Leaderboards let you pick a lift and rep range and see where you rank; filter by age bracket, body weight or experience for a fairer comparison",
                    "No likes, no comments and no streaks guilting you into pretending you trained",
                ],
            },
            {
                "title": "Strava sharing",
                "summary": "Push completed workouts straight to your Strava feed, formatted as a proper strength session.",
                "points": [
                    "Connect Strava once from settings and the integration handles the OAuth flow for you",
                    "A Share to Strava option appears whenever you wrap up a workout",
                    "Shared activities include the workout summary (exercises, total volume, duration and heart-rate data), formatted for Strava rather than dumped as raw data",
                    "Sharing is opt-in per workout: bad session, don't share it; hit a PR, one tap",
                ],
            },
        ],
    },
    {
        "key": "woodchuck",
        "name": "Woodchuck",
        "status": "test",
        "blurb": "On-device scorer for the lawn game Finska (Molkky). No sign in, no backend, no tracking.",
        "tagline": (
            "A download-and-go mobile scorer for Finska. Throw the log, tap the pins you "
            "knocked over, and land on exactly 50."
        ),
        "description": (
            "A fully client-side mobile scorer for the lawn game Finska (Molkky). Download and "
            "go, with no sign in, no backend, no tracking. Handles teams, rotating throws, "
            "mid-game swaps and rule customisation, with save-and-continue snapshots. Built "
            "with Expo / React Native, the whole game is one XState v5 state machine with pure "
            "game logic and centralised validation."
        ),
        "tech": ["Client side", "Expo", "React / TS"],
        "tech_detail": (
            "Expo / React Native app that runs entirely on-device. The full game (participants, "
            "scores, turn order, rules) is a single XState v5 machine; everything around it is a "
            "pure function, a validator, or a dumb component that reads state and dispatches "
            "events. Theme lives outside the machine as two Jotai atoms. ~130 jest cases across "
            "three suites."
        ),
        "links": {
            "Play Store": "https://play.google.com/store/apps/details?id=au.com.moates.woodchuck&hl=en",
            "Source": "https://github.com/moates695/finska",
        },
        "sections": [
            {
                "title": "The idea",
                "summary": (
                    "When the sun is out, Finska (a.k.a. Molkky) is the family game of choice: "
                    "knock over numbered pins to reach exactly 50. Easy to play, awkward to "
                    "score once the included cards run out and the notes app takes over, so I "
                    "built Woodchuck to do the counting."
                ),
                "points": [
                    "On-device only: no sign in, no backend, no tracking",
                    "Players or teams, with rotating member throws",
                    "Tap the pins you knocked over instead of counting yourself",
                    "Tweak target score, reset score, miss limit and more in settings",
                    "Light, dark and sand themes",
                    "Auto-saves after every throw so you can pick up where you left off",
                ],
            },
            {
                "title": "Architecture",
                "summary": "One XState v5 machine owns the game; pure helpers and one validation module do everything else.",
                "points": [
                    "State machine: a single machine owns the full game context and decides which screen renders, so there is no navigation library (idle to setup to playing to settings)",
                    "The snapshot is persisted to AsyncStorage on every transition and restored on launch, so the user chooses to continue or start fresh",
                    "Guards (hasEnoughParticipants, isWinningScore, removalInvalidates, and so on) defer all branching to pure helpers, so the machine never inlines game rules",
                    "Pure game logic in game_logic.ts (submitTurn, missTurn, editScore, cycleStanding, swapTeamMember) returns partial context updates fed into assign actions, and is trivially unit-testable",
                    "Centralised validation exposes every predicate (isNameTaken, validateNewPlayer, validateNewTeam, validateRules, isGameValid, canWinThisTurn), reused by components and machine guards alike",
                ],
            },
            {
                "title": "Gameplay screens",
                "summary": "Idle, setup and a three-part play screen: scoreboard, up-next card and pin-map score input.",
                "points": [
                    "Setup: add players and teams with case-insensitive name collision checks; teams can start with a single member so people can join part-way through; continue is enabled only once isGameValid passes",
                    "Scoreboard: participants ordered by descending score then alphabetically; a white divider marks who could win next throw, a red divider marks the eliminated; edit mode allows direct score and miss-count fixes",
                    "Up-next card: shows whose turn it is and who is on deck; for teams the throwing member rotates and can be swapped with a long-press; tap to open the full upcoming queue",
                    "Score input (pin map): tap the pins you hit and the score computes live in the corner; the X button registers a miss and ticks the player closer to elimination",
                ],
            },
            {
                "title": "Rules and settings",
                "summary": "Every rule from the validator is exposed in settings, with a confirm step if a change would invalidate the game in progress.",
                "points": [
                    "Target score (default 50), reset score for overshoots (can be negative), miss count before elimination",
                    "Elimination reset score, elimination turns (null for permanent, otherwise sit out N turns and re-enter)",
                    "Skip counts as miss, and use pin value (multi-pin hits sum pin values instead of counting pins)",
                    "Theme toggle between light, dark and sand at the top of settings",
                ],
            },
            {
                "title": "Testing",
                "summary": "Three jest suites run without a device (AsyncStorage and expo-crypto mocked).",
                "points": [
                    "game_logic.test.ts: pure function coverage of every rule branch (~130 cases)",
                    "validation.test.ts: predicate coverage including empty names and duplicate teams",
                    "machine.test.ts: XState transition coverage using object syntax for nested state matches",
                ],
            },
        ],
    },
    {
        "key": "poppycock",
        "name": "Poppycock",
        "status": "poc",
        "blurb": "Real-time companion app for the physical Balderdash card game.",
        "tagline": (
            "A real-time companion for the physical Balderdash card game. The cards still "
            "drive the prompts; the app handles the fiddly bits the score pad and slips of "
            "paper used to."
        ),
        "description": (
            "A real-time companion for the physical Balderdash card game. The dasher reads a "
            "card and types the real answer, everyone else submits a bluff from their phone, "
            "and the app shuffles them, runs the vote anonymously, and tallies score deltas at "
            "the end of the round. Split across two repos sharing one hand-mirrored protocol: a "
            "FastAPI backend and an Expo / React Native client, live over WebSocket. Early "
            "proof of concept, playable end to end but not yet published to an app store."
        ),
        "tech": ["Full stack", "Expo", "React / TS", "Python", "FastAPI", "WebSocket", "Postgres"],
        "links": {"Source": "https://github.com/moates695/balderdash"},
        "sections": [
            {
                "title": "How it plays",
                "summary": "Create a room, share the code, and play with a rotating dasher each round.",
                "points": [
                    "Create a room and share the code with the people around the table",
                    "Rotating dasher each round, with the host controlling game flow",
                    "Real-time updates over WebSocket",
                    "Persistent scores so the same group can keep playing across nights",
                ],
            },
            {
                "title": "Backend: a single uvicorn process",
                "summary": "One process, layered into transport, dispatch and domain so each concern stays isolated and testable.",
                "points": [
                    "Transport: REST endpoints for room create and join, plus a /ws/{room}/{player} WebSocket for live play",
                    "Dispatch: switches on message type, validates with pydantic, and enforces host, dasher and phase authorisation",
                    "Domain: a RoomManager owns the in-memory rooms dict and is the only thing that talks to Postgres",
                    "Pure helpers like shuffle_answers and compute_score_deltas live at module level, so they are trivially testable in isolation",
                ],
            },
            {
                "title": "Persistence",
                "summary": "Postgres stores the durable shell; active round state lives only in memory.",
                "points": [
                    "Postgres stores rooms, players, scores, dasher order, round metadata, submissions, votes and score deltas",
                    "Active round state (real answer, fake answers, shuffled list, votes, score deltas) lives only in memory on the Round dataclass",
                    "A restart mid-round leaves that round unrecoverable, so the host starts a new one; hydration only rebuilds the shell",
                ],
            },
            {
                "title": "Round phases",
                "summary": "Three phases per round.",
                "points": [
                    "collecting: only the dasher submits the real answer; only non-dashers submit fakes",
                    "voting: answers are shuffled and sent without attribution",
                    "scored: attribution is revealed alongside score deltas",
                ],
            },
            {
                "title": "Mobile client",
                "summary": "Three logical screens swapped by a single conditional in App.tsx based on room code and round phase.",
                "points": [
                    "HomeScreen: create or join a room",
                    "LobbyScreen: roster, host controls and optional dasher rotation",
                    "GameScreen: phase-driven internally for collecting, voting and scored",
                    "GameProvider uses a useReducer-based context; useGameSocket owns the WebSocket lifecycle and reconnect; protocol.ts is a hand-mirrored copy of the backend pydantic models",
                ],
            },
        ],
    },
    {
        "key": "imax_bot",
        "name": "IMAX Watch Agent",
        "status": "test",
        "blurb": "Watches Event Cinemas IMAX Sydney and pings you on Telegram the moment films or tickets appear.",
        "tagline": (
            "A Python agent that watches Event Cinemas IMAX Sydney and pings you on Telegram "
            "when films appear or tickets open, so you never miss a release or an on-sale window."
        ),
        "description": (
            "A Python agent that scans Event Cinemas IMAX Sydney on a schedule and alerts you on "
            "Telegram when films appear, tickets open, or a watchlisted title becomes bookable, "
            "with a per-session seat breakdown and a daily digest. Stateless per invocation: it "
            "reads its config, scans once, diffs against saved state and fires only on "
            "transitions. State lives in a local file so each alert fires once and never "
            "repeats; deployed as a plain cron job on a droplet."
        ),
        "tech": ["Python", "Telegram", "Automation"],
        "links": {"Source": "https://github.com/moates695/imax_bot"},
        "sections": [
            {
                "title": "What it watches",
                "summary": "A single run drives four independent alert streams. Watchlist alerts replace plain discovery ones for tracked films.",
                "points": [
                    "Coming-soon discovery: a new film appears on the IMAX Sydney coming-soon list",
                    "On-sale discovery: any film site-wide gains bookable sessions",
                    "Watchlist: a highlighted alert when a tracked film first shows as coming-soon, then a per-session Standard / Full Recliner seat breakdown the moment it is bookable",
                    "Daily digest: once a day (08:00 Sydney by default), the full coming-soon and on-sale lists",
                ],
            },
            {
                "title": "How it works",
                "summary": "Stateless per invocation: scan once, diff against saved state, fire only on transitions.",
                "points": [
                    "One run does a single site scan and drives all four streams",
                    "The first run seeds state silently, so there is no alert burst on setup",
                    "Every run after that only messages you on a genuine change",
                    "State lives in a local agent_state.json, so each alert fires once per transition and never repeats",
                    "Title matching is case, punctuation and accent insensitive, so 'dune part two' matches 'Dune: Part Two'",
                ],
            },
            {
                "title": "Deploy",
                "summary": "Each run is self-contained, so deployment is just a cron job on a droplet.",
                "points": [
                    "No runner and no state-commit dance; runs every 15 minutes",
                    "A flock guard stops a slow scan overlapping the next tick",
                    "uv provisions the Python 3.12 toolchain from a lockfile",
                ],
            },
        ],
    },
    {
        "key": "cellular_tracking",
        "name": "Cellular Tracking",
        "status": "prod",
        "blurb": "Computer-vision pipeline for segmenting, tracking and analysing cell division.",
        "tagline": (
            "A UNSW COMP9517 (Computer Vision) group project: segmenting cells and tracking "
            "their position, size and divisions across four provided microscopy sequences."
        ),
        "description": (
            "A computer-vision project for segmenting cells, tracking their paths across frames "
            "and identifying divisions, across four provided microscopy sequences. Combines "
            "classical image analysis with custom methods rather than transfer learning: as a "
            "computer vision course the mark would have been capped at a distinction if existing "
            "neural networks were used, so the solution uses custom methods throughout. Built on "
            "the usual Python ML libraries (OpenCV, scikit-image, matplotlib, SciPy) plus custom "
            "functions tailored to the problem."
        ),
        "tech": ["AI / ML", "Python"],
        "links": {"Source": "https://github.com/moates695/cs9517_Group_Project"},
        "sections": [
            {
                "title": "Segmenting (step one)",
                "summary": "Separate the cells from the background frame by frame.",
                "points": [
                    "Apply CLAHE (Contrast Limited Adaptive Histogram Equalisation) preprocessing",
                    "Calculate a 257-bin histogram, then iterate to find an intensity threshold where the histogram stops decreasing consistently, and scale it to the final pixel threshold",
                    "Create a binary mask above the threshold and apply a morphological open with a 5x5 rectangular kernel to remove noise",
                    "Flush cells touching the image border to prevent erosion from the frame edge",
                    "Apply watershed to separate touching cells, open each cell in its own image space, label the cells, and delete tiny out-of-focus 'cells'",
                ],
            },
            {
                "title": "Tracking (step two)",
                "summary": "Track the segmented, labelled cells across a sequence.",
                "points": [
                    "Compute centroids for the first frame, then initialise global labels, frame-specific centroid labels and per-frame displacement",
                    "For each frame, compute centroids and the distance matrix between consecutive frames",
                    "Match centroids with nearest neighbour within a threshold (cells may appear mid-sequence) and assign global labels so each cell is tracked between frames",
                    "Detect cells in the process of splitting and label these events, including in previous frames",
                    "Filter out small, short-lived cells as noise, then outline each cell by label colour, highlight splits in white, and draw trajectories",
                ],
            },
            {
                "title": "Improvements (reflection)",
                "summary": "With hindsight, what I would change.",
                "points": [
                    "Use curvature-based overlap detection instead of separation filtering methods",
                    "For cells that flash in and out between frames, use a predictive trajectory model to link them across non-consecutive frames",
                    "Run a secondary, more aggressive segmentation around flashing cells to locate the faint ones",
                ],
            },
        ],
    },
    {
        "key": "downer_helper",
        "name": "Downer Helper",
        "status": "prod",
        "blurb": "A PyPI package that wraps the Azure SDK to cut code repetition across projects.",
        "tagline": (
            "A Python package that bundles the common wrapper functions I kept copy and "
            "pasting between projects: logging, Key Vault secrets, GIS, SharePoint and Logic Apps."
        ),
        "description": (
            "A published PyPI package wrapping common Azure SDK commands to reduce code "
            "replication and technical debt across projects. Having a single source of truth "
            "for shared logic means it can be updated or improved once, then deployed "
            "automatically with GitHub Actions. Deployed straight from GitHub and available for "
            "anyone to use."
        ),
        "tech": ["Python", "Package"],
        "links": {"PyPI": "https://pypi.org/project/downerhelper/"},
        "sections": [
            {
                "title": "Logging",
                "summary": "Postgres log queue and a scheduled log check.",
                "points": [
                    "PostgresLogQueue: a psycopg2 handler that enters logs directly to Postgres, creating the table if needed and grouping by job_id; logs queue and dump on save (INFO, DEBUG, WARN, ERROR), with an optional print_logs=True",
                    "Quick setup pulls the DB config from Azure Key Vault (format: dbname,user,password,host); manual setup takes a config dictionary",
                    "Log check: reviews logs from the past interval_hours and emails recipients for any non-INFO levels, via a logic app key/url",
                ],
            },
            {
                "title": "Key Vault secrets",
                "summary": "Helpers for reading secrets, DB config and logic-app key/url combinations.",
                "points": [
                    "get_secret_value, get_config_dict (dbname,user,password,host), get_key_url (key/url combo in one request), form_connection_string, get_secret_json, db_connect (returns psycopg2 connection and cursor)",
                ],
            },
            {
                "title": "GIS (ArcGIS)",
                "summary": "Token auth plus feature-service and attachment operations.",
                "points": [
                    "get_access_token (60-minute expiry), query_feature_service (with optional add_where clause), query_attachments, get_attachment, update_feature_service, timestamp_to_datetime (with pytz timezone)",
                ],
            },
            {
                "title": "SharePoint",
                "summary": "Read and write SharePoint lists, mapping ArcGIS records to list items.",
                "points": [
                    "get_list (items as dicts keyed by data labels), form_list_item (maps SharePoint labels to ArcGIS attributes), create_list_item (via a logic-app key/url), upload_attachments, get_list_attachments",
                ],
            },
            {
                "title": "Logic App (email)",
                "summary": "Send Outlook email through a logic app.",
                "points": [
                    "send_email (recipients/cc/bcc as ';'-delimited strings or lists, attachments as {Name, ContentBytes}) and send_error_email (function/project title in the header)",
                ],
            },
        ],
    },
    {
        "key": "postgres_deploy",
        "name": "Postgres Deploy",
        "status": "prod",
        "blurb": "A PyPI package that deploys and updates Postgres schemas from config files.",
        "tagline": (
            "A Python package that simplifies deploying Postgres schemas. Point it at a folder "
            "and it deploys or updates the schema in the target database, or mirrors an "
            "existing database back into files."
        ),
        "description": (
            "A published PyPI package that deploys and updates Postgres schemas from a set of "
            "configuration files, making it easy to keep different database environments "
            "consistent. Wired into pipelines, a developer works in dev and updates the schema "
            "files locally, then pushing to test or prod automatically updates the Postgres "
            "schema to match, avoiding the classic 'forgot to add a column in the new "
            "environment' bug. Currently on its first release and actively in progress."
        ),
        "tech": ["Python", "Package"],
        "links": {"PyPI": "https://pypi.org/project/postgresdeploy/"},
        "sections": [
            {
                "title": "Target folder structure",
                "summary": "Functions, views, materialized views and triggers are SQL files, organised by schema.",
                "points": [
                    "sql/<schema>/functions/<name>.sql, materialized_views/<name>.sql, triggers/<name>.sql, views/<name>.sql",
                    "Tables live under tables/<name>.json",
                ],
            },
            {
                "title": "Table definitions",
                "summary": "Tables are described with JSON capturing columns, constraints and indexes.",
                "points": [
                    "Columns: name, type, not_null, default, type_convert_using",
                    "Constraints: primary_key, foreign_key, check (name + condition), unique (name + columns)",
                    "Indexes: name + columns",
                ],
            },
            {
                "title": "Usage",
                "summary": "Invoke a deployment from a pipeline action.",
                "points": [
                    "Import deploy from postgresdeploy, fetch a DB config secret (integrates with downerhelper.secrets), build Postgres creds, and call deploy('sql', pg_creds)",
                ],
            },
        ],
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
    lines.append(f"- Work email: {c['work_email']}")
    lines.append(f"- Phone: {c['phone']}")
    lines.append(f"- Website: {p['website']}")
    lines.append(f"- GitHub: {c['github']}")
    lines.append(f"- LinkedIn: {c['linkedin']}")
    lines.append(f"- Strava: {c['strava']}")
    lines.append(f"- PyPI: {c['pypi']}")
    lines.append("")
    lines.append("## Experience")
    for exp in EXPERIENCE:
        lines.append(f"### {exp['role']} - {exp['company']} ({exp['dates']})")
        lines.append(exp["summary"])
        for h in exp["highlights"]:
            lines.append(f"- {h}")
        lines.append("")
    lines.append("## Education")
    for ed in EDUCATION:
        lines.append(f"### {ed['qualification']} - {ed['institution']} ({ed['dates']})")
        lines.append(ed["result"])
        for h in ed["highlights"]:
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
        for section in proj.get("sections", []):
            lines.append(f"- {section['title']}: {section.get('summary', '')}".rstrip())
            for point in section.get("points", []):
                lines.append(f"  - {point}")
        lines.append("")
    lines.append("## Beyond work")
    lines.append(BEYOND_WORK)
    lines.append("")
    lines.append(f"Interests: {', '.join(INTERESTS)}.")
    return "\n".join(lines).strip() + "\n"
