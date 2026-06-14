from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from deploy_samurai.core.github import parse_github_repo_url
from deploy_samurai.models.job import DeploymentTarget, JobMode, JobStatus


class JobCreateRequest(BaseModel):
    repo_url: HttpUrl
    mode: JobMode = JobMode.ADVISOR
    target: DeploymentTarget = DeploymentTarget.AWS_SAM
    allow_deploy: bool = False

    @model_validator(mode="after")
    def deployment_requires_explicit_mode(self) -> "JobCreateRequest":
        if self.mode == JobMode.AUTONOMOUS and not self.allow_deploy:
            raise ValueError("Autonomous mode requires allow_deploy=true.")
        return self

    @model_validator(mode="after")
    def repo_url_must_be_github(self) -> "JobCreateRequest":
        parse_github_repo_url(str(self.repo_url))
        return self


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus
    mode: JobMode


class JobReadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str = Field(validation_alias="id")
    status: JobStatus
    current_step: str
    progress: int
