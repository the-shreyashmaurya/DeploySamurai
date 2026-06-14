from deploy_samurai.schemas.architecture import ArchitectureReasoningResponse
from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata
from deploy_samurai.services.architecture_reasoning.summary import generate_architecture_summary


class FakeSummaryProvider:
    def summarize(
        self,
        metadata: NormalizedRepoMetadata,
        response: ArchitectureReasoningResponse,
    ) -> str:
        return f"AI summary for {metadata.name}: {response.architecture_type}"


def test_generate_architecture_summary_returns_validated_response() -> None:
    metadata = NormalizedRepoMetadata(
        name="demo-api",
        language="python",
        framework="fastapi",
        package_manager="uv",
        has_tests=True,
        folder_paths=["app", "workers", "tests"],
        entrypoints=["app/main.py", "workers/main.py"],
    )

    response = generate_architecture_summary(metadata)

    assert response.architecture_type == "microservices"
    assert response.summary.startswith("demo-api is best approached as microservices")
    assert [service.name for service in response.service_candidates] == ["api", "worker"]
    assert response.communication_flows[0].style == "async"
    assert "At least one asynchronous flow suggests a separate worker boundary." in response.notes

    dumped = response.model_dump(by_alias=True)
    assert dumped == {
        "architecture_type": "microservices",
        "summary": response.summary,
        "service_candidates": [
            {
                "name": "api",
                "responsibility": "Expose synchronous application APIs through API Gateway",
                "runtime": "lambda",
                "data_store": "dynamodb",
            },
            {
                "name": "worker",
                "responsibility": "Process asynchronous work outside the request path",
                "runtime": "lambda",
                "data_store": None,
            },
        ],
        "communication_flows": [
            {
                "from": "api",
                "to": "worker",
                "style": "async",
                "transport": "sqs",
            }
        ],
        "notes": response.notes,
    }


def test_generate_architecture_summary_can_use_optional_summary_provider() -> None:
    metadata = NormalizedRepoMetadata(
        name="simple-app",
        framework="fastapi",
        has_tests=True,
        folder_paths=["app"],
        entrypoints=["app/main.py"],
    )

    response = generate_architecture_summary(metadata, summary_provider=FakeSummaryProvider())

    assert response.summary == "AI summary for simple-app: modular_monolith"
    assert response.architecture_type == "modular_monolith"


def test_generate_architecture_summary_falls_back_for_unknown_repo_shape() -> None:
    metadata = NormalizedRepoMetadata(name="mystery")

    response = generate_architecture_summary(metadata)

    assert response.architecture_type == "modular_monolith"
    assert response.service_candidates[0].name == "application"
    assert response.communication_flows == []
    assert "Only one candidate service was detected." in response.notes
