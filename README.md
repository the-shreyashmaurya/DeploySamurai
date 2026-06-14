# DeploySamurai

DeploySamurai is an AI-assisted AWS serverless architect for GitHub repositories.
It analyzes a repository, recommends a bounded AWS SAM architecture, and can later generate,
deploy, and verify the stack.

## Stack

- Backend: FastAPI
- Runtime and dependency management: uv
- Database: PostgreSQL
- Migrations: Alembic
- IaC target: AWS SAM
- Frontend: Flutter web, scaffolded under `apps/frontend`

## Project Layout

```text
src/deploy_samurai/
  api/                 FastAPI routers
  core/                settings and shared configuration
  db/                  SQLAlchemy base, session, model registry
  models/              persistence models
  schemas/             versioned API and service contracts
  services/            orchestrator and domain services
alembic/               PostgreSQL migrations
apps/frontend/         Flutter web app home
tests/                 unit and contract tests
artifacts/             generated SAM files and reports
scripts/               local developer commands
```

## Local Setup

Install uv, then create the environment and install dependencies:

```powershell
uv sync --dev
```

Start Postgres:

```powershell
docker compose up -d postgres
```

Run migrations:

```powershell
uv run alembic upgrade head
```

Run the API:

```powershell
uv run uvicorn deploy_samurai.main:app --reload --host 127.0.0.1 --port 8000
```

Check health:

```powershell
curl http://127.0.0.1:8000/v1/health
```

## Quality Checks

```powershell
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

## First API Contract

Create an advisor job:

```http
POST /v1/jobs
Content-Type: application/json

{
  "repo_url": "https://github.com/org/repo",
  "mode": "advisor",
  "target": "aws-sam",
  "allow_deploy": false
}
```

Autonomous deployment must be explicitly gated with `allow_deploy=true`.
