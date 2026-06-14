from fastapi.testclient import TestClient

from deploy_samurai.main import create_app


def test_reasoning_endpoint_returns_validated_architecture_payload() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/reason/architecture",
        json={
            "job_id": "job_123",
            "repo_summary": {
                "name": "demo-api",
                "language": "python",
                "framework": "fastapi",
                "package_manager": "uv",
                "has_tests": True,
            },
            "structure": {
                "root_files": ["pyproject.toml"],
                "folder_tree": ["app", "workers", "tests"],
                "entrypoints": ["app/main.py", "workers/main.py"],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["architecture_type"] == "microservices"
    assert body["summary"]
    assert [service["name"] for service in body["service_candidates"]] == ["api", "worker"]
    assert body["communication_flows"][0] == {
        "from": "api",
        "to": "worker",
        "style": "async",
        "transport": "sqs",
    }
    assert "notes" in body
