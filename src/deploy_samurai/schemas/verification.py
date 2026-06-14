from typing import Literal

from pydantic import BaseModel


class VerificationRequest(BaseModel):
    job_id: str
    deployment_id: str
    expected_endpoints: list[str]


class VerificationCheck(BaseModel):
    name: str
    status: Literal["passed", "failed", "skipped"]
    evidence: str | None = None


class VerificationResponse(BaseModel):
    status: Literal["passed", "failed"]
    checks: list[VerificationCheck]
