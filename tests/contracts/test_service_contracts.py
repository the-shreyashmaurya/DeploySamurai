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
