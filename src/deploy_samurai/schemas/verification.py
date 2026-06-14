from typing import Literal

from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):
    job_id: str
    deployment_id: str
    expected_endpoints: list[str]


class VerificationEvidence(BaseModel):
    source: str
    detail: str
    metadata: dict[str, str] = Field(default_factory=dict)


class VerificationCheck(BaseModel):
    name: str
    status: Literal["passed", "failed", "skipped"]
    evidence: str | None = None
    evidence_items: list[VerificationEvidence] = Field(default_factory=list)


class VerificationResponse(BaseModel):
    status: Literal["passed", "failed"]
    checks: list[VerificationCheck]
