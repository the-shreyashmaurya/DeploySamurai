from __future__ import annotations

from dataclasses import dataclass

from deploy_samurai.schemas.architecture import CommunicationFlow, ServiceCandidate
from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata

MAX_SERVICE_CANDIDATES = 5

DOMAIN_FOLDER_HINTS = {
    "api": "Expose synchronous HTTP endpoints and request routing",
    "auth": "Handle authentication, authorization, and identity concerns",
    "billing": "Handle billing, plans, payments, and subscription workflows",
    "jobs": "Run asynchronous background jobs and scheduled tasks",
    "notifications": "Send email, webhook, and user notification messages",
    "orders": "Manage order lifecycle and fulfillment workflows",
    "payments": "Handle payment collection and payment provider integration",
    "users": "Manage user profiles and account data",
    "worker": "Process asynchronous work outside the request path",
    "workers": "Process asynchronous work outside the request path",
}

API_FRAMEWORKS = {"fastapi", "django", "flask", "express", "nextjs"}
FRONTEND_FRAMEWORKS = {"react", "nextjs"}
ASYNC_SERVICE_NAMES = {"jobs", "notifications", "worker", "workers"}


@dataclass(frozen=True)
class BoundaryHeuristicResult:
    service_candidates: list[ServiceCandidate]
    communication_flows: list[CommunicationFlow]
    notes: list[str]


def infer_service_boundaries(metadata: NormalizedRepoMetadata) -> BoundaryHeuristicResult:
    candidates = _dedupe_candidates(
        [
            *_framework_candidates(metadata),
            *_folder_candidates(metadata),
            *_entrypoint_candidates(metadata),
        ]
    )[:MAX_SERVICE_CANDIDATES]

    if not candidates:
        candidates = [
            ServiceCandidate(
                name="application",
                responsibility="Run the application with the detected repository entrypoints",
                runtime="lambda",
            )
        ]

    flows = _infer_flows(candidates)
    notes = _build_notes(metadata, candidates)

    return BoundaryHeuristicResult(
        service_candidates=candidates,
        communication_flows=flows,
        notes=notes,
    )


def _framework_candidates(metadata: NormalizedRepoMetadata) -> list[ServiceCandidate]:
    candidates: list[ServiceCandidate] = []

    if metadata.framework in API_FRAMEWORKS:
        candidates.append(
            ServiceCandidate(
                name="api",
                responsibility="Expose synchronous application APIs through API Gateway",
                runtime="lambda",
                data_store="dynamodb",
            )
        )

    if metadata.framework in FRONTEND_FRAMEWORKS:
        candidates.append(
            ServiceCandidate(
                name="frontend",
                responsibility="Serve the web frontend and route browser traffic",
                runtime="s3-cloudfront",
            )
        )

    return candidates


def _folder_candidates(metadata: NormalizedRepoMetadata) -> list[ServiceCandidate]:
    top_level_folders = {path.split("/", 1)[0] for path in metadata.folder_paths}
    candidates: list[ServiceCandidate] = []

    for folder in sorted(top_level_folders):
        normalized = folder.lower().replace("_", "-")
        responsibility = DOMAIN_FOLDER_HINTS.get(normalized)
        if responsibility is None:
            continue

        candidates.append(
            ServiceCandidate(
                name=_service_name(normalized),
                responsibility=responsibility,
                runtime="lambda",
                data_store="dynamodb" if normalized not in ASYNC_SERVICE_NAMES else None,
            )
        )

    return candidates


def _entrypoint_candidates(metadata: NormalizedRepoMetadata) -> list[ServiceCandidate]:
    entrypoint_text = " ".join(metadata.entrypoints).lower()
    if "worker" not in entrypoint_text and "job" not in entrypoint_text:
        return []

    return [
        ServiceCandidate(
            name="worker",
            responsibility="Process asynchronous jobs and long-running tasks",
            runtime="lambda",
        )
    ]


def _infer_flows(candidates: list[ServiceCandidate]) -> list[CommunicationFlow]:
    names = {candidate.name for candidate in candidates}
    flows: list[CommunicationFlow] = []

    for target in sorted(names & ASYNC_SERVICE_NAMES):
        source = "api" if "api" in names else "application"
        flows.append(
            CommunicationFlow(
                source=source,
                target=target,
                style="async",
                transport="sqs",
            )
        )

    if "frontend" in names and "api" in names:
        flows.insert(
            0,
            CommunicationFlow(
                source="frontend",
                target="api",
                style="sync",
                transport="api_gateway",
            ),
        )

    return flows


def _build_notes(
    metadata: NormalizedRepoMetadata,
    candidates: list[ServiceCandidate],
) -> list[str]:
    notes = [
        "Service boundaries are heuristic and should be reviewed before SAM generation.",
        f"Detected {len(candidates)} candidate service(s) from repository metadata.",
    ]
    if not metadata.has_tests:
        notes.append("Repository tests were not detected; deployment confidence is lower.")
    return notes


def _dedupe_candidates(candidates: list[ServiceCandidate]) -> list[ServiceCandidate]:
    deduped: dict[str, ServiceCandidate] = {}
    for candidate in candidates:
        deduped.setdefault(candidate.name, candidate)
    return list(deduped.values())


def _service_name(value: str) -> str:
    if value == "workers":
        return "worker"
    return value
