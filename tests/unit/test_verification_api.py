import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from deploy_samurai.main import create_app


def test_verification_endpoint_returns_machine_readable_result() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/verify",
        json={
            "job_id": "job_123",
            "deployment_id": "dep_123",
            "expected_endpoints": ["/health"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "passed"
    assert body["checks"][0]["name"] == "stack_status"
    assert body["checks"][0]["status"] == "skipped"
    assert body["checks"][0]["evidence_items"][0]["source"] == "verification.workflow"
