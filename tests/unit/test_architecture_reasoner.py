from deploy_samurai.schemas.architecture import ArchitectureReasoningRequest
from deploy_samurai.schemas.architecture import ArchitectureReasoningResponse
from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata
from deploy_samurai.schemas.repo_analysis import RepoStructure, RepoSummary
from deploy_samurai.services.architecture_reasoning.reasoner import reason_about_architecture


class FakeSummaryProvider:
    def summarize(
        self,
        metadata: NormalizedRepoMetadata,
        response: ArchitectureReasoningResponse,
    ) -> str:
        return f"OpenAI-backed summary for {metadata.name}"


def test_reason_about_architecture_returns_validated_summary() -> None:
    response = reason_about_architecture(
        ArchitectureReasoningRequest(
            job_id="job_123",
            repo_summary=RepoSummary(
                name="demo-api",
                language="python",
                framework="fastapi",
                package_manager="uv",
                has_tests=True,
            ),
            structure=RepoStructure(
                root_files=["pyproject.toml"],
                folder_tree=["app", "workers", "tests"],
                entrypoints=["app/main.py", "workers/main.py"],
            ),
        )
    )

    assert response.architecture_type == "microservices"
    assert response.service_candidates[0].name == "api"
    assert response.communication_flows[0].source == "api"
    assert response.communication_flows[0].target == "worker"


def test_reason_about_architecture_uses_configured_summary_provider() -> None:
    response = reason_about_architecture(
        ArchitectureReasoningRequest(
            job_id="job_123",
            repo_summary=RepoSummary(
                name="demo-api",
                language="python",
                framework="fastapi",
                package_manager="uv",
                has_tests=True,
            ),
            structure=RepoStructure(
                folder_tree=["app"],
                entrypoints=["app/main.py"],
            ),
        ),
        summary_provider=FakeSummaryProvider(),
    )

    assert response.summary == "OpenAI-backed summary for demo-api"
