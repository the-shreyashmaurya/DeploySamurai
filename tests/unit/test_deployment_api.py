import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from deploy_samurai.main import create_app
from deploy_samurai.schemas.deployment import AwsCredentialPreflightResult, DeploymentResult


def test_deployment_preflight_endpoint_returns_aws_readiness(monkeypatch) -> None:
    def fake_check_aws_credentials() -> AwsCredentialPreflightResult:
        return AwsCredentialPreflightResult(
            status="passed",
            region="us-east-1",
            account_id="123456789012",
            arn="arn:aws:iam::123456789012:user/deploy-samurai",
            message="AWS credentials are valid.",
        )

    monkeypatch.setattr(
        "deploy_samurai.api.routes.deployment.check_aws_credentials",
        fake_check_aws_credentials,
    )

    client = TestClient(create_app())
    response = client.post("/v1/deploy/preflight")

    assert response.status_code == 200
    assert response.json() == {
        "status": "passed",
        "region": "us-east-1",
        "account_id": "123456789012",
        "arn": "arn:aws:iam::123456789012:user/deploy-samurai",
        "message": "AWS credentials are valid.",
    }


def test_deploy_sam_endpoint_requires_preflight(monkeypatch) -> None:
    def fake_check_aws_credentials() -> AwsCredentialPreflightResult:
        return AwsCredentialPreflightResult(
            status="failed",
            region="us-east-1",
            message="AWS credentials were not found.",
        )

    monkeypatch.setattr(
        "deploy_samurai.api.routes.deployment.check_aws_credentials",
        fake_check_aws_credentials,
    )

    client = TestClient(create_app())
    response = client.post(
        "/v1/deploy/sam",
        json={
            "job_id": "job_123",
            "artifact_path": "artifacts/job_123/template.yaml",
            "confirm_deploy": True,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "AWS credentials were not found."}


def test_deploy_sam_endpoint_runs_approved_deployment(monkeypatch) -> None:
    def fake_check_aws_credentials() -> AwsCredentialPreflightResult:
        return AwsCredentialPreflightResult(
            status="passed",
            region="us-east-1",
            account_id="123456789012",
            message="AWS credentials are valid.",
        )

    def fake_execute_sam_build_and_deploy(
        payload,
        *,
        stack_name: str,
    ) -> DeploymentResult:
        return DeploymentResult(
            deployment_id="dep_123",
            status="succeeded",
            stack_name=stack_name,
            outputs={"ApiUrl": "https://api.example.com"},
            logs=["sam build exited 0: ok", "sam deploy exited 0: ok"],
        )

    monkeypatch.setattr(
        "deploy_samurai.api.routes.deployment.check_aws_credentials",
        fake_check_aws_credentials,
    )
    monkeypatch.setattr(
        "deploy_samurai.api.routes.deployment.execute_sam_build_and_deploy",
        fake_execute_sam_build_and_deploy,
    )

    client = TestClient(create_app())
    response = client.post(
        "/v1/deploy/sam",
        json={
            "job_id": "job_123",
            "artifact_path": "artifacts/job_123/template.yaml",
            "confirm_deploy": True,
            "stack_name": "deploy-samurai-demo",
        },
    )

    assert response.status_code == 200
    assert response.json()["deployment_id"] == "dep_123"
    assert response.json()["stack_name"] == "deploy-samurai-demo"
