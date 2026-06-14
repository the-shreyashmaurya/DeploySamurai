from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from deploy_samurai.core.github import GitHubRepoUrl, parse_github_repo_url

GIT_CLONE_TIMEOUT_SECONDS = 60


class RepoCloneError(RuntimeError):
    pass


CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class ClonedRepo:
    repo_url: GitHubRepoUrl
    job_id: str
    path: Path


def clone_github_repo(
    repo_url: str,
    job_id: str,
    workspace_root: Path | None = None,
    runner: CommandRunner = subprocess.run,
) -> ClonedRepo:
    parsed_url = parse_github_repo_url(repo_url)
    root = (workspace_root or _default_workspace_root()).resolve()
    destination = _safe_job_repo_path(root, job_id, parsed_url)

    root.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    command = _clone_command(parsed_url.normalized_url, destination)
    try:
        result = runner(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=GIT_CLONE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RepoCloneError(f"Git clone timed out after {GIT_CLONE_TIMEOUT_SECONDS} seconds.") from exc
    except OSError as exc:
        raise RepoCloneError(f"Git clone failed to start: {exc}") from exc

    if result.returncode != 0:
        message = (result.stderr or result.stdout or "Unknown git clone error.").strip()
        raise RepoCloneError(f"Git clone failed: {message}")

    return ClonedRepo(repo_url=parsed_url, job_id=job_id, path=destination)


def _clone_command(repo_url: str, destination: Path) -> list[str]:
    return [
        "git",
        "clone",
        "--depth",
        "1",
        "--single-branch",
        repo_url,
        str(destination),
    ]


def _default_workspace_root() -> Path:
    from deploy_samurai.core.config import settings

    return settings.repo_workspace_root


def _safe_job_repo_path(root: Path, job_id: str, repo_url: GitHubRepoUrl) -> Path:
    safe_job_id = _safe_path_segment(job_id, "job id")
    safe_owner = _safe_path_segment(repo_url.owner, "GitHub owner")
    safe_repo = _safe_path_segment(repo_url.repo, "GitHub repository")

    destination = (root / safe_job_id / f"{safe_owner}__{safe_repo}").resolve()
    if not _is_relative_to(destination, root):
        raise ValueError("Resolved repository workspace escaped the configured root.")
    return destination


def _safe_path_segment(value: str, label: str) -> str:
    if not value:
        raise ValueError(f"{label} cannot be empty.")

    disallowed = {"/", "\\", ":", "\0"}
    if any(character in value for character in disallowed) or value in {".", ".."}:
        raise ValueError(f"{label} contains unsafe path characters.")

    return value


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
