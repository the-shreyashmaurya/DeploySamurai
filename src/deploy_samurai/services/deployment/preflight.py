from __future__ import annotations

from typing import Protocol

from deploy_samurai.schemas.deployment import AwsCredentialPreflightResult

DEFAULT_AWS_REGION = "us-east-1"


class AwsSessionLike(Protocol):
    region_name: str | None

    def get_credentials(self):
        pass

    def client(self, service_name: str):
        pass


def check_aws_credentials(
    session: AwsSessionLike | None = None,
    *,
    verify_identity: bool = True,
) -> AwsCredentialPreflightResult:
    aws_session = session or _create_boto3_session()
    region = aws_session.region_name or DEFAULT_AWS_REGION

    try:
        credentials = aws_session.get_credentials()
    except Exception as exc:
        return AwsCredentialPreflightResult(
            status="failed",
            region=region,
            message=f"Unable to load AWS credentials: {exc}",
        )

    if credentials is None:
        return AwsCredentialPreflightResult(
            status="failed",
            region=region,
            message="AWS credentials were not found.",
        )

    if not verify_identity:
        return AwsCredentialPreflightResult(
            status="passed",
            region=region,
            message="AWS credentials are available.",
        )

    try:
        identity = aws_session.client("sts").get_caller_identity()
    except Exception as exc:
        return AwsCredentialPreflightResult(
            status="failed",
            region=region,
            message=f"AWS credentials could not call STS: {exc}",
        )

    return AwsCredentialPreflightResult(
        status="passed",
        region=region,
        account_id=identity.get("Account"),
        arn=identity.get("Arn"),
        message="AWS credentials are valid.",
    )


def _create_boto3_session() -> AwsSessionLike:
    import boto3
    from deploy_samurai.core.config import settings

    return boto3.Session(region_name=settings.aws_region)
