from fastapi import APIRouter

from deploy_samurai.api.routes import analysis, health, jobs, reasoning

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(analysis.router, prefix="/analyze", tags=["analysis"])
api_router.include_router(reasoning.router, prefix="/reason", tags=["reasoning"])
