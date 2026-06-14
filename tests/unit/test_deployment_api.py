import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from deploy_samurai.main import create_app
from deploy_samurai.schemas.deployment import AwsCredentialPreflightResult


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
