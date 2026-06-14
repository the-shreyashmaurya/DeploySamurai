from __future__ import annotations

from pathlib import Path

import yaml

from deploy_samurai.schemas.architecture import ArchitectureReasoningResponse, ServiceCandidate
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
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Description": architecture.summary or "DeploySamurai generated SAM scaffold.",
        "Globals": {
            "Function": {
                "Timeout": 30,
                "Runtime": "python3.12",
                "MemorySize": 256,
            }
        },
        "Resources": _template_resources(architecture),
        "Outputs": {
            "ApiUrl": {
                "Description": "HTTP API endpoint URL",
                "Value": {"Fn::Sub": "https://${HttpApi}.execute-api.${AWS::Region}.amazonaws.com"},
            }
        },
    }
    return yaml.safe_dump(template, sort_keys=False)


def _template_resources(architecture: ArchitectureReasoningResponse) -> dict[str, object]:
    resources: dict[str, object] = {
        "HttpApi": {
            "Type": "AWS::Serverless::HttpApi",
            "Properties": {
                "StageName": "prod",
            },
        }
    }

    for service in _lambda_services(architecture.service_candidates):
        logical_id = _function_logical_id(service.name)
        resources[logical_id] = {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                "CodeUri": f"src/{service.name}/",
                "Handler": "app.handler",
                "Description": service.responsibility,
                "Events": {
                    "ApiEvent": {
                        "Type": "HttpApi",
                        "Properties": {
                            "ApiId": {"Ref": "HttpApi"},
                            "Path": f"/{service.name}",
                            "Method": "ANY",
                        },
                    }
                },
            },
        }

    return resources


def _resource_summaries(architecture: ArchitectureReasoningResponse) -> list[SamResourceSummary]:
    summaries = [
        SamResourceSummary(
            logical_id="HttpApi",
            resource_type="AWS::Serverless::HttpApi",
            reason="Expose synchronous service endpoints through API Gateway",
        )
    ]

    for service in _lambda_services(architecture.service_candidates):
        summaries.append(
            SamResourceSummary(
                logical_id=_function_logical_id(service.name),
                resource_type="AWS::Serverless::Function",
                service_name=service.name,
                reason=service.responsibility,
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


def _function_logical_id(service_name: str) -> str:
    return "".join(part.capitalize() for part in service_name.replace("_", "-").split("-")) + "Function"
