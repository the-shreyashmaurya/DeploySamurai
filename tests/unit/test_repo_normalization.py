from deploy_samurai.schemas.repo_analysis import RepoAnalysisResponse, RepoStructure, RepoSummary
from deploy_samurai.services.repo_analysis.normalization import normalize_repo_metadata


def test_normalize_repo_metadata_produces_stable_reasoning_input() -> None:
    analysis = RepoAnalysisResponse(
        repo_summary=RepoSummary(
            name="demo-api",
            default_branch="main",
            language="Python",
            framework="FastAPI",
            package_manager="uv",
            has_tests=True,
        ),
        structure=RepoStructure(
            root_files=["pyproject.toml", "README.md", "README.md"],
            folder_tree=["tests", "app"],
            entrypoints=["app/main.py", "app/main.py"],
        ),
    )

    normalized = normalize_repo_metadata(analysis)

    assert normalized.name == "demo-api"
    assert normalized.default_branch == "main"
    assert normalized.language == "python"
    assert normalized.framework == "fastapi"
    assert normalized.package_manager == "uv"
    assert normalized.has_tests is True
    assert normalized.root_files == ["README.md", "pyproject.toml"]
    assert normalized.folder_paths == ["app", "tests"]
    assert normalized.entrypoints == ["app/main.py"]
    assert normalized.signals == ["has_tests", "has_entrypoints", "has_folder_structure"]


def test_normalize_repo_metadata_falls_back_to_unknown_for_unrecognized_values() -> None:
    analysis = RepoAnalysisResponse(
        repo_summary=RepoSummary(
            name="mystery",
            language="go",
            framework="fiber",
            package_manager="bun",
        ),
        structure=RepoStructure(),
    )

    normalized = normalize_repo_metadata(analysis)

    assert normalized.language == "unknown"
    assert normalized.framework == "unknown"
    assert normalized.package_manager == "unknown"
    assert normalized.signals == []
