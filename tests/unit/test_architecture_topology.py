from deploy_samurai.schemas.architecture import CommunicationFlow, ServiceCandidate
from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata
from deploy_samurai.services.architecture_reasoning.topology import decide_architecture_type


def test_decide_architecture_type_prefers_modular_monolith_for_single_service() -> None:
    decision = decide_architecture_type(
        NormalizedRepoMetadata(name="simple", has_tests=True),
        [ServiceCandidate(name="api", responsibility="Serve API requests")],
        [],
    )

    assert decision.architecture_type == "modular_monolith"
    assert "Only one candidate service was detected." in decision.rationale


def test_decide_architecture_type_prefers_modular_monolith_without_tests() -> None:
    decision = decide_architecture_type(
        NormalizedRepoMetadata(name="untested", has_tests=False),
        [
            ServiceCandidate(name="api", responsibility="Serve API requests"),
            ServiceCandidate(name="worker", responsibility="Process jobs"),
        ],
        [
            CommunicationFlow(
                source="api",
                target="worker",
                style="async",
                transport="sqs",
            )
        ],
    )

    assert decision.architecture_type == "modular_monolith"
    assert "tests were not detected" in decision.rationale[0]


def test_decide_architecture_type_selects_microservices_for_async_tested_repo() -> None:
    decision = decide_architecture_type(
        NormalizedRepoMetadata(name="tested-worker-app", has_tests=True),
        [
            ServiceCandidate(name="api", responsibility="Serve API requests"),
            ServiceCandidate(name="worker", responsibility="Process jobs"),
        ],
        [
            CommunicationFlow(
                source="api",
                target="worker",
                style="async",
                transport="sqs",
            )
        ],
    )

    assert decision.architecture_type == "microservices"
    assert "asynchronous flow" in decision.rationale[1]


def test_decide_architecture_type_selects_microservices_for_clear_domains() -> None:
    decision = decide_architecture_type(
        NormalizedRepoMetadata(name="domain-app", has_tests=True),
        [
            ServiceCandidate(name="api", responsibility="Serve API requests"),
            ServiceCandidate(name="auth", responsibility="Handle identity"),
            ServiceCandidate(name="billing", responsibility="Handle billing"),
        ],
        [],
    )

    assert decision.architecture_type == "microservices"
    assert decision.rationale == ["Multiple independently deployable service candidates were detected."]


def test_decide_architecture_type_selects_microservices_for_containerized_services_without_tests() -> None:
    decision = decide_architecture_type(
        NormalizedRepoMetadata(name="spring-cloud-demo", framework="spring-cloud"),
        [
            ServiceCandidate(name="api-gateway", responsibility="Route traffic", runtime="container"),
            ServiceCandidate(name="movie", responsibility="Movie API", runtime="container"),
            ServiceCandidate(name="users", responsibility="User API", runtime="container"),
        ],
        [],
    )

    assert decision.architecture_type == "microservices"
    assert "Multiple containerized service candidates were detected." in decision.rationale


def test_decide_architecture_type_keeps_simple_two_service_repo_modular() -> None:
    decision = decide_architecture_type(
        NormalizedRepoMetadata(name="two-part-app", has_tests=True),
        [
            ServiceCandidate(name="api", responsibility="Serve API requests"),
            ServiceCandidate(name="frontend", responsibility="Serve frontend"),
        ],
        [],
    )

    assert decision.architecture_type == "modular_monolith"
    assert "repository shape is still simple" in decision.rationale[0]
