from pydantic import BaseModel, Field


class RepoSummary(BaseModel):
    name: str
    default_branch: str | None = None
    language: str | None = None
    framework: str | None = None
    package_manager: str | None = None
    has_tests: bool = False


class RepoStructure(BaseModel):
    root_files: list[str] = Field(default_factory=list)
    folder_tree: list[str] = Field(default_factory=list)
    entrypoints: list[str] = Field(default_factory=list)


class RepoAnalysisRequest(BaseModel):
    repo_url: str
    job_id: str


class RepoAnalysisResponse(BaseModel):
    repo_summary: RepoSummary
    structure: RepoStructure
