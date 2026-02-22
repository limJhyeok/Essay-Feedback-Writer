# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Essay Feedback Writer** is a full-stack web app that delivers AI-powered feedback on student essays (primarily IELTS). It uses FastAPI + PostgreSQL on the backend and Svelte + Vite on the frontend, containerized via Docker Compose with Traefik as a reverse proxy.

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
FastAPI (backend/app/)
    │
    ├── JWT auth (python-jose + bcrypt)
    ├── OpenAI API for essay feedback generation
    ├── SMTP email for password recovery
    └── SQLAlchemy ORM
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
| CRUD | `crud/` | Database query logic per entity |
| Routes | `api/routes/` | HTTP endpoints (3 routers) |
| Core | `core/` | config, security (JWT/Fernet), DB session |

**API base path**: `/api/v1`
- `user_router.py` — auth: login, register, password reset
- `ielts_router.py` — core app: prompts, essays, feedbacks, bots, rubrics
- `util_router.py` — health check

**Dependency injection** (`api/deps.py`): `SessionDep` (DB session) and `CurrentUser` (JWT-validated user) are injected into route handlers via `Annotated` + `Depends`.

### Frontend Structure (`frontend/src/`)

- `App.svelte` — root component with `svelte-spa-router` route definitions
- `routes/` — page-level components (Auth, IELTSFeedbackWriter, Password, ResetPassword)
- `lib/api.js` — fetch wrapper that attaches JWT Bearer token from the store
- `lib/store.js` — Svelte writable stores persisted to `localStorage` (`isLogin`, `accessToken`)

### Key Data Models

- **User** — email/password, superuser flag, linked to essays, feedbacks, API keys
- **Essay** — student submission, linked to a Prompt
- **Feedback** — AI-generated feedback stored as JSONB, linked to Essay + Bot
- **Bot** — AI model configuration (name, version, deprecated flag)
- **AIProvider / APIModel** — provider registry (e.g., OpenAI, Anthropic) and their models
- **UserAPIKey** — user's personal API keys, encrypted with Fernet
- **Prompt / Rubric / RubricCriterion** — essay assignment + scoring criteria
- **ExampleEssay** — sample essays per prompt

### Feedback Generation Flow
1. User submits essay → backend stores `Essay` in DB
2. Backend retrieves user's encrypted API key (or falls back to superuser's key)
3. Backend calls OpenAI API with essay + prompt + rubric criteria
4. Response stored as JSONB in `Feedback` model
5. Frontend renders feedback using `marked.js`

## Environment Configuration

Copy `.env.example` to `.env` and fill in:

- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- `FERNET_SECRET` — generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `POSTGRES_SERVER=db` when using Docker Compose, `localhost` for local dev
- `VITE_SERVER_URL` — backend URL seen by the browser (not the container name)
- `ENVIRONMENT=local|staging|production` — `production` disables Swagger docs at `/docs`

## Testing

- **Framework**: pytest
- **Location**: `backend/app/tests/` with `conftest.py` fixtures
- **Test DB**: separate database configured via `TEST_POSTGRES_*` env vars
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

Seed data (AI providers, bots, rubrics) is loaded via `backend/app/initial_data.py` from CSV files in `backend/app/data/`.

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
