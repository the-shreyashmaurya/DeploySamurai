from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata
from deploy_samurai.services.architecture_reasoning.boundaries import infer_service_boundaries


def test_infer_service_boundaries_for_fastapi_with_worker() -> None:
    metadata = NormalizedRepoMetadata(
        name="demo-api",
        language="python",
        framework="fastapi",
        package_manager="uv",
        has_tests=True,
        folder_paths=["app", "workers", "tests"],
        entrypoints=["app/main.py", "workers/main.py"],
    )

    result = infer_service_boundaries(metadata)

    assert [service.name for service in result.service_candidates] == ["api", "worker"]
    assert result.service_candidates[0].data_store == "dynamodb"
    assert result.communication_flows[0].model_dump(by_alias=True) == {
        "from": "api",
        "to": "worker",
        "style": "async",
        "transport": "sqs",
    }
    assert "Detected 2 candidate service(s) from repository metadata." in result.notes


def test_infer_service_boundaries_for_nextjs_frontend_and_api() -> None:
    metadata = NormalizedRepoMetadata(
        name="web-app",
        language="typescript",
        framework="nextjs",
        package_manager="pnpm",
        has_tests=True,
        folder_paths=["app", "api", "components"],
        entrypoints=["app/page.tsx"],
    )

    result = infer_service_boundaries(metadata)

    assert [service.name for service in result.service_candidates] == ["api", "frontend"]
    assert result.communication_flows[0].model_dump(by_alias=True) == {
        "from": "frontend",
        "to": "api",
        "style": "sync",
        "transport": "api_gateway",
    }


def test_infer_service_boundaries_falls_back_to_application_service() -> None:
    metadata = NormalizedRepoMetadata(
        name="unknown",
        folder_paths=["lib"],
        entrypoints=[],
    )

    result = infer_service_boundaries(metadata)

    assert [service.name for service in result.service_candidates] == ["application"]
    assert result.communication_flows == []
    assert "Repository tests were not detected; deployment confidence is lower." in result.notes


def test_infer_service_boundaries_limits_candidate_count() -> None:
    metadata = NormalizedRepoMetadata(
        name="large-app",
        framework="fastapi",
        has_tests=True,
        folder_paths=["auth", "billing", "jobs", "notifications", "orders", "payments", "users"],
    )

    result = infer_service_boundaries(metadata)

    assert len(result.service_candidates) == 5
    assert [service.name for service in result.service_candidates] == [
        "api",
        "auth",
        "billing",
        "jobs",
        "notifications",
    ]
