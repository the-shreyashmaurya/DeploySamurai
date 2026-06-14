from pydantic import ValidationError
import pytest

from deploy_samurai.schemas.verification import (
    VerificationCheck,
    VerificationEvidence,
    VerificationRequest,
    VerificationResponse,
)


def test_verification_request_accepts_runtime_deployment_targets() -> None:
    payload = VerificationRequest(
        job_id="job_123",
        deployment_id="dep_123",
        stack_name="deploy-samurai-dev",
        base_url="https://api.example.com",
        expected_endpoints=["/health", "/ready"],
    )

    assert payload.stack_name == "deploy-samurai-dev"
    assert payload.base_url == "https://api.example.com"
    assert payload.expected_endpoints == ["/health", "/ready"]


def test_verification_response_serializes_machine_readable_checks() -> None:
    response = VerificationResponse(
        status="passed",
        checks=[
            VerificationCheck(
                name="endpoint_smoke:/health",
                status="passed",
                evidence="GET https://api.example.com/health returned HTTP 200.",
                evidence_items=[
                    VerificationEvidence(
                        source="http.get",
                        detail="GET https://api.example.com/health returned HTTP 200.",
                        metadata={
                            "url": "https://api.example.com/health",
                            "status_code": "200",
                        },
                    )
                ],
            )
        ],
    )

    assert response.model_dump() == {
        "status": "passed",
        "checks": [
            {
                "name": "endpoint_smoke:/health",
                "status": "passed",
                "evidence": "GET https://api.example.com/health returned HTTP 200.",
                "evidence_items": [
                    {
                        "source": "http.get",
                        "detail": "GET https://api.example.com/health returned HTTP 200.",
                        "metadata": {
                            "url": "https://api.example.com/health",
                            "status_code": "200",
                        },
                    }
                ],
            }
        ],
    }


def test_verification_response_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        VerificationResponse(status="unknown", checks=[])
