from pathlib import Path

import pytest

from deploy_samurai.services.repo_analysis.stack_detection import detect_stack


def test_detect_stack_identifies_python_fastapi_uv(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
dependencies = ["fastapi>=0.112", "sqlalchemy"]
""",
        encoding="utf-8",
    )
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")

    detection = detect_stack(tmp_path)

    assert detection.language == "python"
    assert detection.framework == "fastapi"
    assert detection.package_manager == "uv"


def test_detect_stack_identifies_nextjs_typescript_pnpm(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        """
{
  "dependencies": {
    "next": "latest",
    "react": "latest"
  }
}
""",
        encoding="utf-8",
    )
    (tmp_path / "pnpm-lock.yaml").write_text("", encoding="utf-8")
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "page.tsx").write_text("export default function Page() {}", encoding="utf-8")

    detection = detect_stack(tmp_path)

    assert detection.language == "typescript"
    assert detection.framework == "nextjs"
    assert detection.package_manager == "pnpm"


def test_detect_stack_identifies_express_javascript_npm(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        """
{
  "dependencies": {
    "express": "^4.18.0"
  }
}
""",
        encoding="utf-8",
    )
    (tmp_path / "package-lock.json").write_text("", encoding="utf-8")
    (tmp_path / "server.js").write_text("const app = express()", encoding="utf-8")

    detection = detect_stack(tmp_path)

    assert detection.language == "javascript"
    assert detection.framework == "express"
    assert detection.package_manager == "npm"


def test_detect_stack_ignores_invalid_manifest_content(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("not valid toml", encoding="utf-8")
    (tmp_path / "package.json").write_text("{", encoding="utf-8")

    detection = detect_stack(tmp_path)

    assert detection.language == "python"
    assert detection.framework is None
    assert detection.package_manager == "npm"


def test_detect_stack_requires_existing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        detect_stack(tmp_path / "missing")


def test_detect_stack_rejects_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "README.md"
    file_path.write_text("# Demo", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        detect_stack(file_path)
