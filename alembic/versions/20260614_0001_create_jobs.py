"""create jobs table

Revision ID: 20260614_0001
Revises:
Create Date: 2026-06-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260614_0001"
down_revision = None
branch_labels = None
depends_on = None


job_mode = sa.Enum("advisor", "autonomous", name="job_mode")
job_status = sa.Enum("queued", "running", "succeeded", "failed", name="job_status")
deployment_target = sa.Enum("aws-sam", name="deployment_target")


def upgrade() -> None:
    bind = op.get_bind()
    job_mode.create(bind, checkfirst=True)
    job_status.create(bind, checkfirst=True)
    deployment_target.create(bind, checkfirst=True)

    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("repo_url", sa.String(length=2048), nullable=False),
        sa.Column("mode", job_mode, nullable=False),
        sa.Column("target", deployment_target, nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("current_step", sa.String(length=80), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("jobs")

    bind = op.get_bind()
    deployment_target.drop(bind, checkfirst=True)
    job_status.drop(bind, checkfirst=True)
    job_mode.drop(bind, checkfirst=True)
