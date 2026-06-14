import pytest

from deploy_samurai.core.github import parse_github_repo_url


@pytest.mark.parametrize(
    ("url", "normalized_url"),
    [
        ("https://github.com/openai/openai-python", "https://github.com/openai/openai-python"),
        ("https://github.com/openai/openai-python.git", "https://github.com/openai/openai-python"),
        ("https://www.github.com/openai/openai-python", "https://github.com/openai/openai-python"),
    ],
)
def test_parse_github_repo_url_accepts_repo_urls(url: str, normalized_url: str) -> None:
    parsed = parse_github_repo_url(url)

    assert parsed.owner == "openai"
    assert parsed.repo == "openai-python"
    assert parsed.normalized_url == normalized_url


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/openai/openai-python",
        "https://example.com/openai/openai-python",
        "https://github.com/openai",
        "https://github.com/openai/openai-python/tree/main",
        "https://github.com/openai/openai-python?tab=readme",
        "https://github.com/openai/openai-python#readme",
    ],
)
def test_parse_github_repo_url_rejects_non_repo_urls(url: str) -> None:
    with pytest.raises(ValueError):
        parse_github_repo_url(url)
