# Deep Research Agent

**An open-source, human-in-the-loop, multi-agent research platform built with LangGraph, FastAPI, PostgreSQL, and Next.js.**

Deep Research Agent turns a research question into an organized investigation. It generates specialist analyst profiles, requests human approval, conducts evidence-backed web research, synthesizes findings, and produces a source-linked Markdown report in a private web workspace.

> **Project status:** Actively developed. The application has been demonstrated locally with completed research reports. Review generated findings and citations independently before relying on them for consequential decisions.

## Highlights

- **Multi-agent orchestration:** LangGraph coordinates analyst generation, interviews, research sections, and final synthesis.
- **Human-in-the-loop review:** Approve or provide feedback on proposed research analysts before investigations continue.
- **Evidence-backed research:** Tavily-powered web discovery, URL validation, source collection, and deduplication.
- **Structured reports:** Introduction, findings, conclusion, and a reference list, with Markdown export.
- **Durable execution:** PostgreSQL-backed research runs and checkpointing enable progress tracking and workflow recovery.
- **Research dashboard:** Next.js interface for creating projects, reviewing analysts, monitoring events, exploring the library, and reading reports.
- **Private workspace:** Admin authentication and a server-side proxy for backend access.
- **Developer tooling:** `uv`, Ruff, pytest, Docker Compose, and Alembic migrations.

## Technology stack

| Layer | Technologies |
| --- | --- |
| Agent orchestration | Python, LangGraph, LangChain |
| Research and retrieval | Tavily Search API |
| LLM integration | Configurable chat-model factory |
| Backend API | FastAPI |
| Persistence and checkpoints | PostgreSQL, SQLAlchemy, psycopg, LangGraph checkpointing |
| Database migrations | Alembic |
| Background processing | Python research worker |
| Frontend | Next.js, React, TypeScript |
| Tooling | uv, pytest, Ruff, Docker Compose |

## How it works

```text
Research question
      |
      v
Generate specialist analysts
      |
      v
Human review / approval
      |
      v
Parallel analyst interviews
      |
      +--> Web search --> Evidence validation --> Source collection
      |
      v
Evidence-backed research sections
      |
      v
Final report synthesis
      |
      v
Report validation and PostgreSQL persistence
      |
      v
Research dashboard and Markdown export
```

## Repository structure

```text
deep-research-agent/
├── src/research_assistant/
│   ├── agents/                # Analyst, interview, research, and report graphs
│   ├── api/                   # FastAPI endpoints
│   ├── core/                  # Configuration and core exceptions
│   ├── guardrails/            # URL and output validation
│   ├── infrastructure/        # Database, worker, and LLM integrations
│   ├── orchestration/         # End-to-end LangGraph workflow
│   ├── prompts/               # Agent prompt templates
│   ├── schemas/               # Shared typed data models
│   ├── services/              # Application services
│   └── tools/                 # Web search integrations
├── frontend/
│   ├── app/                   # Next.js routes and server handlers
│   ├── components/            # UI components
│   └── lib/                   # Frontend utilities
├── migrations/                # Database migrations
├── scripts/                   # Worker and maintenance scripts
├── tests/                     # Unit and integration tests
├── docs/                      # Additional documentation
├── .env.example               # Backend environment template
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── langgraph.json
├── pyproject.toml
├── uv.lock
└── README.md
```

## Prerequisites

- **Python 3.12** (the version used in local development)
- [uv](https://docs.astral.sh/uv/) for Python dependencies
- **Node.js and npm** compatible with `frontend/package.json`
- **Docker Desktop** (or an existing compatible PostgreSQL instance)
- API credentials for the LLM provider configured in the backend and for [Tavily](https://tavily.com/)

## Getting started

Run these commands from the **`deep-research-agent` directory that contains `src/`, `frontend/`, and the backend `pyproject.toml`**.

### 1. Clone and install backend dependencies

```powershell
git clone <YOUR-REPOSITORY-URL>
cd deep-research-agent
uv sync
```

### 2. Configure backend environment

```powershell
Copy-Item .env.example .env
```

Edit `.env` and supply the required values documented in `.env.example`, including your Tavily API key, the configured LLM provider credentials, and the PostgreSQL connection settings. **Never commit real secrets.**

### 3. Start PostgreSQL and apply migrations

```powershell
docker compose up -d
uv run alembic upgrade head
```

Confirm the database host, port, username, password, and database name agree with your `.env` and `docker-compose.yml`. Local development has used PostgreSQL exposed on host port `5433`; use your actual configuration.

### 4. Start the API

In a new terminal at the repository root:

```powershell
uv run uvicorn research_assistant.api.main:app --reload --port 8000
```

API: `http://localhost:8000` · Interactive API documentation (if enabled): `http://localhost:8000/docs`.

### 5. Start the research worker

In a separate root-level terminal:

```powershell
uv run python scripts/run_worker.py
```

The worker processes research jobs and persists completed reports. Leave it running while testing research projects.

### 6. Configure and start the frontend

In another terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Set the keys requested by `frontend/.env.example`, including the private workspace credentials, session secret, backend URL, and backend access key as applicable. The frontend runs at **http://localhost:3000** by default.

### 7. Run a research project

1. Sign in to the private research workspace.
2. Create a new project and enter a research question.
3. Select the analyst count and interview depth.
4. Review and approve the generated analysts.
5. Monitor progress, inspect evidence, and open the completed report.
6. Export the Markdown report if needed.

## Tests and code quality

From the backend project root:

```powershell
uv run ruff format --check src tests
uv run ruff check src tests
uv run pytest -q
```

To format code locally:

```powershell
uv run ruff format src tests
```

The latest reported local suite completed with **25 passed and 2 skipped**. This is a local development result, not a continuous-integration guarantee.

## Configuration and security

- Keep `.env` and `frontend/.env.local` **out of version control**.
- Publish only placeholder templates such as `.env.example` and `frontend/.env.example`.
- Do not expose backend API keys, Tavily keys, LLM credentials, or session secrets to browser-side code.
- Change default/example credentials before any deployment.
- Use HTTPS, secure cookies, strong secrets, access controls, logging, and production-grade secret management when deploying beyond localhost.
- Treat retrieved web pages as untrusted evidence; verify important claims and their citations.
- Review generated reports for factual errors, source quality, and unsupported claims.

## Current capabilities and limitations

The application supports research creation, analyst review, web retrieval, structured report generation, persisted project records, and Markdown export. Quality depends on search availability, model behavior, source validity, and deployment configuration. Generated citations should be checked against original sources. Production readiness, scalability, and third-party service limits have not been independently audited.

## Roadmap

Potential future improvements include automated citation-to-claim verification, stronger source-quality ranking, additional export formats, automated deployment/CI checks, comprehensive database integration tests, observability dashboards, and expanded authentication and team collaboration.

## Contributing

Contributions, issue reports, documentation improvements, and constructive reviews are welcome.

1. Open an issue to discuss substantial changes.
2. Create a feature branch from the default branch.
3. Add focused tests for bug fixes and new behavior.
4. Run Ruff and pytest before opening a pull request.
5. Document new configuration options without including credentials.

Please follow any repository-specific contribution or conduct policies once those files are added.

## License

**License selection pending.** To make the repository explicitly open source, add a root-level `LICENSE` file with an OSI-approved license (for example, MIT or Apache-2.0) and update this section to identify the chosen license. Public visibility alone does not grant an open-source license.

## Suggested repository topics

`langgraph` · `deep-research` · `ai-agents` · `multi-agent-systems` · `agentic-ai` · `generative-ai` · `human-in-the-loop` · `research-automation` · `fastapi` · `nextjs` · `postgresql` · `tavily` · `python` · `typescript` · `open-source`

---

Built to make AI-assisted research more structured, traceable, and reviewable.
