from __future__ import annotations

from typing import Protocol

from deploy_samurai.schemas.verification import VerificationCheck

SUCCESSFUL_STACK_STATUSES = {
    "CREATE_COMPLETE",
    "UPDATE_COMPLETE",
    "UPDATE_ROLLBACK_COMPLETE",
}


class CloudFormationClientLike(Protocol):
    def describe_stacks(self, StackName: str):
        pass


def check_stack_status(
    stack_name: str,
    cloudformation_client: CloudFormationClientLike,
) -> VerificationCheck:
    try:
        response = cloudformation_client.describe_stacks(StackName=stack_name)
    except Exception as exc:
        return VerificationCheck(
            name="stack_status",
            status="failed",
            evidence=f"Unable to describe stack {stack_name}: {exc}",
        )

    stacks = response.get("Stacks", [])
    if not stacks:
        return VerificationCheck(
            name="stack_status",
            status="failed",
            evidence=f"Stack {stack_name} was not found.",
        )

    status = str(stacks[0].get("StackStatus", "UNKNOWN"))
    check_status = "passed" if status in SUCCESSFUL_STACK_STATUSES else "failed"
    return VerificationCheck(
        name="stack_status",
        status=check_status,
        evidence=f"Stack {stack_name} status is {status}.",
    )
