from pathlib import Path

import pytest

from deploy_samurai.services.repo_analysis.metadata import extract_repo_metadata


def test_extract_repo_metadata_combines_structure_and_stack(tmp_path: Path) -> None:
    repo_path = tmp_path / "demo-api"
    repo_path.mkdir()
    (repo_path / "README.md").write_text("# Demo API", encoding="utf-8")
    (repo_path / "pyproject.toml").write_text(
        """
[project]
dependencies = ["fastapi>=0.112", "pytest"]
""",
        encoding="utf-8",
    )
    (repo_path / "uv.lock").write_text("", encoding="utf-8")
    (repo_path / "app").mkdir()
    (repo_path / "app" / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")
    (repo_path / "tests").mkdir()
    (repo_path / "tests" / "test_health.py").write_text("def test_health(): pass", encoding="utf-8")

    metadata = extract_repo_metadata(repo_path, default_branch="main")

    assert metadata.repo_summary.name == "demo-api"
    assert metadata.repo_summary.default_branch == "main"
    assert metadata.repo_summary.language == "python"
    assert metadata.repo_summary.framework == "fastapi"
    assert metadata.repo_summary.package_manager == "uv"
    assert metadata.repo_summary.has_tests is True
    assert metadata.structure.root_files == ["README.md", "pyproject.toml", "uv.lock"]
    assert metadata.structure.folder_tree == ["app", "tests"]
    assert metadata.structure.entrypoints == ["app/main.py"]


def test_extract_repo_metadata_detects_test_files_without_tests_directory(tmp_path: Path) -> None:
    repo_path = tmp_path / "node-service"
    repo_path.mkdir()
    (repo_path / "package.json").write_text(
        """
{
  "dependencies": {
    "express": "^4.18.0"
  }
}
""",
        encoding="utf-8",
    )
    (repo_path / "server.js").write_text("const app = express()", encoding="utf-8")
    (repo_path / "server.test.js").write_text("test('server', () => {})", encoding="utf-8")

    metadata = extract_repo_metadata(repo_path)

    assert metadata.repo_summary.language == "javascript"
    assert metadata.repo_summary.framework == "express"
    assert metadata.repo_summary.package_manager == "npm"
    assert metadata.repo_summary.has_tests is True
    assert metadata.structure.entrypoints == ["server.js"]


def test_extract_repo_metadata_requires_existing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_repo_metadata(tmp_path / "missing")
