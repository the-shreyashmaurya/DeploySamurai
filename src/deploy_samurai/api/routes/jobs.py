from fastapi import APIRouter, Depends, HTTPException, status

from deploy_samurai.schemas.jobs import JobCreateRequest, JobCreateResponse, JobReadResponse
from deploy_samurai.services.orchestrator import JobOrchestrator, get_job_orchestrator

router = APIRouter()


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    payload: JobCreateRequest,
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
) -> JobCreateResponse:
    return await orchestrator.create_job(payload)


@router.get("/{job_id}", response_model=JobReadResponse)
async def read_job(
    job_id: str,
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
) -> JobReadResponse:
    job = await orchestrator.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
