from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from deploy_samurai.core.config import settings
from deploy_samurai.schemas.sam_generation import SamGenerationRequest, SamGenerationResponse
from deploy_samurai.services.sam_generation.template import generate_sam_template

router = APIRouter()


@router.post("/generate", response_model=SamGenerationResponse)
def generate_sam_artifacts(payload: SamGenerationRequest) -> SamGenerationResponse:
    return generate_sam_template(payload, output_root=settings.artifact_root)


@router.get("/artifacts/{job_id}/template.yaml")
def download_sam_template(job_id: str) -> FileResponse:
    template_path = (settings.artifact_root / job_id / "template.yaml").resolve()
    artifact_root = settings.artifact_root.resolve()

    if artifact_root not in template_path.parents or not template_path.exists():
        raise HTTPException(status_code=404, detail="SAM template artifact was not found.")

    return FileResponse(
        template_path,
        media_type="text/yaml",
        filename=f"{job_id}-template.yaml",
    )
