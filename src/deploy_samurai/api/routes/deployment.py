from fastapi import APIRouter

from deploy_samurai.schemas.deployment import AwsCredentialPreflightResult
from deploy_samurai.services.deployment.preflight import check_aws_credentials

router = APIRouter()


@router.post("/preflight", response_model=AwsCredentialPreflightResult)
def run_deployment_preflight() -> AwsCredentialPreflightResult:
    return check_aws_credentials()
