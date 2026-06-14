from __future__ import annotations

from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata
from deploy_samurai.schemas.repo_analysis import RepoAnalysisResponse

KNOWN_FRAMEWORKS = {
    "fastapi",
    "django",
    "flask",
    "nextjs",
    "react",
    "flutter",
    "express",
    "spring-boot",
    "spring-cloud",
    "static-site",
}
KNOWN_LANGUAGES = {"python", "javascript", "typescript", "dart", "java"}
KNOWN_PACKAGE_MANAGERS = {"uv", "poetry", "pipenv", "pip", "pnpm", "yarn", "npm", "pub", "maven", "gradle"}


def normalize_repo_metadata(analysis: RepoAnalysisResponse) -> NormalizedRepoMetadata:
    return NormalizedRepoMetadata(
        name=analysis.repo_summary.name,
        default_branch=analysis.repo_summary.default_branch,
        language=_normalize_value(analysis.repo_summary.language, KNOWN_LANGUAGES),
        framework=_normalize_value(analysis.repo_summary.framework, KNOWN_FRAMEWORKS),
        package_manager=_normalize_value(
            analysis.repo_summary.package_manager,
            KNOWN_PACKAGE_MANAGERS,
        ),
        has_tests=analysis.repo_summary.has_tests,
        root_files=sorted(set(analysis.structure.root_files)),
        folder_paths=sorted(set(analysis.structure.folder_tree)),
        entrypoints=sorted(set(analysis.structure.entrypoints)),
        signals=_build_signals(analysis),
    )


def _normalize_value(value: str | None, allowed_values: set[str]) -> str:
    if value is None:
        return "unknown"

    normalized = value.strip().lower()
    return normalized if normalized in allowed_values else "unknown"


def _build_signals(analysis: RepoAnalysisResponse) -> list[str]:
    signals: list[str] = []
    if analysis.repo_summary.has_tests:
        signals.append("has_tests")
    if analysis.structure.entrypoints:
        signals.append("has_entrypoints")
    if analysis.structure.folder_tree:
        signals.append("has_folder_structure")
    return signals
