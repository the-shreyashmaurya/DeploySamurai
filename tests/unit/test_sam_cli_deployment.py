import subprocess
from pathlib import Path

import pytest

from deploy_samurai.schemas.deployment import DeploymentRequest
from deploy_samurai.services.deployment.sam_cli import (
    SamDeploymentError,
    execute_sam_build_and_deploy,
)


def test_execute_sam_build_and_deploy_runs_expected_commands(tmp_path: Path) -> None:
    template_path = tmp_path / "template.yaml"
    template_path.write_text("Transform: AWS::Serverless-2016-10-31", encoding="utf-8")
    calls = []

    def runner(command, **kwargs):  # type: ignore[no-untyped-def]
        calls.append((command, kwargs))
        if command[:3] == ["aws", "cloudformation", "describe-stacks"]:
            return subprocess.CompletedProcess(
                command,
                returncode=0,
                stdout='[{"OutputKey": "ApiUrl", "OutputValue": "https://example.test"}]',
                stderr="",
            )
        return subprocess.CompletedProcess(command, returncode=0, stdout="ok", stderr="")

    response = execute_sam_build_and_deploy(
        DeploymentRequest(
            job_id="job_123",
            artifact_path=str(template_path),
            confirm_deploy=True,
        ),
        stack_name="deploy-samurai-dev",
        runner=runner,
    )

    assert response.status == "succeeded"
    assert response.stack_name == "deploy-samurai-dev"
    assert response.outputs == {"ApiUrl": "https://example.test"}
    assert response.logs[0] == "sam build exited 0: ok"
    assert response.logs[1] == "sam deploy exited 0: ok"
    assert calls[0][0] == ["sam", "build", "--template-file", str(template_path)]
    assert calls[1][0] == [
        "sam",
        "deploy",
        "--stack-name",
        "deploy-samurai-dev",
        "--no-confirm-changeset",
        "--no-fail-on-empty-changeset",
        "--capabilities",
        "CAPABILITY_IAM",
    ]
    assert calls[2][0] == [
        "aws",
        "cloudformation",
        "describe-stacks",
        "--stack-name",
        "deploy-samurai-dev",
        "--query",
        "Stacks[0].Outputs",
        "--output",
        "json",
    ]


def test_execute_sam_build_and_deploy_requires_confirmation(tmp_path: Path) -> None:
    template_path = tmp_path / "template.yaml"
    template_path.write_text("Transform: AWS::Serverless-2016-10-31", encoding="utf-8")

    with pytest.raises(SamDeploymentError, match="confirm_deploy=true"):
        execute_sam_build_and_deploy(
            DeploymentRequest(
                job_id="job_123",
                artifact_path=str(template_path),
                confirm_deploy=False,
            ),
            stack_name="deploy-samurai-dev",
        )


def test_execute_sam_build_and_deploy_surfaces_build_failure(tmp_path: Path) -> None:
    template_path = tmp_path / "template.yaml"
    template_path.write_text("Transform: AWS::Serverless-2016-10-31", encoding="utf-8")

    def runner(command, **kwargs):  # type: ignore[no-untyped-def]
        return subprocess.CompletedProcess(command, returncode=1, stdout="", stderr="bad template")

    with pytest.raises(SamDeploymentError, match="sam build failed: bad template after 2 attempt"):
        execute_sam_build_and_deploy(
            DeploymentRequest(
                job_id="job_123",
                artifact_path=str(template_path),
                confirm_deploy=True,
            ),
            stack_name="deploy-samurai-dev",
            runner=runner,
        )


def test_execute_sam_build_and_deploy_retries_failed_deploy(tmp_path: Path) -> None:
    template_path = tmp_path / "template.yaml"
    template_path.write_text("Transform: AWS::Serverless-2016-10-31", encoding="utf-8")
    deploy_attempts = 0

    def runner(command, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal deploy_attempts
        if command[:2] == ["sam", "build"]:
            return subprocess.CompletedProcess(command, returncode=0, stdout="build ok", stderr="")
        if command[:2] == ["sam", "deploy"]:
            deploy_attempts += 1
            if deploy_attempts == 1:
                return subprocess.CompletedProcess(command, returncode=1, stdout="", stderr="busy")
            return subprocess.CompletedProcess(command, returncode=0, stdout="deploy ok", stderr="")
        return subprocess.CompletedProcess(command, returncode=0, stdout="[]", stderr="")

    response = execute_sam_build_and_deploy(
        DeploymentRequest(
            job_id="job_123",
            artifact_path=str(template_path),
            confirm_deploy=True,
        ),
        stack_name="deploy-samurai-dev",
        runner=runner,
        retry_attempts=2,
    )

    assert response.status == "succeeded"
    assert deploy_attempts == 2
