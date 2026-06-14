from typing import Literal

from pydantic import BaseModel

from deploy_samurai.schemas.architecture import ArchitectureReasoningResponse


class SamGenerationRequest(BaseModel):
    job_id: str
    architecture: ArchitectureReasoningResponse
    output_format: Literal["sam"] = "sam"


class GeneratedFile(BaseModel):
    path: str
    content_type: str


class SamArtifacts(BaseModel):
    template_path: str


class SamGenerationResponse(BaseModel):
    files: list[GeneratedFile]
    artifacts: SamArtifacts
