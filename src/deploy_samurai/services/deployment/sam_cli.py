from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from deploy_samurai.schemas.deployment import DeploymentRequest, DeploymentResult

SAM_BUILD_TIMEOUT_SECONDS = 300
SAM_DEPLOY_TIMEOUT_SECONDS = 900
DEFAULT_RETRY_ATTEMPTS = 2

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class SamDeploymentError(RuntimeError):
    pass


def execute_sam_build_and_deploy(
    payload: DeploymentRequest,
    *,
    stack_name: str,
    runner: CommandRunner = subprocess.run,
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
) -> DeploymentResult:
    if not payload.confirm_deploy:
        raise SamDeploymentError("Deployment requires confirm_deploy=true.")

    template_path = Path(payload.artifact_path)
    if not template_path.exists():
        raise SamDeploymentError(f"SAM template does not exist: {template_path}")

    build_result = _run_command_with_retries(
        [
            "sam",
            "build",
            "--template-file",
            str(template_path),
        ],
        label="sam build",
        runner=runner,
        timeout=SAM_BUILD_TIMEOUT_SECONDS,
        max_attempts=retry_attempts,
    )

    deploy_result = _run_command_with_retries(
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
        label="sam deploy",
        runner=runner,
        timeout=SAM_DEPLOY_TIMEOUT_SECONDS,
        max_attempts=retry_attempts,
    )

    outputs_result = _run_command(
        [
            "aws",
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            stack_name,
            "--query",
            "Stacks[0].Outputs",
            "--output",
            "json",
        ],
        runner=runner,
        timeout=60,
    )

    outputs = {}
    output_logs = [_command_log("aws cloudformation describe-stacks", outputs_result)]
    if outputs_result.returncode == 0:
        outputs = _parse_stack_outputs(outputs_result.stdout)

    return DeploymentResult(
        deployment_id=f"dep_{uuid4().hex[:12]}",
        status="succeeded",
        stack_name=stack_name,
        outputs=outputs,
        logs=[
            _command_log("sam build", build_result),
            _command_log("sam deploy", deploy_result),
            *output_logs,
        ],
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


def _run_command_with_retries(
    command: list[str],
    *,
    label: str,
    runner: CommandRunner,
    timeout: int,
    max_attempts: int,
) -> subprocess.CompletedProcess[str]:
    attempts = max(1, max_attempts)
    last_result: subprocess.CompletedProcess[str] | None = None

    for attempt in range(1, attempts + 1):
        result = _run_command(command, runner=runner, timeout=timeout)
        if result.returncode == 0:
            return result
        last_result = result
        if attempt == attempts:
            break

    if last_result is None:
        raise SamDeploymentError(f"{label} did not run.")
    raise SamDeploymentError(f"{_command_error(label, last_result)} after {attempts} attempt(s)")


def _command_error(label: str, result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stderr or result.stdout or "Unknown SAM CLI error.").strip()
    return f"{label} failed: {output}"


def _command_log(label: str, result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stdout or result.stderr or "").strip()
    return f"{label} exited {result.returncode}: {output}"


def _parse_stack_outputs(stdout: str) -> dict[str, str]:
    try:
        values = json.loads(stdout or "[]")
    except json.JSONDecodeError:
        return {}

    if not isinstance(values, list):
        return {}

    outputs: dict[str, str] = {}
    for item in values:
        if not isinstance(item, dict):
            continue
        key = item.get("OutputKey")
        value = item.get("OutputValue")
        if key and value:
            outputs[str(key)] = str(value)
    return outputs
