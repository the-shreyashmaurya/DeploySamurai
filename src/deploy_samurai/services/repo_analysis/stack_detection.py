from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StackDetection:
    language: str | None
    framework: str | None
    package_manager: str | None


def detect_stack(repo_path: Path) -> StackDetection:
    root = repo_path.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path must be a directory: {repo_path}")

    root_files = {path.name for path in root.iterdir() if path.is_file()}
    package_dependencies = _read_package_dependencies(root / "package.json")
    pyproject_dependencies = _read_pyproject_dependencies(root / "pyproject.toml")

    language = _detect_language(root, root_files)
    package_manager = _detect_package_manager(root_files)
    framework = _detect_framework(root, package_dependencies, pyproject_dependencies)

    return StackDetection(
        language=language,
        framework=framework,
        package_manager=package_manager,
    )


def _detect_language(root: Path, root_files: set[str]) -> str | None:
    if {"pubspec.yaml", "pubspec.lock"} & root_files:
        return "dart"
    if {"pyproject.toml", "requirements.txt", "setup.py", "Pipfile"} & root_files:
        return "python"
    if {"package.json", "tsconfig.json"} & root_files:
        return "typescript" if _has_typescript_files(root) else "javascript"
    if {"pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"} & root_files:
        return "java"
    if _has_file_with_suffix(root, ".py"):
        return "python"
    if _has_typescript_files(root):
        return "typescript"
    if _has_file_with_suffix(root, ".dart"):
        return "dart"
    if _has_file_with_suffix(root, ".java"):
        return "java"
    if _has_file_with_suffix(root, ".js"):
        return "javascript"
    return None


def _detect_package_manager(root_files: set[str]) -> str | None:
    if "uv.lock" in root_files:
        return "uv"
    if "poetry.lock" in root_files:
        return "poetry"
    if "Pipfile.lock" in root_files:
        return "pipenv"
    if "requirements.txt" in root_files:
        return "pip"
    if "pubspec.lock" in root_files or "pubspec.yaml" in root_files:
        return "pub"
    if "pom.xml" in root_files:
        return "maven"
    if "build.gradle" in root_files or "build.gradle.kts" in root_files:
        return "gradle"
    if "pnpm-lock.yaml" in root_files:
        return "pnpm"
    if "yarn.lock" in root_files:
        return "yarn"
    if "package-lock.json" in root_files:
        return "npm"
    if "package.json" in root_files:
        return "npm"
    if "pyproject.toml" in root_files:
        return "uv"
    return None


def _detect_framework(
    root: Path,
    package_dependencies: set[str],
    pyproject_dependencies: set[str],
) -> str | None:
    dependencies = package_dependencies | pyproject_dependencies

    if (root / "pubspec.yaml").is_file() or (root / "lib" / "main.dart").is_file():
        return "flutter"
    if "fastapi" in dependencies:
        return "fastapi"
    if {"django", "flask"} & dependencies:
        return sorted({"django", "flask"} & dependencies)[0]
    if "next" in dependencies:
        return "nextjs"
    if "react" in dependencies:
        return "react"
    if "express" in dependencies:
        return "express"
    if {"index.html", "404.html"} & {path.name for path in root.iterdir() if path.is_file()}:
        return "static-site"
    if _contains_text(root, "*.xml", "spring-cloud") or _contains_text(root, "*.gradle", "spring-cloud"):
        return "spring-cloud"
    if _contains_text(root, "*.java", "@SpringBootApplication"):
        return "spring-boot"
    if _contains_text(root, "*.xml", "spring-boot") or _contains_text(root, "*.gradle", "spring-boot"):
        return "spring-boot"

    if _contains_text(root, "*.py", "FastAPI("):
        return "fastapi"
    if _contains_text(root, "*.py", "django"):
        return "django"
    if _contains_text(root, "*.js", "express(") or _contains_text(root, "*.ts", "express("):
        return "express"
    return None


def _read_package_dependencies(package_json_path: Path) -> set[str]:
    if not package_json_path.exists():
        return set()

    try:
        data = json.loads(package_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()

    dependencies: set[str] = set()
    for key in ("dependencies", "devDependencies"):
        values = data.get(key, {})
        if isinstance(values, dict):
            dependencies.update(str(name).lower() for name in values)
    return dependencies


def _read_pyproject_dependencies(pyproject_path: Path) -> set[str]:
    if not pyproject_path.exists():
        return set()

    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return set()

    dependencies: set[str] = set()
    project_dependencies = data.get("project", {}).get("dependencies", [])
    if isinstance(project_dependencies, list):
        dependencies.update(_normalize_python_dependency(value) for value in project_dependencies)

    optional_dependencies = data.get("project", {}).get("optional-dependencies", {})
    if isinstance(optional_dependencies, dict):
        for values in optional_dependencies.values():
            if isinstance(values, list):
                dependencies.update(_normalize_python_dependency(value) for value in values)

    return {dependency for dependency in dependencies if dependency}


def _normalize_python_dependency(value: object) -> str:
    name = str(value).strip().lower()
    for separator in ("[", "<", ">", "=", "~", "!", ";"):
        name = name.split(separator, 1)[0]
    return name.strip()


def _has_file_with_suffix(root: Path, suffix: str) -> bool:
    return any(path.is_file() for path in _iter_repo_files(root, f"*{suffix}"))


def _has_typescript_files(root: Path) -> bool:
    return _has_file_with_suffix(root, ".ts") or _has_file_with_suffix(root, ".tsx")


def _contains_text(root: Path, pattern: str, needle: str) -> bool:
    for path in _iter_repo_files(root, pattern):
        try:
            if needle in path.read_text(encoding="utf-8", errors="ignore"):
                return True
        except OSError:
            continue
    return False


def _iter_repo_files(root: Path, pattern: str):
    ignored_parts = {".git", ".venv", "__pycache__", "node_modules", "dist", "build"}
    for path in root.rglob(pattern):
        if path.is_file() and not ignored_parts.intersection(path.relative_to(root).parts):
            yield path
