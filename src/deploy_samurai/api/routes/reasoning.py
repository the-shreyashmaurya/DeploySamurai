from fastapi import APIRouter

from deploy_samurai.schemas.architecture import (
    ArchitectureReasoningRequest,
    ArchitectureReasoningResponse,
)
from deploy_samurai.services.architecture_reasoning.reasoner import reason_about_architecture

router = APIRouter()


@router.post("/architecture", response_model=ArchitectureReasoningResponse)
async def reason_architecture(
    payload: ArchitectureReasoningRequest,
) -> ArchitectureReasoningResponse:
    return reason_about_architecture(payload)
