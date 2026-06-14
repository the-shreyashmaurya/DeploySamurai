from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SupportedLanguage = Literal["python", "javascript", "typescript", "unknown"]
SupportedFramework = Literal[
    "fastapi",
    "django",
    "flask",
    "nextjs",
    "react",
    "express",
    "unknown",
]
SupportedPackageManager = Literal[
    "uv",
    "poetry",
    "pipenv",
    "pip",
    "pnpm",
    "yarn",
    "npm",
    "unknown",
]


class NormalizedRepoMetadata(BaseModel):
    name: str
    default_branch: str | None = None
    language: SupportedLanguage = "unknown"
    framework: SupportedFramework = "unknown"
    package_manager: SupportedPackageManager = "unknown"
    has_tests: bool = False
    root_files: list[str] = Field(default_factory=list)
    folder_paths: list[str] = Field(default_factory=list)
    entrypoints: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)


class NormalizedRepoMetadataEnvelope(BaseModel):
    job_id: str
    repo_url: str
    metadata: NormalizedRepoMetadata
