from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
}


@dataclass(frozen=True)
class FolderNode:
    name: str
    path: str
    children: list["FolderNode"] = field(default_factory=list)


@dataclass(frozen=True)
class RepoStructureSnapshot:
    root_files: list[str]
    folder_tree: list[FolderNode]


def extract_repo_structure(
    repo_path: Path,
    *,
    max_depth: int = 3,
    max_children_per_directory: int = 50,
) -> RepoStructureSnapshot:
    root = repo_path.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path must be a directory: {repo_path}")

    root_files = sorted(child.name for child in root.iterdir() if child.is_file())
    folder_tree = [
        _build_folder_node(child, root, max_depth, max_children_per_directory)
        for child in _iter_visible_directories(root, max_children_per_directory)
    ]

    return RepoStructureSnapshot(root_files=root_files, folder_tree=folder_tree)


def flatten_folder_tree(nodes: list[FolderNode]) -> list[str]:
    paths: list[str] = []
    for node in nodes:
        paths.append(node.path)
        paths.extend(flatten_folder_tree(node.children))
    return paths


def _build_folder_node(
    directory: Path,
    root: Path,
    remaining_depth: int,
    max_children_per_directory: int,
) -> FolderNode:
    children: list[FolderNode] = []
    if remaining_depth > 1:
        children = [
            _build_folder_node(child, root, remaining_depth - 1, max_children_per_directory)
            for child in _iter_visible_directories(directory, max_children_per_directory)
        ]

    return FolderNode(
        name=directory.name,
        path=directory.relative_to(root).as_posix(),
        children=children,
    )


def _iter_visible_directories(directory: Path, limit: int) -> list[Path]:
    children = [
        child
        for child in directory.iterdir()
        if child.is_dir() and child.name not in IGNORED_DIRECTORIES
    ]
    return sorted(children, key=lambda child: child.name.lower())[:limit]
