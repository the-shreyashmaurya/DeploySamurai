from __future__ import annotations

from dataclasses import dataclass

from deploy_samurai.schemas.architecture import CommunicationFlow, ServiceCandidate
from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata

MAX_SERVICE_CANDIDATES = 10

DOMAIN_FOLDER_HINTS = {
    "api": "Expose synchronous HTTP endpoints and request routing",
    "api-gateway": "Route external traffic to internal services",
    "auth": "Handle authentication, authorization, and identity concerns",
    "billing": "Handle billing, plans, payments, and subscription workflows",
    "config": "Centralize runtime configuration for services",
    "consul": "Provide service discovery and cluster DNS",
    "discovery": "Provide service discovery and routing metadata",
    "hystrix-dashboard": "Expose circuit breaker and resilience dashboards",
    "jobs": "Run asynchronous background jobs and scheduled tasks",
    "movie": "Manage movie catalog data and movie APIs",
    "movies-ui": "Serve the movie recommendation user interface",
    "notifications": "Send email, webhook, and user notification messages",
    "orders": "Manage order lifecycle and fulfillment workflows",
    "payments": "Handle payment collection and payment provider integration",
    "recommendation": "Compute movie recommendations from user and movie signals",
    "users": "Manage user profiles and account data",
    "worker": "Process asynchronous work outside the request path",
    "workers": "Process asynchronous work outside the request path",
}

API_FRAMEWORKS = {"fastapi", "django", "flask", "express", "nextjs"}
FRONTEND_FRAMEWORKS = {"react", "nextjs", "flutter", "static-site"}
CONTAINER_FRAMEWORKS = {"spring-boot", "spring-cloud"}
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
        candidates = _fallback_candidates(metadata)

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
        responsibility = (
            "Build and serve the Flutter web application as static assets"
            if metadata.framework == "flutter"
            else "Serve the web frontend and route browser traffic"
        )
        candidates.append(
            ServiceCandidate(
                name="frontend",
                responsibility=responsibility,
                runtime="s3-cloudfront",
            )
        )

    return candidates


def _folder_candidates(metadata: NormalizedRepoMetadata) -> list[ServiceCandidate]:
    top_level_folders = {path.split("/", 1)[0] for path in metadata.folder_paths}
    candidates: list[ServiceCandidate] = []

    for folder in sorted(top_level_folders):
        normalized = folder.lower().replace("_", "-")
        if normalized.endswith("-microservice"):
            normalized = normalized.removesuffix("-microservice")
        responsibility = DOMAIN_FOLDER_HINTS.get(normalized)
        if responsibility is None:
            continue

        runtime = "container" if metadata.framework in CONTAINER_FRAMEWORKS else "lambda"
        candidates.append(
            ServiceCandidate(
                name=_service_name(normalized),
                responsibility=responsibility,
                runtime=runtime,
                data_store=_data_store_for_service(normalized, runtime),
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


def _fallback_candidates(metadata: NormalizedRepoMetadata) -> list[ServiceCandidate]:
    if metadata.framework == "static-site" or metadata.language in {"javascript", "typescript", "dart"}:
        return [
            ServiceCandidate(
                name="frontend",
                responsibility="Serve detected browser application assets",
                runtime="s3-cloudfront",
            )
        ]

    if metadata.framework in CONTAINER_FRAMEWORKS or metadata.language == "java":
        return [
            ServiceCandidate(
                name="application",
                responsibility="Run the Java Spring application as a containerized service",
                runtime="container",
            )
        ]

    return [
        ServiceCandidate(
            name="application",
            responsibility="Run the application with the detected repository entrypoints",
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

    if "api-gateway" in names:
        for target in sorted(names - {"api-gateway", "config", "consul", "discovery"}):
            flows.append(
                CommunicationFlow(
                    source="api-gateway",
                    target=target,
                    style="sync",
                    transport="http",
                )
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


def _data_store_for_service(service_name: str, runtime: str) -> str | None:
    if runtime == "container":
        return {
            "movie": "mongodb",
            "recommendation": "neo4j",
            "users": "mysql",
        }.get(service_name)
    return "dynamodb" if service_name not in ASYNC_SERVICE_NAMES else None
