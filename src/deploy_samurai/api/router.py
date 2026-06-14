from fastapi import APIRouter

from deploy_samurai.api.routes import analysis, deployment, health, jobs, reasoning, verification

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(analysis.router, prefix="/analyze", tags=["analysis"])
api_router.include_router(reasoning.router, prefix="/reason", tags=["reasoning"])
api_router.include_router(deployment.router, prefix="/deploy", tags=["deployment"])
api_router.include_router(verification.router, prefix="/verify", tags=["verification"])
