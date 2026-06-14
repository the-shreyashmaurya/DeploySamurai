from typing import Literal

from pydantic import BaseModel, Field

from deploy_samurai.schemas.architecture import ArchitectureReasoningResponse

SamResourceType = Literal[
    "AWS::Serverless::Function",
    "AWS::Serverless::HttpApi",
    "AWS::DynamoDB::Table",
    "AWS::S3::Bucket",
    "AWS::CloudFront::Distribution",
    "AWS::SQS::Queue",
    "AWS::Events::Rule",
    "AWS::ECS::Cluster",
    "AWS::ECS::TaskDefinition",
    "AWS::ECS::Service",
    "AWS::ECR::Repository",
    "AWS::Logs::LogGroup",
    "AWS::IAM::Role",
]


class SamGenerationRequest(BaseModel):
    job_id: str
    architecture: ArchitectureReasoningResponse
    output_format: Literal["sam"] = "sam"


class GeneratedFile(BaseModel):
    path: str
    content_type: str
    purpose: str = "artifact"


class SamResourceSummary(BaseModel):
    logical_id: str
    resource_type: SamResourceType
    service_name: str | None = None
    reason: str


class LambdaHandlerArtifact(BaseModel):
    service_name: str
    handler_path: str
    runtime: str = "python3.12"
    function_logical_id: str


class SamArtifacts(BaseModel):
    template_path: str
    handler_paths: list[str] = Field(default_factory=list)
    resource_summaries: list[SamResourceSummary] = Field(default_factory=list)


class SamGenerationResponse(BaseModel):
    files: list[GeneratedFile]
    artifacts: SamArtifacts
    handlers: list[LambdaHandlerArtifact] = Field(default_factory=list)
