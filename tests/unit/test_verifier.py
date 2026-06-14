from dataclasses import dataclass

from deploy_samurai.schemas.verification import VerificationRequest
from deploy_samurai.services.verification.verifier import run_verification


class FakeCloudFormationClient:
    def __init__(self, status: str) -> None:
        self.status = status

    def describe_stacks(self, StackName: str):
        return {"Stacks": [{"StackName": StackName, "StackStatus": self.status}]}


@dataclass
class FakeResponse:
    status_code: int


class FakeEndpointClient:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code

    def get(self, url: str, timeout: float = 10.0) -> FakeResponse:
        return FakeResponse(status_code=self.status_code)


def test_run_verification_returns_passed_when_all_checks_pass() -> None:
    response = run_verification(
        VerificationRequest(
            job_id="job_123",
            deployment_id="dep_123",
            stack_name="deploy-samurai-dev",
            base_url="https://api.example.com",
            expected_endpoints=["/health"],
        ),
        cloudformation_client=FakeCloudFormationClient("CREATE_COMPLETE"),
        endpoint_client=FakeEndpointClient(200),
    )

    assert response.status == "passed"
    assert [check.status for check in response.checks] == ["passed", "passed"]


def test_run_verification_returns_failed_when_any_check_fails() -> None:
    response = run_verification(
        VerificationRequest(
            job_id="job_123",
            deployment_id="dep_123",
            stack_name="deploy-samurai-dev",
            base_url="https://api.example.com",
            expected_endpoints=["/health"],
        ),
        cloudformation_client=FakeCloudFormationClient("ROLLBACK_COMPLETE"),
        endpoint_client=FakeEndpointClient(200),
    )

    assert response.status == "failed"
    assert response.checks[0].status == "failed"
    assert response.checks[1].status == "passed"


def test_run_verification_returns_skipped_checks_for_missing_runtime_clients() -> None:
    response = run_verification(
        VerificationRequest(
            job_id="job_123",
            deployment_id="dep_123",
            expected_endpoints=["/health"],
        )
    )

    assert response.status == "passed"
    assert [check.status for check in response.checks] == ["skipped", "skipped"]
    assert all(check.evidence_items for check in response.checks)
