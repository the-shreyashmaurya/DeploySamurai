from pathlib import Path

import yaml

from deploy_samurai.schemas.architecture import (
    ArchitectureReasoningResponse,
    CommunicationFlow,
    ServiceCandidate,
)
from deploy_samurai.schemas.sam_generation import SamGenerationRequest
from deploy_samurai.services.sam_generation.template import generate_sam_template, render_sam_template


def test_render_sam_template_creates_http_api_and_lambda_function() -> None:
    template = render_sam_template(
        ArchitectureReasoningResponse(
            architecture_type="modular_monolith",
            summary="Recommended SAM scaffold.",
            service_candidates=[
                ServiceCandidate(
                    name="api",
                    responsibility="Expose synchronous application APIs",
                    runtime="lambda",
                    data_store="dynamodb",
                )
            ],
        )
    )

    parsed = yaml.safe_load(template)

    assert parsed["Transform"] == "AWS::Serverless-2016-10-31"
    assert parsed["Resources"]["HttpApi"]["Type"] == "AWS::Serverless::HttpApi"
    assert parsed["Resources"]["ApiFunction"]["Type"] == "AWS::Serverless::Function"
    assert parsed["Resources"]["ApiFunction"]["Properties"]["CodeUri"] == "src/api/"
    assert parsed["Outputs"]["ApiUrl"]["Description"] == "HTTP API endpoint URL"


def test_render_sam_template_maps_supported_serverless_resources() -> None:
    template = render_sam_template(
        ArchitectureReasoningResponse(
            architecture_type="microservices",
            service_candidates=[
                ServiceCandidate(
                    name="api",
                    responsibility="Expose synchronous application APIs",
                    runtime="lambda",
                    data_store="dynamodb",
                ),
                ServiceCandidate(
                    name="worker",
                    responsibility="Process asynchronous jobs",
                    runtime="lambda",
                ),
                ServiceCandidate(
                    name="frontend",
                    responsibility="Serve static frontend assets",
                    runtime="s3-cloudfront",
                ),
            ],
            communication_flows=[
                CommunicationFlow(
                    source="api",
                    target="worker",
                    style="async",
                    transport="sqs",
                ),
                CommunicationFlow(
                    source="api",
                    target="worker",
                    style="async",
                    transport="eventbridge",
                ),
            ],
        )
    )

    parsed = yaml.safe_load(template)
    resources = parsed["Resources"]

    assert resources["ApiTable"]["Type"] == "AWS::DynamoDB::Table"
    assert resources["FrontendBucket"]["Type"] == "AWS::S3::Bucket"
    assert resources["WorkerQueue"]["Type"] == "AWS::SQS::Queue"
    assert resources["ApiToWorkerRule"]["Type"] == "AWS::Events::Rule"
    assert resources["WorkerFunction"]["Properties"]["Events"]["ApiToWorkerEvent"]["Type"] == "SQS"
    assert resources["ApiFunction"]["Properties"]["Policies"][0] == {
        "DynamoDBCrudPolicy": {"TableName": {"Ref": "ApiTable"}}
    }


def test_generate_sam_template_writes_template_artifact(tmp_path: Path) -> None:
    response = generate_sam_template(
        SamGenerationRequest(
            job_id="job_123",
            architecture=ArchitectureReasoningResponse(
                architecture_type="microservices",
                service_candidates=[
                    ServiceCandidate(
                        name="api",
                        responsibility="Expose synchronous application APIs",
                    )
                ],
            ),
        ),
        output_root=tmp_path,
    )

    template_path = tmp_path / "job_123" / "template.yaml"
    assert template_path.exists()
    assert response.artifacts.template_path == template_path.as_posix()
    assert response.artifacts.resource_summaries[0].logical_id == "HttpApi"
    assert response.artifacts.resource_summaries[1].logical_id == "ApiFunction"
    handler_path = tmp_path / "job_123" / "src/api/app.py"
    assert response.handlers[0].handler_path == handler_path.as_posix()
    assert handler_path.exists()
    assert '"service": "api"' in handler_path.read_text(encoding="utf-8")
    assert response.files[1].purpose == "lambda_handler"
