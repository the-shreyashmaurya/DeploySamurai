$ErrorActionPreference = "Stop"

uv run uvicorn deploy_samurai.main:app --reload --host 127.0.0.1 --port 8000
