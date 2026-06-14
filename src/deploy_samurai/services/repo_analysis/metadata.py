from __future__ import annotations

from pathlib import Path

from deploy_samurai.schemas.repo_analysis import RepoAnalysisResponse, RepoStructure, RepoSummary
from deploy_samurai.services.repo_analysis.stack_detection import detect_stack
from deploy_samurai.services.repo_analysis.structure import extract_repo_structure, flatten_folder_tree


def extract_repo_metadata(repo_path: Path, default_branch: str | None = None) -> RepoAnalysisResponse:
    root = repo_path.resolve()
    structure = extract_repo_structure(root)
    stack = detect_stack(root)

    return RepoAnalysisResponse(
        repo_summary=RepoSummary(
            name=root.name,
            default_branch=default_branch,
            language=stack.language,
            framework=stack.framework,
            package_manager=stack.package_manager,
            has_tests=_has_tests(root),
        ),
        structure=RepoStructure(
            root_files=structure.root_files,
            folder_tree=flatten_folder_tree(structure.folder_tree),
            entrypoints=_detect_entrypoints(root),
        ),
    )


def _has_tests(root: Path) -> bool:
    if (root / "tests").is_dir() or (root / "test").is_dir():
        return True

    test_patterns = ("test_*.py", "*_test.py", "*.test.js", "*.spec.js", "*.test.ts", "*.spec.ts")
    return any(any(root.rglob(pattern)) for pattern in test_patterns)


def _detect_entrypoints(root: Path) -> list[str]:
    candidates = [
        "main.py",
        "app/main.py",
        "src/main.py",
        "server.js",
        "src/server.js",
        "index.js",
        "src/index.js",
        "app/page.tsx",
        "pages/index.tsx",
        "lib/main.dart",
        "web/index.html",
        "index.html",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
    ]
    return [path for path in candidates if (root / path).is_file()]
