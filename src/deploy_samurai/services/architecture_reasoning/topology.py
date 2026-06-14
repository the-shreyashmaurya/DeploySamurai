from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from deploy_samurai.schemas.architecture import CommunicationFlow, ServiceCandidate
from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata

ArchitectureType = Literal["modular_monolith", "microservices"]


@dataclass(frozen=True)
class ArchitectureTypeDecision:
    architecture_type: ArchitectureType
    rationale: list[str]


def decide_architecture_type(
    metadata: NormalizedRepoMetadata,
    service_candidates: list[ServiceCandidate],
    communication_flows: list[CommunicationFlow],
) -> ArchitectureTypeDecision:
    service_count = len(service_candidates)
    has_async_flow = any(flow.style == "async" for flow in communication_flows)
    has_clear_domains = service_count >= 3
    has_containerized_services = any(service.runtime == "container" for service in service_candidates)

    if service_count <= 1:
        return ArchitectureTypeDecision(
            architecture_type="modular_monolith",
            rationale=[
                "Only one candidate service was detected.",
                "Start with a modular monolith and keep boundaries internal.",
            ],
        )

    if has_containerized_services and service_count >= 3:
        reasons = [
            "Multiple containerized service candidates were detected.",
            "The repository shape matches an independently deployable microservice system.",
        ]
        if not metadata.has_tests:
            reasons.append("Repository tests were not detected; deployment confidence is lower.")
        return ArchitectureTypeDecision(
            architecture_type="microservices",
            rationale=reasons,
        )

    if not metadata.has_tests:
        return ArchitectureTypeDecision(
            architecture_type="modular_monolith",
            rationale=[
                "Multiple candidates were found, but tests were not detected.",
                "Prefer a modular monolith until behavior is safer to split.",
            ],
        )

    if has_clear_domains or has_async_flow:
        reasons = ["Multiple independently deployable service candidates were detected."]
        if has_async_flow:
            reasons.append("At least one asynchronous flow suggests a separate worker boundary.")
        return ArchitectureTypeDecision(
            architecture_type="microservices",
            rationale=reasons,
        )

    return ArchitectureTypeDecision(
        architecture_type="modular_monolith",
        rationale=[
            "Candidate boundaries exist, but the repository shape is still simple.",
            "Keep one deployable unit while preserving module boundaries.",
        ],
    )
