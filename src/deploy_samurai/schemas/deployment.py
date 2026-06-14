from typing import Literal

from pydantic import BaseModel


class DeploymentRequest(BaseModel):
    job_id: str
    artifact_path: str
    confirm_deploy: bool


class DeploymentCreateResponse(BaseModel):
    deployment_id: str
    status: Literal["in_progress", "failed", "succeeded"]
    stack_name: str | None = None


class DeploymentResult(BaseModel):
    deployment_id: str
    status: Literal["succeeded", "failed"]
    stack_name: str
    outputs: dict[str, str]
    logs: list[str] = []


class AwsCredentialPreflightResult(BaseModel):
    status: Literal["passed", "failed"]
    region: str
    account_id: str | None = None
    arn: str | None = None
    message: str
