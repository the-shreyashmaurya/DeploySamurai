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

    with pytest.raises(SamDeploymentError, match="sam build failed: bad template"):
        execute_sam_build_and_deploy(
            DeploymentRequest(
                job_id="job_123",
                artifact_path=str(template_path),
                confirm_deploy=True,
            ),
            stack_name="deploy-samurai-dev",
            runner=runner,
        )
