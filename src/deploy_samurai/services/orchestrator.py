from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deploy_samurai.db.session import async_session_factory
from deploy_samurai.models.job import Job
from deploy_samurai.schemas.jobs import JobCreateRequest, JobCreateResponse, JobReadResponse


class JobOrchestrator:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_job(self, payload: JobCreateRequest) -> JobCreateResponse:
        job = Job(
            repo_url=str(payload.repo_url),
            mode=payload.mode,
            target=payload.target,
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return JobCreateResponse(job_id=job.id, status=job.status, mode=job.mode)

    async def get_job(self, job_id: str) -> JobReadResponse | None:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if job is None:
            return None
        return JobReadResponse.model_validate(job)


async def get_job_orchestrator() -> JobOrchestrator:
    async with async_session_factory() as session:
        yield JobOrchestrator(session)
