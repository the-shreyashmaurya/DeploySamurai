from fastapi import APIRouter, HTTPException

from deploy_samurai.schemas.deployment import (
    AwsCredentialPreflightResult,
    DeploymentRequest,
    DeploymentResult,
)
from deploy_samurai.services.deployment.preflight import check_aws_credentials
from deploy_samurai.services.deployment.sam_cli import SamDeploymentError, execute_sam_build_and_deploy

router = APIRouter()


@router.post("/preflight", response_model=AwsCredentialPreflightResult)
def run_deployment_preflight() -> AwsCredentialPreflightResult:
    return check_aws_credentials()


@router.post("/sam", response_model=DeploymentResult)
def deploy_sam_stack(payload: DeploymentRequest) -> DeploymentResult:
    preflight = check_aws_credentials()
    if preflight.status != "passed":
        raise HTTPException(status_code=400, detail=preflight.message)

    stack_name = payload.stack_name or f"deploy-samurai-{payload.job_id.replace('_', '-')}"
    try:
        return execute_sam_build_and_deploy(payload, stack_name=stack_name)
    except SamDeploymentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
