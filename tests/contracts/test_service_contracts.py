import pytest
from pydantic import ValidationError

from deploy_samurai.schemas.architecture import (
    ArchitectureReasoningResponse,
    CommunicationFlow,
    ServiceCandidate,
)


def test_architecture_contract_serializes_documented_flow_keys() -> None:
    response = ArchitectureReasoningResponse(
        architecture_type="microservices",
        service_candidates=[
            ServiceCandidate(
                name="api",
                responsibility="Handle synchronous API requests",
                data_store="dynamodb",
            )
        ],
        communication_flows=[
            CommunicationFlow(
                source="api",
                target="worker",
                style="async",
                transport="sqs",
            )
        ],
    )

    dumped = response.model_dump(by_alias=True)

    assert dumped["communication_flows"][0]["from"] == "api"
    assert dumped["communication_flows"][0]["to"] == "worker"


def test_architecture_contract_accepts_documented_flow_keys() -> None:
    response = ArchitectureReasoningResponse.model_validate(
        {
            "architecture_type": "microservices",
            "summary": "Split API and worker boundaries.",
            "service_candidates": [
                {
                    "name": "api",
                    "responsibility": "Handle synchronous API requests",
                    "runtime": "lambda",
                    "data_store": "dynamodb",
                }
            ],
            "communication_flows": [
                {
                    "from": "api",
                    "to": "worker",
                    "style": "async",
                    "transport": "sqs",
                }
            ],
            "notes": ["Review generated boundaries before deployment."],
        }
    )

    assert response.communication_flows[0].source == "api"
    assert response.communication_flows[0].target == "worker"
    assert response.summary == "Split API and worker boundaries."


@pytest.mark.parametrize("architecture_type", ["serverless", "monolith", "micro_service"])
def test_architecture_contract_rejects_unknown_architecture_type(
    architecture_type: str,
) -> None:
    with pytest.raises(ValidationError):
        ArchitectureReasoningResponse(
            architecture_type=architecture_type,
            service_candidates=[
                ServiceCandidate(name="api", responsibility="Handle requests"),
            ],
        )


@pytest.mark.parametrize("style", ["queue", "event", "request"])
def test_architecture_contract_rejects_unknown_flow_style(style: str) -> None:
    with pytest.raises(ValidationError):
        CommunicationFlow(
            source="api",
            target="worker",
            style=style,
            transport="sqs",
        )
