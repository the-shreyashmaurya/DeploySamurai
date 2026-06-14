from __future__ import annotations

from pathlib import Path

import yaml

from deploy_samurai.schemas.architecture import (
    ArchitectureReasoningResponse,
    CommunicationFlow,
    ServiceCandidate,
)
from deploy_samurai.schemas.sam_generation import (
    GeneratedFile,
    LambdaHandlerArtifact,
    SamArtifacts,
    SamGenerationRequest,
    SamGenerationResponse,
    SamResourceSummary,
)


def generate_sam_template(
    payload: SamGenerationRequest,
    output_root: Path,
) -> SamGenerationResponse:
    artifact_root = output_root / payload.job_id
    template_path = artifact_root / "template.yaml"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_content = render_sam_template(payload.architecture)
    template_path.write_text(template_content, encoding="utf-8")

    resources = _resource_summaries(payload.architecture)
    handlers = _handler_artifacts(payload.architecture, artifact_root)
    _write_handler_scaffolds(handlers)

    return SamGenerationResponse(
        files=[
            GeneratedFile(
                path=template_path.as_posix(),
                content_type="text/yaml",
                purpose="sam_template",
            ),
            *[
                GeneratedFile(
                    path=handler.handler_path,
                    content_type="text/x-python",
                    purpose="lambda_handler",
                )
                for handler in handlers
            ],
        ],
        artifacts=SamArtifacts(
            template_path=template_path.as_posix(),
            handler_paths=[handler.handler_path for handler in handlers],
            resource_summaries=resources,
        ),
        handlers=handlers,
    )


def render_sam_template(architecture: ArchitectureReasoningResponse) -> str:
    lambda_services = _lambda_services(architecture.service_candidates)
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Description": architecture.summary or "DeploySamurai generated SAM scaffold.",
    }
    if lambda_services:
        template["Globals"] = {
            "Function": {
                "Timeout": 30,
                "Runtime": "python3.12",
                "MemorySize": 256,
            }
        }
    if _container_services(architecture.service_candidates):
        template["Parameters"] = _container_parameters()
    template["Resources"] = _template_resources(architecture)
    template["Outputs"] = _template_outputs(architecture)
    return yaml.safe_dump(template, sort_keys=False)


def _template_resources(architecture: ArchitectureReasoningResponse) -> dict[str, object]:
    resources: dict[str, object] = {}

    if _lambda_services(architecture.service_candidates):
        resources["HttpApi"] = {
            "Type": "AWS::Serverless::HttpApi",
            "Properties": {
                "StageName": "prod",
            },
        }

    for service in _lambda_services(architecture.service_candidates):
        logical_id = _function_logical_id(service.name)
        events = {
            "ApiEvent": {
                "Type": "HttpApi",
                "Properties": {
                    "ApiId": {"Ref": "HttpApi"},
                    "Path": f"/{service.name}",
                    "Method": "ANY",
                },
            }
        }
        policies: list[object] = []

        if service.data_store == "dynamodb":
            table_id = _table_logical_id(service.name)
            resources[table_id] = _dynamodb_table(service.name)
            policies.append(
                {
                    "DynamoDBCrudPolicy": {
                        "TableName": {"Ref": table_id},
                    }
                }
            )

        for flow in _targeted_flows(architecture.communication_flows, service.name, "sqs"):
            queue_id = _queue_logical_id(flow.target)
            resources.setdefault(queue_id, _sqs_queue(flow.target))
            events[_event_logical_id(flow.source, flow.target)] = {
                "Type": "SQS",
                "Properties": {
                    "Queue": {"Fn::GetAtt": [queue_id, "Arn"]},
                    "BatchSize": 10,
                },
            }
            policies.append(
                {
                    "SQSPollerPolicy": {
                        "QueueName": {"Fn::GetAtt": [queue_id, "QueueName"]},
                    }
                }
            )

        resources[logical_id] = {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                "CodeUri": f"src/{service.name}/",
                "Handler": "app.handler",
                "Description": service.responsibility,
                "Events": events,
            },
        }
        if policies:
            resources[logical_id]["Properties"]["Policies"] = policies

    for service in architecture.service_candidates:
        if service.runtime == "s3-cloudfront":
            bucket_id = _bucket_logical_id(service.name)
            distribution_id = _distribution_logical_id(service.name)
            resources[bucket_id] = _s3_bucket(service.name)
            resources[distribution_id] = _cloudfront_distribution(service.name, bucket_id)

    container_services = _container_services(architecture.service_candidates)
    if container_services:
        resources["EcsCluster"] = {"Type": "AWS::ECS::Cluster"}
        resources["ContainerTaskExecutionRole"] = _container_task_execution_role()
        for service in container_services:
            repository_id = _repository_logical_id(service.name)
            log_group_id = _log_group_logical_id(service.name)
            task_id = _task_definition_logical_id(service.name)
            service_id = _ecs_service_logical_id(service.name)
            resources[repository_id] = _ecr_repository(service.name)
            resources[log_group_id] = _log_group(service.name)
            resources[task_id] = _task_definition(service, repository_id, log_group_id)
            resources[service_id] = _ecs_service(service, task_id)

    for flow in _transport_flows(architecture.communication_flows, "eventbridge"):
        resources[_eventbridge_rule_logical_id(flow.source, flow.target)] = _eventbridge_rule(flow)

    return resources


def _template_outputs(architecture: ArchitectureReasoningResponse) -> dict[str, object]:
    outputs: dict[str, object] = {}
    if _lambda_services(architecture.service_candidates):
        outputs["ApiUrl"] = {
            "Description": "HTTP API endpoint URL",
            "Value": {"Fn::Sub": "https://${HttpApi}.execute-api.${AWS::Region}.amazonaws.com"},
        }

    for service in architecture.service_candidates:
        if service.runtime == "s3-cloudfront":
            outputs[f"{_pascal_case(service.name)}BucketName"] = {
                "Description": f"S3 bucket for {service.name} static assets",
                "Value": {"Ref": _bucket_logical_id(service.name)},
            }
            outputs[f"{_pascal_case(service.name)}DistributionDomainName"] = {
                "Description": f"CloudFront domain for {service.name}",
                "Value": {"Fn::GetAtt": [_distribution_logical_id(service.name), "DomainName"]},
            }

    if _container_services(architecture.service_candidates):
        outputs["ClusterName"] = {
            "Description": "ECS cluster for containerized services",
            "Value": {"Ref": "EcsCluster"},
        }
        for service in _container_services(architecture.service_candidates):
            outputs[f"{_pascal_case(service.name)}ImageRepository"] = {
                "Description": f"ECR repository URI for {service.name}",
                "Value": {"Fn::GetAtt": [_repository_logical_id(service.name), "RepositoryUri"]},
            }

    return outputs


def _resource_summaries(architecture: ArchitectureReasoningResponse) -> list[SamResourceSummary]:
    summaries = []
    if _lambda_services(architecture.service_candidates):
        summaries.append(
            SamResourceSummary(
                logical_id="HttpApi",
                resource_type="AWS::Serverless::HttpApi",
                reason="Expose synchronous service endpoints through API Gateway",
            )
        )

    for service in _lambda_services(architecture.service_candidates):
        summaries.append(
            SamResourceSummary(
                logical_id=_function_logical_id(service.name),
                resource_type="AWS::Serverless::Function",
                service_name=service.name,
                reason=service.responsibility,
            )
        )
        if service.data_store == "dynamodb":
            summaries.append(
                SamResourceSummary(
                    logical_id=_table_logical_id(service.name),
                    resource_type="AWS::DynamoDB::Table",
                    service_name=service.name,
                    reason=f"Persist {service.name} service state",
                )
            )

    for service in architecture.service_candidates:
        if service.runtime == "s3-cloudfront":
            bucket_id = _bucket_logical_id(service.name)
            summaries.append(
                SamResourceSummary(
                    logical_id=bucket_id,
                    resource_type="AWS::S3::Bucket",
                    service_name=service.name,
                    reason=f"Store static assets for {service.name}",
                )
            )
            summaries.append(
                SamResourceSummary(
                    logical_id=_distribution_logical_id(service.name),
                    resource_type="AWS::CloudFront::Distribution",
                    service_name=service.name,
                    reason=f"Serve {service.name} assets globally over HTTPS",
                )
            )

    container_services = _container_services(architecture.service_candidates)
    if container_services:
        summaries.append(
            SamResourceSummary(
                logical_id="EcsCluster",
                resource_type="AWS::ECS::Cluster",
                reason="Run Spring Cloud services as containerized workloads",
            )
        )
        summaries.append(
            SamResourceSummary(
                logical_id="ContainerTaskExecutionRole",
                resource_type="AWS::IAM::Role",
                reason="Allow ECS tasks to pull images and write logs",
            )
        )
        for service in container_services:
            summaries.extend(
                [
                    SamResourceSummary(
                        logical_id=_repository_logical_id(service.name),
                        resource_type="AWS::ECR::Repository",
                        service_name=service.name,
                        reason=f"Store container images for {service.name}",
                    ),
                    SamResourceSummary(
                        logical_id=_task_definition_logical_id(service.name),
                        resource_type="AWS::ECS::TaskDefinition",
                        service_name=service.name,
                        reason=service.responsibility,
                    ),
                    SamResourceSummary(
                        logical_id=_ecs_service_logical_id(service.name),
                        resource_type="AWS::ECS::Service",
                        service_name=service.name,
                        reason=f"Run one desired task for {service.name} on Fargate",
                    ),
                    SamResourceSummary(
                        logical_id=_log_group_logical_id(service.name),
                        resource_type="AWS::Logs::LogGroup",
                        service_name=service.name,
                        reason=f"Capture container logs for {service.name}",
                    ),
                ]
            )
    for flow in _transport_flows(architecture.communication_flows, "sqs"):
        summaries.append(
            SamResourceSummary(
                logical_id=_queue_logical_id(flow.target),
                resource_type="AWS::SQS::Queue",
                service_name=flow.target,
                reason=f"Buffer async messages from {flow.source} to {flow.target}",
            )
        )

    for flow in _transport_flows(architecture.communication_flows, "eventbridge"):
        summaries.append(
            SamResourceSummary(
                logical_id=_eventbridge_rule_logical_id(flow.source, flow.target),
                resource_type="AWS::Events::Rule",
                service_name=flow.target,
                reason=f"Route events from {flow.source} to {flow.target}",
            )
        )

    return summaries


def _handler_artifacts(
    architecture: ArchitectureReasoningResponse,
    artifact_root: Path,
) -> list[LambdaHandlerArtifact]:
    return [
        LambdaHandlerArtifact(
            service_name=service.name,
            handler_path=(artifact_root / "src" / service.name / "app.py").as_posix(),
            function_logical_id=_function_logical_id(service.name),
        )
        for service in _lambda_services(architecture.service_candidates)
    ]


def _write_handler_scaffolds(handlers: list[LambdaHandlerArtifact]) -> None:
    for handler in handlers:
        handler_path = Path(handler.handler_path)
        handler_path.parent.mkdir(parents=True, exist_ok=True)
        handler_path.write_text(_handler_source(handler.service_name), encoding="utf-8")


def _handler_source(service_name: str) -> str:
    return f'''from __future__ import annotations

import json


def handler(event, context):
    body = {{
        "service": "{service_name}",
        "message": "Generated by DeploySamurai. Replace with application logic.",
    }}
    return {{
        "statusCode": 200,
        "headers": {{"content-type": "application/json"}},
        "body": json.dumps(body),
    }}
'''


def _lambda_services(candidates: list[ServiceCandidate]) -> list[ServiceCandidate]:
    return [service for service in candidates if service.runtime == "lambda"]


def _container_services(candidates: list[ServiceCandidate]) -> list[ServiceCandidate]:
    return [service for service in candidates if service.runtime == "container"]


def _function_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}Function"


def _table_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}Table"


def _bucket_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}Bucket"


def _distribution_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}Distribution"


def _repository_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}Repository"


def _task_definition_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}TaskDefinition"


def _ecs_service_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}Service"


def _log_group_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}LogGroup"


def _queue_logical_id(service_name: str) -> str:
    return f"{_pascal_case(service_name)}Queue"


def _event_logical_id(source: str, target: str) -> str:
    return f"{_pascal_case(source)}To{_pascal_case(target)}Event"


def _eventbridge_rule_logical_id(source: str, target: str) -> str:
    return f"{_pascal_case(source)}To{_pascal_case(target)}Rule"


def _pascal_case(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("_", "-").split("-"))


def _dynamodb_table(service_name: str) -> dict[str, object]:
    return {
        "Type": "AWS::DynamoDB::Table",
        "Properties": {
            "BillingMode": "PAY_PER_REQUEST",
            "AttributeDefinitions": [
                {"AttributeName": "pk", "AttributeType": "S"},
            ],
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
            ],
            "TableName": {"Fn::Sub": f"${{AWS::StackName}}-{service_name}"},
        },
    }


def _s3_bucket(service_name: str) -> dict[str, object]:
    return {
        "Type": "AWS::S3::Bucket",
        "Properties": {
            "BucketName": {"Fn::Sub": f"${{AWS::StackName}}-{service_name}-assets"},
            "VersioningConfiguration": {"Status": "Enabled"},
        },
    }


def _cloudfront_distribution(service_name: str, bucket_logical_id: str) -> dict[str, object]:
    origin_id = f"{_pascal_case(service_name)}S3Origin"
    return {
        "Type": "AWS::CloudFront::Distribution",
        "Properties": {
            "DistributionConfig": {
                "Enabled": True,
                "DefaultRootObject": "index.html",
                "Origins": [
                    {
                        "Id": origin_id,
                        "DomainName": {"Fn::GetAtt": [bucket_logical_id, "RegionalDomainName"]},
                        "S3OriginConfig": {},
                    }
                ],
                "DefaultCacheBehavior": {
                    "TargetOriginId": origin_id,
                    "ViewerProtocolPolicy": "redirect-to-https",
                    "AllowedMethods": ["GET", "HEAD", "OPTIONS"],
                    "CachedMethods": ["GET", "HEAD"],
                    "ForwardedValues": {"QueryString": False},
                },
            }
        },
    }


def _container_parameters() -> dict[str, object]:
    return {
        "VpcId": {
            "Type": "AWS::EC2::VPC::Id",
            "Description": "VPC where ECS Fargate services will run",
        },
        "SubnetIds": {
            "Type": "List<AWS::EC2::Subnet::Id>",
            "Description": "Subnets for ECS Fargate tasks",
        },
    }


def _container_task_execution_role() -> dict[str, object]:
    return {
        "Type": "AWS::IAM::Role",
        "Properties": {
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            },
            "ManagedPolicyArns": [
                "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
            ],
        },
    }


def _ecr_repository(service_name: str) -> dict[str, object]:
    return {
        "Type": "AWS::ECR::Repository",
        "Properties": {
            "RepositoryName": {"Fn::Sub": f"${{AWS::StackName}}/{service_name}"},
            "ImageScanningConfiguration": {"ScanOnPush": True},
        },
    }


def _log_group(service_name: str) -> dict[str, object]:
    return {
        "Type": "AWS::Logs::LogGroup",
        "Properties": {
            "LogGroupName": {"Fn::Sub": f"/ecs/${{AWS::StackName}}/{service_name}"},
            "RetentionInDays": 14,
        },
    }


def _task_definition(
    service: ServiceCandidate,
    repository_logical_id: str,
    log_group_logical_id: str,
) -> dict[str, object]:
    return {
        "Type": "AWS::ECS::TaskDefinition",
        "Properties": {
            "RequiresCompatibilities": ["FARGATE"],
            "NetworkMode": "awsvpc",
            "Cpu": "512",
            "Memory": "1024",
            "ExecutionRoleArn": {"Fn::GetAtt": ["ContainerTaskExecutionRole", "Arn"]},
            "ContainerDefinitions": [
                {
                    "Name": service.name,
                    "Image": {
                        "Fn::Sub": [
                            "${RepositoryUri}:latest",
                            {
                                "RepositoryUri": {
                                    "Fn::GetAtt": [repository_logical_id, "RepositoryUri"]
                                }
                            },
                        ]
                    },
                    "Essential": True,
                    "PortMappings": [{"ContainerPort": 8080, "Protocol": "tcp"}],
                    "Environment": _container_environment(service),
                    "LogConfiguration": {
                        "LogDriver": "awslogs",
                        "Options": {
                            "awslogs-group": {"Ref": log_group_logical_id},
                            "awslogs-region": {"Ref": "AWS::Region"},
                            "awslogs-stream-prefix": service.name,
                        },
                    },
                }
            ],
        },
    }


def _ecs_service(service: ServiceCandidate, task_definition_logical_id: str) -> dict[str, object]:
    return {
        "Type": "AWS::ECS::Service",
        "Properties": {
            "Cluster": {"Ref": "EcsCluster"},
            "DesiredCount": 1,
            "LaunchType": "FARGATE",
            "TaskDefinition": {"Ref": task_definition_logical_id},
            "NetworkConfiguration": {
                "AwsvpcConfiguration": {
                    "AssignPublicIp": "ENABLED",
                    "Subnets": {"Ref": "SubnetIds"},
                }
            },
        },
    }


def _container_environment(service: ServiceCandidate) -> list[dict[str, str]]:
    values = [{"Name": "SPRING_PROFILES_ACTIVE", "Value": "aws"}]
    if service.data_store:
        values.append({"Name": "DEPLOYSAMURAI_DATA_STORE_HINT", "Value": service.data_store})
    return values


def _sqs_queue(service_name: str) -> dict[str, object]:
    return {
        "Type": "AWS::SQS::Queue",
        "Properties": {
            "QueueName": {"Fn::Sub": f"${{AWS::StackName}}-{service_name}"},
            "VisibilityTimeout": 60,
        },
    }


def _eventbridge_rule(flow: CommunicationFlow) -> dict[str, object]:
    return {
        "Type": "AWS::Events::Rule",
        "Properties": {
            "EventPattern": {
                "source": [f"deploy-samurai.{flow.source}"],
                "detail-type": [f"{flow.source}.{flow.target}"],
            },
            "State": "ENABLED",
        },
    }


def _targeted_flows(
    flows: list[CommunicationFlow],
    target: str,
    transport: str,
) -> list[CommunicationFlow]:
    return [flow for flow in flows if flow.target == target and flow.transport == transport]


def _transport_flows(
    flows: list[CommunicationFlow],
    transport: str,
) -> list[CommunicationFlow]:
    return [flow for flow in flows if flow.transport == transport]
