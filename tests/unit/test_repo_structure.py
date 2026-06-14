from pathlib import Path

import pytest

from deploy_samurai.services.repo_analysis.structure import (
    extract_repo_structure,
    flatten_folder_tree,
)


def test_extract_repo_structure_returns_root_files_and_folder_tree(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]", encoding="utf-8")
    (tmp_path / "src" / "api" / "routes").mkdir(parents=True)
    (tmp_path / "src" / "worker").mkdir(parents=True)
    (tmp_path / "tests" / "unit").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (tmp_path / "node_modules" / "package").mkdir(parents=True)

    snapshot = extract_repo_structure(tmp_path)

    assert snapshot.root_files == ["README.md", "pyproject.toml"]
    assert flatten_folder_tree(snapshot.folder_tree) == [
        "src",
        "src/api",
        "src/api/routes",
        "src/worker",
        "tests",
        "tests/unit",
    ]


def test_extract_repo_structure_respects_max_depth(tmp_path: Path) -> None:
    (tmp_path / "src" / "api" / "routes" / "v1").mkdir(parents=True)

    snapshot = extract_repo_structure(tmp_path, max_depth=2)

    assert flatten_folder_tree(snapshot.folder_tree) == ["src", "src/api"]


def test_extract_repo_structure_limits_children_per_directory(tmp_path: Path) -> None:
    for name in ["zeta", "alpha", "beta"]:
        (tmp_path / name).mkdir()

    snapshot = extract_repo_structure(tmp_path, max_children_per_directory=2)

    assert flatten_folder_tree(snapshot.folder_tree) == ["alpha", "beta"]


def test_extract_repo_structure_requires_existing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_repo_structure(tmp_path / "missing")


def test_extract_repo_structure_rejects_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "README.md"
    file_path.write_text("# Demo", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        extract_repo_structure(file_path)
