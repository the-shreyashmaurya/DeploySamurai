import subprocess
from pathlib import Path

import pytest

from deploy_samurai.services.repo_analysis.workspace import RepoCloneError, clone_github_repo


def test_clone_github_repo_uses_safe_per_job_workspace(tmp_path: Path) -> None:
    calls = []

    def runner(command, **kwargs):  # type: ignore[no-untyped-def]
        calls.append((command, kwargs))
        destination = Path(command[-1])
        destination.mkdir(parents=True)
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    cloned = clone_github_repo(
        "https://github.com/openai/openai-python.git",
        "job_123",
        workspace_root=tmp_path,
        runner=runner,
    )

    assert cloned.repo_url.normalized_url == "https://github.com/openai/openai-python"
    assert cloned.path == tmp_path.resolve() / "job_123" / "openai__openai-python"
    assert calls[0][0] == [
        "git",
        "clone",
        "--depth",
        "1",
        "--single-branch",
        "https://github.com/openai/openai-python",
        str(cloned.path),
    ]
    assert calls[0][1]["timeout"] == 60


def test_clone_github_repo_replaces_existing_workspace(tmp_path: Path) -> None:
    existing_file = tmp_path / "job_123" / "openai__openai-python" / "stale.txt"
    existing_file.parent.mkdir(parents=True)
    existing_file.write_text("old", encoding="utf-8")

    def runner(command, **kwargs):  # type: ignore[no-untyped-def]
        Path(command[-1]).mkdir(parents=True)
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    cloned = clone_github_repo(
        "https://github.com/openai/openai-python",
        "job_123",
        workspace_root=tmp_path,
        runner=runner,
    )

    assert cloned.path.exists()
    assert not existing_file.exists()


def test_clone_github_repo_rejects_unsafe_job_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsafe"):
        clone_github_repo(
            "https://github.com/openai/openai-python",
            "..\\outside",
            workspace_root=tmp_path,
        )


def test_clone_github_repo_raises_clone_error_on_git_failure(tmp_path: Path) -> None:
    def runner(command, **kwargs):  # type: ignore[no-untyped-def]
        return subprocess.CompletedProcess(command, returncode=128, stdout="", stderr="not found")

    with pytest.raises(RepoCloneError, match="not found"):
        clone_github_repo(
            "https://github.com/openai/missing",
            "job_123",
            workspace_root=tmp_path,
            runner=runner,
        )


def test_clone_github_repo_raises_clone_error_on_timeout(tmp_path: Path) -> None:
    def runner(command, **kwargs):  # type: ignore[no-untyped-def]
        raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

    with pytest.raises(RepoCloneError, match="timed out"):
        clone_github_repo(
            "https://github.com/openai/openai-python",
            "job_123",
            workspace_root=tmp_path,
            runner=runner,
        )
