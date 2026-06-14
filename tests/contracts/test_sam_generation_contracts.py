from pydantic import ValidationError
import pytest

from deploy_samurai.schemas.sam_generation import (
    GeneratedFile,
    LambdaHandlerArtifact,
    SamArtifacts,
    SamGenerationResponse,
    SamResourceSummary,
)


def test_sam_generation_response_contract_includes_artifact_metadata() -> None:
    response = SamGenerationResponse(
        files=[
            GeneratedFile(
                path="artifacts/job_123/template.yaml",
                content_type="text/yaml",
                purpose="sam_template",
            )
        ],
        artifacts=SamArtifacts(
            template_path="artifacts/job_123/template.yaml",
            handler_paths=["artifacts/job_123/src/api/app.py"],
            resource_summaries=[
                SamResourceSummary(
                    logical_id="ApiFunction",
                    resource_type="AWS::Serverless::Function",
                    service_name="api",
                    reason="Expose synchronous API requests",
                )
            ],
        ),
        handlers=[
            LambdaHandlerArtifact(
                service_name="api",
                handler_path="artifacts/job_123/src/api/app.py",
                function_logical_id="ApiFunction",
            )
        ],
    )

    dumped = response.model_dump()

    assert dumped["artifacts"]["template_path"] == "artifacts/job_123/template.yaml"
    assert dumped["artifacts"]["resource_summaries"][0]["resource_type"] == (
        "AWS::Serverless::Function"
    )
    assert dumped["handlers"][0]["runtime"] == "python3.12"


def test_sam_resource_summary_rejects_unsupported_resource_types() -> None:
    with pytest.raises(ValidationError):
        SamResourceSummary(
            logical_id="ContainerService",
            resource_type="AWS::ECS::Service",
            reason="Not in the SAM MVP scope",
        )
