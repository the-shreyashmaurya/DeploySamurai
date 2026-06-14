from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from deploy_samurai.schemas.repo_analysis import RepoStructure, RepoSummary


class ArchitectureReasoningRequest(BaseModel):
    job_id: str
    repo_summary: RepoSummary
    structure: RepoStructure


class ServiceCandidate(BaseModel):
    name: str
    responsibility: str
    runtime: str = "lambda"
    data_store: str | None = None


class CommunicationFlow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: str = Field(validation_alias="from", serialization_alias="from")
    target: str = Field(validation_alias="to", serialization_alias="to")
    style: Literal["sync", "async"]
    transport: str


class ArchitectureReasoningResponse(BaseModel):
    architecture_type: Literal["modular_monolith", "microservices"]
    service_candidates: list[ServiceCandidate]
    communication_flows: list[CommunicationFlow] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
