from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from deploy_samurai.main import create_app


def test_sam_generation_endpoint_writes_downloadable_template(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("deploy_samurai.api.routes.sam.settings.artifact_root", tmp_path)

    client = TestClient(create_app())
    response = client.post(
        "/v1/sam/generate",
        json={
            "job_id": "job_123",
            "architecture": {
                "architecture_type": "modular_monolith",
                "summary": "Recommended SAM scaffold.",
                "service_candidates": [
                    {
                        "name": "api",
                        "responsibility": "Expose synchronous application APIs",
                        "runtime": "lambda",
                        "data_store": "dynamodb",
                    }
                ],
                "communication_flows": [],
                "notes": [],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["artifacts"]["template_path"].endswith("job_123/template.yaml")

    download = client.get("/v1/sam/artifacts/job_123/template.yaml")

    assert download.status_code == 200
    assert "AWS::Serverless::Function" in download.text
