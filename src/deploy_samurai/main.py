from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from deploy_samurai.api.router import api_router
from deploy_samurai.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Analyze GitHub repositories and generate AWS SAM deployment plans.",
    )
    app.include_router(api_router, prefix="/v1")
    return app


app = create_app()


def run() -> None:
    uvicorn.run(
        "deploy_samurai.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "local",
    )
