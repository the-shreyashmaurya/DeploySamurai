from __future__ import annotations

from deploy_samurai.schemas.verification import VerificationCheck, VerificationRequest, VerificationResponse
from deploy_samurai.services.verification.evidence import build_evidence
from deploy_samurai.services.verification.smoke import EndpointClientLike, check_endpoint_health
from deploy_samurai.services.verification.stack_status import CloudFormationClientLike, check_stack_status


def skipped_check(name: str, detail: str) -> VerificationCheck:
    return VerificationCheck(
        name=name,
        status="skipped",
        evidence=detail,
        evidence_items=[build_evidence(source="verification.workflow", detail=detail)],
    )


def summarize_verification(checks: list[VerificationCheck]) -> str:
    return "failed" if any(check.status == "failed" for check in checks) else "passed"


def run_verification(
    request: VerificationRequest,
    cloudformation_client: CloudFormationClientLike | None = None,
    endpoint_client: EndpointClientLike | None = None,
) -> VerificationResponse:
    checks: list[VerificationCheck] = []

    if request.stack_name and cloudformation_client is not None:
        checks.append(check_stack_status(request.stack_name, cloudformation_client))
    else:
        checks.append(
            skipped_check(
                "stack_status",
                "Stack status check skipped because stack_name or CloudFormation client was not provided.",
            )
        )

    if request.base_url:
        checks.extend(
            check_endpoint_health(request.base_url, endpoint_path, endpoint_client)
            for endpoint_path in request.expected_endpoints
        )
    elif request.expected_endpoints:
        checks.append(
            skipped_check(
                "endpoint_smoke",
                "Endpoint smoke checks skipped because base_url was not provided.",
            )
        )

    return VerificationResponse(status=summarize_verification(checks), checks=checks)
