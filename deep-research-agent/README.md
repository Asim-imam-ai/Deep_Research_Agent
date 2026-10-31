# Deep Research Agent · Deep Research Studio

**An AI-powered, human-supervised research platform built with LangGraph, FastAPI, PostgreSQL and Next.js.**

The repository contains a durable multi-agent backend **and a fully integrated web interface**. It orchestrates specialist analysts, evidence gathering and interviews, supports human approval before research proceeds, and stores structured research reports.

## Highlights

- **LangGraph workflows:** analyst generation, pause for approval, parallel interviews, synthesis and report production.
- **Research jobs:** PostgreSQL-backed queue, worker leases, restartable checkpoints and durable job events.
- **FastAPI:** typed research, feedback, analyst, interview, report and health endpoints with `X-API-Key` authentication.
- **Research guardrails:** input bounds, citation URL validation and report checks.
- **Observability:** LangSmith tracing hooks, execution timings and usage counters.
- **Professional frontend:** Next.js 15, TypeScript, Tailwind CSS 4, private sign-in, responsive workspace, analyst approval, SSE progress, interviews and Markdown report export.

## Architecture

```text
Browser (Next.js :3000)
   │ signed HttpOnly cookie
   ▼
Next.js API proxy ── X-API-Key (server only) ──► FastAPI :8000
                                                   │
                                    PostgreSQL research tables & events
                                                   │
                                    LangGraph background worker
                                                   │
                               LangGraph Postgres checkpoints + LLM + Tavily
```

## Requirements

- Python 3.12, [`uv`](https://docs.astral.sh/uv/)
- Node.js 20+ and npm
- Docker Desktop with Docker Compose
- OpenAI API key and Tavily API key to execute actual research

## 1. Configure the backend

From the repository root (`deep-research-agent`):

```powershell
Copy-Item .env.example .env
uv sync --group dev
```

Set `OPENAI_API_KEY`, `TAVILY_API_KEY`, a long `API_KEY`, and PostgreSQL credentials in `.env`. Avoid committing secrets. If running the Python API directly on your host, its `DATABASE_URL` and `CHECKPOINT_DATABASE_URL` must use the **published host port** (for example 5433). Inside Compose services, use `postgres:5432`.

Start PostgreSQL:

```powershell
docker compose up -d postgres
docker compose ps
```

Your Compose file must publish PostgreSQL to the host if you are running FastAPI locally. Example:

```yaml
ports:
  - "127.0.0.1:5433:5432"
```

Then configure host database URLs accordingly:

```text
DATABASE_URL=postgresql+psycopg://research:<PASSWORD>@127.0.0.1:5433/research
CHECKPOINT_DATABASE_URL=postgresql://research:<PASSWORD>@127.0.0.1:5433/research
```

Initialize tables:

```powershell
uv run python scripts/setup_database.py
```

> Existing PostgreSQL volumes preserve their original database passwords; changing `.env` does not change an already initialized database user's password.

## 2. Run FastAPI and the worker

**Terminal A — API:**

```powershell
uv run uvicorn research_assistant.api.main:app --reload --port 8000
```

**Terminal B — worker:**

```powershell
uv run python scripts/run_worker.py
```

API docs: **http://127.0.0.1:8000/docs**. Research endpoints require your backend `X-API-Key`.

## 3. Run the frontend

**Terminal C:**

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Set `BACKEND_API_URL=http://127.0.0.1:8000`, `BACKEND_API_KEY` to match the backend `API_KEY`, and a strong `FRONTEND_USERNAME`, `FRONTEND_PASSWORD`, `SESSION_SECRET` (32+ characters). Open **http://localhost:3000**.

### Research journey

1. **Sign in** to the private studio.
2. **New research:** provide topic, analyst count (1–8) and number of interview turns (1–8).
3. **Research workspace:** follow the durable event timeline.
4. **Human-in-the-loop:** when `awaiting_feedback`, review the generated analyst cards and approve or ask for revisions.
5. **Monitor:** the background worker continues interviews and report synthesis.
6. **Read & export:** the final research report appears when `research_completed` emits its `report_id`; download the Markdown report.

## Backend API reference

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/research` | Enqueue research |
| GET | `/api/v1/research` | Paginated run list |
| GET | `/api/v1/research/{run_id}` | Run status/details |
| POST | `/api/v1/research/{run_id}/feedback` | Approve or reject analysts |
| GET | `/api/v1/research/{run_id}/stream` | Replayable SSE activity |
| GET | `/api/v1/research/{run_id}/analysts` | Persisted analyst profiles |
| GET | `/api/v1/research/{run_id}/interviews` | Persisted interviews |
| GET | `/api/v1/reports/{report_id}` | Final report |
| GET | `/api/v1/health` | Database readiness |

The frontend proxies these backend routes through `/api/backend/*` and adds the API key server-side. The authentication session must be valid to access the proxy.

## Tests and quality

```powershell
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest -rs -q
cd frontend
npm run lint
npm run typecheck
npm run build
```

Database integration tests may skip unless a separate disposable `TEST_DATABASE_URL` is provided. A passing unit suite does **not** prove live LLM/Tavily calls, worker checkpoint recovery or actual cloud deployment have been validated.

## Project map

```text
frontend/                  Next.js application and API proxy
src/research_assistant/   Agents, orchestration, API and infrastructure
migrations/               Alembic schema migrations
scripts/                  Database setup and worker commands
tests/                    Unit, API, integration and quality evaluations
docs/                     Architecture, decisions and deployment guidance
Dockerfile                Backend container
docker-compose.yml         Backend services + PostgreSQL
```

## Deployment and security

- Current setup is **single-operator**, not multi-tenant. Shared API key plus a signed login cookie does **not** enforce user ownership of research runs.
- Never expose secrets through frontend `NEXT_PUBLIC_` environment variables; never commit `.env` or `.env.local`.
- Deploy over HTTPS; add a proper identity provider, per-user ownership checks, CSRF defenses and distributed rate limiting before a public multi-user launch.
- Use managed PostgreSQL, automated backups, secret management, structured telemetry and worker health monitoring.
- Long-running SSE streams require proxy/load-balancer support for streaming and appropriate idle timeouts.
- See `docs/deployment/production.md` for backend operational considerations.

## License

No license is granted by this README. Add a LICENSE file only if you intend to publish or distribute the project under a particular license.
