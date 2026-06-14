from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class GitHubRepoUrl:
    owner: str
    repo: str
    normalized_url: str


def parse_github_repo_url(value: str) -> GitHubRepoUrl:
    parsed = urlparse(value.strip())

    if parsed.scheme != "https":
        raise ValueError("GitHub repository URL must use https.")

    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("Only GitHub repository URLs are supported.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("GitHub repository URL must be in the form https://github.com/owner/repo.")

    owner, repo = parts
    if repo.endswith(".git"):
        repo = repo.removesuffix(".git")

    if not owner or not repo:
        raise ValueError("GitHub repository URL must include an owner and repository name.")

    if parsed.query or parsed.fragment:
        raise ValueError("GitHub repository URL must not include query strings or fragments.")

    return GitHubRepoUrl(
        owner=owner,
        repo=repo,
        normalized_url=f"https://github.com/{owner}/{repo}",
    )
