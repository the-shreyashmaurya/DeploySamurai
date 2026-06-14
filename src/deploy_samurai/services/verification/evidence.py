from __future__ import annotations

from deploy_samurai.schemas.verification import VerificationEvidence


def build_evidence(
    source: str,
    detail: str,
    metadata: dict[str, str] | None = None,
) -> VerificationEvidence:
    return VerificationEvidence(source=source, detail=detail, metadata=metadata or {})
