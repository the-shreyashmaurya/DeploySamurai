from __future__ import annotations

from typing import Protocol

from deploy_samurai.schemas.verification import VerificationCheck
from deploy_samurai.services.verification.evidence import build_evidence

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
        detail = f"Unable to describe stack {stack_name}: {exc}"
        return VerificationCheck(
            name="stack_status",
            status="failed",
            evidence=detail,
            evidence_items=[
                build_evidence(
                    source="cloudformation.describe_stacks",
                    detail=detail,
                    metadata={"stack_name": stack_name},
                )
            ],
        )

    stacks = response.get("Stacks", [])
    if not stacks:
        detail = f"Stack {stack_name} was not found."
        return VerificationCheck(
            name="stack_status",
            status="failed",
            evidence=detail,
            evidence_items=[
                build_evidence(
                    source="cloudformation.describe_stacks",
                    detail=detail,
                    metadata={"stack_name": stack_name},
                )
            ],
        )

    status = str(stacks[0].get("StackStatus", "UNKNOWN"))
    check_status = "passed" if status in SUCCESSFUL_STACK_STATUSES else "failed"
    detail = f"Stack {stack_name} status is {status}."
    return VerificationCheck(
        name="stack_status",
        status=check_status,
        evidence=detail,
        evidence_items=[
            build_evidence(
                source="cloudformation.describe_stacks",
                detail=detail,
                metadata={"stack_name": stack_name, "stack_status": status},
            )
        ],
    )
