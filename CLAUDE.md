# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Essay Feedback Writer** is a full-stack web app that delivers AI-powered feedback on student essays across multiple domains (IELTS Writing, Korean university entrance exams / 수능 논술). It uses FastAPI + PostgreSQL on the backend and Svelte + Vite on the frontend, containerized via Docker Compose with Traefik as a reverse proxy. A multi-agent scoring system evaluates essays per criterion in parallel, with configurable YAML-based rubrics.

## Common Commands

### Docker-based Development (Primary Workflow)
```bash
# Start all services with hot-reload (docker-compose.override.yaml applied automatically)
docker-compose up -d

# Run backend tests
docker-compose exec backend bash ./scripts/test.sh

# Open a shell inside the backend container
docker-compose exec backend bash

# Apply DB migrations inside the container
alembic upgrade head

# Create a new migration after modifying models.py
alembic revision --autogenerate -m "Description"
```

### Backend (local, without Docker)
```bash
cd backend
uv sync                                       # Install all dependencies (including dev)
uv run pytest                                 # Run all tests
uv run pytest app/tests/api/routes/           # Run a specific directory
uv run pytest app/tests/api/routes/test_users.py  # Run a single test file
uv run ruff check --fix                       # Lint and format
```

### Frontend (local, without Docker)
```bash
cd frontend
npm install
npm run dev      # Dev server at http://localhost:5173
npm run build    # Production build
```

### Pre-commit Hooks
```bash
pre-commit install        # Set up hooks after cloning
pre-commit run --all      # Run all hooks manually
```

## Architecture

```
Svelte SPA (frontend/)
    │ REST API calls via frontend/src/lib/api.js
    ▼
Traefik (reverse proxy, HTTPS, Let's Encrypt)
    │
    ▼
FastAPI (backend/app/)  [fully async — AsyncSession + asyncio]
    │
    ├── JWT auth (python-jose + bcrypt)
    ├── LangChain LLM clients (OpenAI, Anthropic) for essay feedback
    ├── VLM-based OCR for handwriting input
    ├── SMTP email for password recovery
    └── Async SQLAlchemy ORM
    │
    ▼
PostgreSQL (separate DB for tests)
```

### Backend Structure (`backend/app/`)

| Layer | Directory | Purpose |
|---|---|---|
| Entry | `main.py` | FastAPI app init, CORS, routers |
| Models | `models.py` | All SQLAlchemy ORM models |
| Schemas | `schemas/` | Pydantic validation (input/output) |
| CRUD | `crud/` | Async database query logic per entity |
| Routes | `api/routes/` | HTTP endpoints (4 routers) |
| Services | `services/` | Business logic (e.g., `feedback_service.py`) |
| Agents | `agents/` | Multi-agent scoring: schema, swarm, aggregator, builder, loader |
| Agent Configs | `agents/configs/` | YAML rubric definitions per domain (IELTS, KSAT) |
| Core | `core/` | config, security (JWT/Fernet), async DB session |

**API base path**: `/api/v1`
- `user_router.py` — auth: login, register, password reset
- `ielts_router.py` — IELTS-specific: prompts, essays, feedbacks, rubrics; also `POST /essays/handwriting` and `GET /essays/{id}/image`
- `ksat_router.py` — KSAT-specific: exam browsing (university/year/track filters), essay submission per question, feedback generation, criteria & examples
- `shared_router.py` — cross-domain: bots, AI providers, API models, user API key management
- `util_router.py` — health check

**Dependency injection** (`api/deps.py`): `SessionDep` (async DB session) and `CurrentUser` (JWT-validated user) are injected into route handlers via `Annotated` + `Depends`.

### Frontend Structure (`frontend/src/`)

- `App.svelte` — root component with `svelte-spa-router` route definitions
- `routes/DomainSelector.svelte` — landing page with domain cards (IELTS, KSAT, future: Math, Science)
- `routes/IELTSFeedbackWriter.svelte` — IELTS essay submission and feedback UI
- `routes/KSATFeedbackWriter.svelte` — KSAT exam browsing, per-question essay/feedback UI
- `routes/` — also Auth, Password, ResetPassword pages
- `components/HandwritingCanvas.svelte` — stylus/touch canvas for handwriting input
- `lib/api.js` — fetch wrapper that attaches JWT Bearer token from the store
- `lib/store.js` — Svelte writable stores persisted to `localStorage` (`isLogin`, `accessToken`)

### Key Data Models

- **User** — email/password, superuser flag, linked to essays, feedbacks, API keys
- **Essay** — student submission, linked to a Prompt; includes `input_type` (`text`/`handwriting`), `image_path` (uploaded image), and `ocr_text` (VLM-extracted text)
- **Feedback** — AI-generated feedback stored as JSONB, linked to Essay + Bot
- **Bot** — AI model configuration (name, version, deprecated flag)
- **AIProvider / APIModel** — provider registry (e.g., OpenAI, Anthropic) and their models
- **UserAPIKey** — user's personal API keys, encrypted with Fernet
- **Prompt** — essay assignment with `domain` field (`DomainType`: ielts / ksat)
- **Rubric / RubricCriterion** — scoring criteria for prompts
- **ExampleEssay** — sample essays per prompt
- **Exam** — KSAT exam metadata (university, year, track: humanities/sciences), stores unified passage `content`
- **ExamQuestion** — links exam to prompt, with question_number, max_points, char_min/max, passage_refs

### Feedback Generation Flow

**Multi-agent scoring pipeline** (used by all domains):
1. User submits essay → backend stores `Essay` in DB
2. Backend retrieves user's encrypted API key (or falls back to superuser's key)
3. `feedback_service.generate_feedback()` loads the YAML rubric for the prompt's domain
4. `builder.py` generates one `AgentConfig` per rubric criterion
5. `ScoringSwarm` runs all criterion agents in parallel (semaphore-limited, max 4 concurrent)
6. Each agent scores its criterion using structured LLM output (`CriterionResult`)
7. `Aggregator` combines scores via weighted average, LLM holistic synthesis, or both
8. Result stored as JSONB: `{ feedback_by_criteria: {...}, overall_score, overall_feedback }`
9. Frontend renders feedback using `marked.js`

**Handwriting path** (IELTS only):
1. User draws on `HandwritingCanvas.svelte` → image uploaded to `POST /essays/handwriting`
2. Backend stores `Essay` (input_type=`handwriting`) + image file in `UPLOAD_DIR`
3. VLM OCR extracts text → saved to `essay.ocr_text` → standard scoring pipeline runs

**Rubric configuration:**
- YAML files in `agents/configs/` define criteria, weights, scales, band descriptors, and prompt templates
- Loaded at runtime with caching via `loader.py`
- Registry maps rubric names → YAML paths (e.g., `"KSAT 2025 CAU Humanities Q1"` → `ksat/cau_2025_humanities_q1.yaml`)

## Environment Configuration

Copy `.env.example` to `.env` and fill in:

- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- `FERNET_SECRET` — generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `POSTGRES_SERVER=db` when using Docker Compose, `localhost` for local dev
- `VITE_SERVER_URL` — backend URL seen by the browser (not the container name)
- `ENVIRONMENT=local|staging|production` — `production` disables Swagger docs at `/docs`
- `UPLOAD_DIR` — directory for uploaded essay images (default: `/app/uploads`); mounted as the `essay-uploads` Docker volume
- `MAX_UPLOAD_SIZE_MB` — maximum allowed upload size in MB (default: `10`)

## Testing

- **Framework**: pytest + pytest-asyncio
- **Location**: `backend/app/tests/` with `conftest.py` fixtures
- **Test DB**: separate database configured via `TEST_POSTGRES_*` env vars; runs on RAM-backed `tmpfs` in Docker for speed
- **HTTP client**: `httpx.AsyncClient` with `ASGITransport` (replaces synchronous `TestClient`)
- **Coverage**: HTML report generated in `htmlcov/`

```bash
# Inside backend container or locally with uv
pytest app/tests/crud/test_user.py         # single file
pytest app/tests/ -k "test_login"          # filter by name
```

## Database Migrations

Models are defined in `backend/app/models.py`. After changes:
```bash
alembic revision --autogenerate -m "Add X column to Y table"
alembic upgrade head
```

Seed data (AI providers, bots, rubrics) is loaded via `backend/app/initial_data.py` from CSV files in `backend/app/data/`. KSAT exam data is seeded from `backend/app/data/ksat/seed_ksat_data.py`.

## CI/CD

GitHub Actions workflows in `.github/workflows/`:
- `test-backend.yml` — runs pytest on every push
- `test-docker-compose.yml` — integration test of the full stack
- `deploy-production.yml` — builds and pushes Docker images, deploys to server

Docker images are published to `ghcr.io/limjhyeok/`.

## Docker Compose Files

| File | Purpose |
|---|---|
| `docker-compose.yaml` | Base service definitions |
| `docker-compose.override.yaml` | Dev overrides (volume mounts, hot-reload) |
| `docker-compose.test.yaml` | Test environment |
| `docker-compose.traefik.yaml` | Production Traefik configuration |

## Local Service URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/v1 |
| Swagger docs | http://localhost:8000/docs |
| Adminer (DB UI) | http://localhost:8080 |
| Traefik dashboard | http://localhost:8090 |
