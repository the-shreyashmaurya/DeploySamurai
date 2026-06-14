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


def test_render_sam_template_creates_static_site_resources_without_lambda() -> None:
    template = render_sam_template(
        ArchitectureReasoningResponse(
            architecture_type="modular_monolith",
            summary="Recommended static frontend hosting.",
            service_candidates=[
                ServiceCandidate(
                    name="frontend",
                    responsibility="Build and serve the Flutter web application as static assets",
                    runtime="s3-cloudfront",
                )
            ],
        )
    )

    parsed = yaml.safe_load(template)
    resources = parsed["Resources"]

    assert "Globals" not in parsed
    assert "HttpApi" not in resources
    assert "FrontendFunction" not in resources
    assert resources["FrontendBucket"]["Type"] == "AWS::S3::Bucket"
    assert resources["FrontendDistribution"]["Type"] == "AWS::CloudFront::Distribution"
    assert parsed["Outputs"]["FrontendDistributionDomainName"]["Description"] == (
        "CloudFront domain for frontend"
    )


def test_render_sam_template_creates_ecs_resources_for_container_services() -> None:
    template = render_sam_template(
        ArchitectureReasoningResponse(
            architecture_type="microservices",
            summary="Recommended Spring Cloud container deployment.",
            service_candidates=[
                ServiceCandidate(
                    name="api-gateway",
                    responsibility="Route external traffic to internal services",
                    runtime="container",
                ),
                ServiceCandidate(
                    name="movie",
                    responsibility="Manage movie catalog data and movie APIs",
                    runtime="container",
                    data_store="mongodb",
                ),
            ],
            communication_flows=[
                CommunicationFlow(
                    source="api-gateway",
                    target="movie",
                    style="sync",
                    transport="http",
                )
            ],
        )
    )

    parsed = yaml.safe_load(template)
    resources = parsed["Resources"]

    assert "Globals" not in parsed
    assert parsed["Parameters"]["VpcId"]["Type"] == "AWS::EC2::VPC::Id"
    assert resources["EcsCluster"]["Type"] == "AWS::ECS::Cluster"
    assert resources["ApiGatewayRepository"]["Type"] == "AWS::ECR::Repository"
    assert resources["ApiGatewayTaskDefinition"]["Type"] == "AWS::ECS::TaskDefinition"
    assert resources["ApiGatewayService"]["Type"] == "AWS::ECS::Service"
    assert resources["MovieTaskDefinition"]["Properties"]["ContainerDefinitions"][0]["Environment"] == [
        {"Name": "SPRING_PROFILES_ACTIVE", "Value": "aws"},
        {"Name": "DEPLOYSAMURAI_DATA_STORE_HINT", "Value": "mongodb"},
    ]
    assert parsed["Outputs"]["ApiGatewayImageRepository"]["Description"] == (
        "ECR repository URI for api-gateway"
    )


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


def test_generate_sam_template_renders_complete_iac_recommendation(tmp_path: Path) -> None:
    response = generate_sam_template(
        SamGenerationRequest(
            job_id="job_456",
            architecture=ArchitectureReasoningResponse(
                architecture_type="microservices",
                summary="Recommended infrastructure for an API and worker split.",
                service_candidates=[
                    ServiceCandidate(
                        name="api",
                        responsibility="Expose synchronous application APIs",
                        data_store="dynamodb",
                    ),
                    ServiceCandidate(
                        name="worker",
                        responsibility="Process async jobs",
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
                    )
                ],
            ),
        ),
        output_root=tmp_path,
    )

    template = yaml.safe_load(Path(response.artifacts.template_path).read_text(encoding="utf-8"))
    resource_types = {
        summary.logical_id: summary.resource_type
        for summary in response.artifacts.resource_summaries
    }

    assert template["Description"] == "Recommended infrastructure for an API and worker split."
    assert resource_types == {
        "HttpApi": "AWS::Serverless::HttpApi",
        "ApiFunction": "AWS::Serverless::Function",
        "ApiTable": "AWS::DynamoDB::Table",
        "WorkerFunction": "AWS::Serverless::Function",
        "FrontendBucket": "AWS::S3::Bucket",
        "FrontendDistribution": "AWS::CloudFront::Distribution",
        "WorkerQueue": "AWS::SQS::Queue",
    }
    assert {file.purpose for file in response.files} == {"sam_template", "lambda_handler"}
    assert len(response.handlers) == 2
    assert all(Path(handler.handler_path).exists() for handler in response.handlers)
