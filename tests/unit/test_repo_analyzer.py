import subprocess
from pathlib import Path

from deploy_samurai.schemas.repo_analysis import RepoAnalysisRequest
from deploy_samurai.services.repo_analysis.analyzer import analyze_repository


def test_analyze_repository_clones_and_extracts_metadata(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspaces"

    def fake_runner(command, **kwargs):  # type: ignore[no-untyped-def]
        repo_path = Path(command[-1])
        repo_path.mkdir(parents=True)
        (repo_path / "pyproject.toml").write_text(
            """
[project]
dependencies = ["fastapi"]
""",
            encoding="utf-8",
        )
        (repo_path / "uv.lock").write_text("", encoding="utf-8")
        (repo_path / "app").mkdir()
        (repo_path / "app" / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    response = analyze_repository(
        RepoAnalysisRequest(
            repo_url="https://github.com/example/demo-api",
            job_id="job_123",
        ),
        workspace_root=workspace_root,
        runner=fake_runner,
    )

    assert response.repo_summary.name == "example__demo-api"
    assert response.repo_summary.language == "python"
    assert response.repo_summary.framework == "fastapi"
    assert response.repo_summary.package_manager == "uv"
    assert response.structure.root_files == ["pyproject.toml", "uv.lock"]
    assert response.structure.entrypoints == ["app/main.py"]
