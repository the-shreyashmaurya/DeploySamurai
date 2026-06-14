from fastapi import APIRouter

from deploy_samurai.schemas.verification import VerificationRequest, VerificationResponse
from deploy_samurai.services.verification.verifier import run_verification

router = APIRouter()


@router.post("", response_model=VerificationResponse)
def verify_deployment(payload: VerificationRequest) -> VerificationResponse:
    return run_verification(payload)
