import pytest
from pydantic import ValidationError

from deploy_samurai.models.job import JobMode
from deploy_samurai.schemas.jobs import JobCreateRequest


def test_job_create_accepts_advisor_github_url() -> None:
    payload = JobCreateRequest(repo_url="https://github.com/openai/openai-python")

    assert str(payload.repo_url).startswith("https://github.com/openai/openai-python")
    assert payload.mode == JobMode.ADVISOR


def test_job_create_rejects_non_github_url() -> None:
    with pytest.raises(ValidationError, match="Only GitHub"):
        JobCreateRequest(repo_url="https://example.com/org/repo")


def test_job_create_rejects_github_owner_url_without_repo() -> None:
    with pytest.raises(ValidationError, match="owner/repo"):
        JobCreateRequest(repo_url="https://github.com/openai")


def test_autonomous_mode_requires_deploy_approval() -> None:
    with pytest.raises(ValidationError, match="allow_deploy=true"):
        JobCreateRequest(
            repo_url="https://github.com/openai/openai-python",
            mode=JobMode.AUTONOMOUS,
        )
