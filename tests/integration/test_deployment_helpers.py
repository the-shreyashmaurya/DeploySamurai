import subprocess
from pathlib import Path

from deploy_samurai.schemas.architecture import ArchitectureReasoningResponse, ServiceCandidate
from deploy_samurai.schemas.deployment import DeploymentRequest
from deploy_samurai.schemas.sam_generation import SamGenerationRequest
from deploy_samurai.services.deployment.preflight import check_aws_credentials
from deploy_samurai.services.deployment.sam_cli import execute_sam_build_and_deploy
from deploy_samurai.services.sam_generation.template import generate_sam_template


class FakeCredentials:
    pass


class FakeStsClient:
    def get_caller_identity(self):
        return {
            "Account": "123456789012",
            "Arn": "arn:aws:iam::123456789012:user/tester",
        }


class FakeAwsSession:
    region_name = "us-east-1"

    def get_credentials(self):
        return FakeCredentials()

    def client(self, service_name: str):
        assert service_name == "sts"
        return FakeStsClient()


def test_deployment_helpers_support_advisor_to_sam_deploy_flow(tmp_path: Path) -> None:
    preflight = check_aws_credentials(FakeAwsSession())
    sam_artifacts = generate_sam_template(
        SamGenerationRequest(
            job_id="job_123",
            architecture=ArchitectureReasoningResponse(
                architecture_type="modular_monolith",
                service_candidates=[
                    ServiceCandidate(
                        name="api",
                        responsibility="Expose API requests",
                        data_store="dynamodb",
                    )
                ],
            ),
        ),
        output_root=tmp_path,
    )

    def runner(command, **kwargs):  # type: ignore[no-untyped-def]
        if command[:3] == ["aws", "cloudformation", "describe-stacks"]:
            return subprocess.CompletedProcess(
                command,
                returncode=0,
                stdout='[{"OutputKey": "ApiUrl", "OutputValue": "https://example.test"}]',
                stderr="",
            )
        return subprocess.CompletedProcess(command, returncode=0, stdout="ok", stderr="")

    deployment = execute_sam_build_and_deploy(
        DeploymentRequest(
            job_id="job_123",
            artifact_path=sam_artifacts.artifacts.template_path,
            confirm_deploy=True,
        ),
        stack_name="deploy-samurai-dev",
        runner=runner,
    )

    assert preflight.status == "passed"
    assert Path(sam_artifacts.artifacts.template_path).exists()
    assert deployment.status == "succeeded"
    assert deployment.outputs == {"ApiUrl": "https://example.test"}
    assert len(deployment.logs) == 3
