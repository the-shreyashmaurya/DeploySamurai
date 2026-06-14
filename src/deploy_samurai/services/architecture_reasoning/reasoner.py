from __future__ import annotations

from deploy_samurai.schemas.architecture import (
    ArchitectureReasoningRequest,
    ArchitectureReasoningResponse,
)
from deploy_samurai.schemas.repo_analysis import RepoAnalysisResponse
from deploy_samurai.services.architecture_reasoning.summary import generate_architecture_summary
from deploy_samurai.services.repo_analysis.normalization import normalize_repo_metadata


def reason_about_architecture(
    payload: ArchitectureReasoningRequest,
) -> ArchitectureReasoningResponse:
    analysis = RepoAnalysisResponse(
        repo_summary=payload.repo_summary,
        structure=payload.structure,
    )
    metadata = normalize_repo_metadata(analysis)
    return generate_architecture_summary(metadata)
