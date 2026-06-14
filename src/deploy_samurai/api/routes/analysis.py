from fastapi import APIRouter, HTTPException, status

from deploy_samurai.schemas.repo_analysis import RepoAnalysisRequest, RepoAnalysisResponse
from deploy_samurai.services.repo_analysis.analyzer import analyze_repository
from deploy_samurai.services.repo_analysis.workspace import RepoCloneError

router = APIRouter()


@router.post("/repo", response_model=RepoAnalysisResponse)
async def analyze_repo(payload: RepoAnalysisRequest) -> RepoAnalysisResponse:
    try:
        return analyze_repository(payload)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RepoCloneError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
