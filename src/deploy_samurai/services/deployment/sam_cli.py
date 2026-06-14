from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from deploy_samurai.schemas.deployment import DeploymentCreateResponse, DeploymentRequest

SAM_BUILD_TIMEOUT_SECONDS = 300
SAM_DEPLOY_TIMEOUT_SECONDS = 900

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class SamDeploymentError(RuntimeError):
    pass


def execute_sam_build_and_deploy(
    payload: DeploymentRequest,
    *,
    stack_name: str,
    runner: CommandRunner = subprocess.run,
) -> DeploymentCreateResponse:
    if not payload.confirm_deploy:
        raise SamDeploymentError("Deployment requires confirm_deploy=true.")

    template_path = Path(payload.artifact_path)
    if not template_path.exists():
        raise SamDeploymentError(f"SAM template does not exist: {template_path}")

    build_result = _run_command(
        [
            "sam",
            "build",
            "--template-file",
            str(template_path),
        ],
        runner=runner,
        timeout=SAM_BUILD_TIMEOUT_SECONDS,
    )
    if build_result.returncode != 0:
        raise SamDeploymentError(_command_error("sam build", build_result))

    deploy_result = _run_command(
        [
            "sam",
            "deploy",
            "--stack-name",
            stack_name,
            "--no-confirm-changeset",
            "--no-fail-on-empty-changeset",
            "--capabilities",
            "CAPABILITY_IAM",
        ],
        runner=runner,
        timeout=SAM_DEPLOY_TIMEOUT_SECONDS,
    )
    if deploy_result.returncode != 0:
        raise SamDeploymentError(_command_error("sam deploy", deploy_result))

    return DeploymentCreateResponse(
        deployment_id=f"dep_{uuid4().hex[:12]}",
        status="succeeded",
        stack_name=stack_name,
    )


def _run_command(
    command: list[str],
    *,
    runner: CommandRunner,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    try:
        return runner(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise SamDeploymentError(f"Command timed out: {' '.join(command)}") from exc
    except OSError as exc:
        raise SamDeploymentError(f"Command failed to start: {' '.join(command)}: {exc}") from exc


def _command_error(label: str, result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stderr or result.stdout or "Unknown SAM CLI error.").strip()
    return f"{label} failed: {output}"
