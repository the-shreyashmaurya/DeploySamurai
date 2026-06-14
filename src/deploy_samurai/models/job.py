from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from deploy_samurai.db.base import Base


class JobMode(StrEnum):
    ADVISOR = "advisor"
    AUTONOMOUS = "autonomous"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class DeploymentTarget(StrEnum):
    AWS_SAM = "aws-sam"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(40),
        primary_key=True,
        default=lambda: f"job_{uuid4().hex[:12]}",
    )
    repo_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    mode: Mapped[JobMode] = mapped_column(
        Enum(JobMode, name="job_mode", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    target: Mapped[DeploymentTarget] = mapped_column(
        Enum(
            DeploymentTarget,
            name="deployment_target",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=DeploymentTarget.AWS_SAM,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=JobStatus.QUEUED,
    )
    current_step: Mapped[str] = mapped_column(String(80), nullable=False, default="queued")
    progress: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
