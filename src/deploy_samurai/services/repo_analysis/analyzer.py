from __future__ import annotations

from pathlib import Path

from deploy_samurai.schemas.repo_analysis import RepoAnalysisRequest, RepoAnalysisResponse
from deploy_samurai.services.repo_analysis.metadata import extract_repo_metadata
from deploy_samurai.services.repo_analysis.workspace import CommandRunner, clone_github_repo


def analyze_repository(
    payload: RepoAnalysisRequest,
    workspace_root: Path | None = None,
    runner: CommandRunner | None = None,
) -> RepoAnalysisResponse:
    if runner is None:
        cloned_repo = clone_github_repo(
            repo_url=payload.repo_url,
            job_id=payload.job_id,
            workspace_root=workspace_root,
        )
        return extract_repo_metadata(cloned_repo.path, default_branch=None)

    cloned_repo = clone_github_repo(
        repo_url=payload.repo_url,
        job_id=payload.job_id,
        workspace_root=workspace_root,
        runner=runner,
    )
    return extract_repo_metadata(cloned_repo.path, default_branch=None)
